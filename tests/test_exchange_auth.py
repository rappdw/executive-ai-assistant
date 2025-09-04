"""
Tests for Exchange authentication functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import os

from eaia.exchange import (
    get_exchange_credentials,
    refresh_exchange_token,
    validate_exchange_scopes,
    get_exchange_auth_from_env,
    ExchangeCredentials,
    _get_token_cache,
    _save_token_cache,
    _EXCHANGE_SCOPES
)


class TestExchangeCredentials:
    """Test ExchangeCredentials class."""
    
    def test_credentials_creation(self):
        """Test creating ExchangeCredentials object."""
        creds = ExchangeCredentials(
            access_token="test_token",
            expires_in=3600,
            refresh_token="refresh_token"
        )
        
        assert creds.token == "test_token"
        assert creds.expires_in == 3600
        assert creds.refresh_token == "refresh_token"
        assert creds.scopes == _EXCHANGE_SCOPES
    
    def test_credentials_to_dict(self):
        """Test converting credentials to dictionary."""
        creds = ExchangeCredentials(
            access_token="test_token",
            expires_in=3600,
            refresh_token="refresh_token"
        )
        
        result = creds.to_dict()
        expected = {
            "access_token": "test_token",
            "expires_in": 3600,
            "refresh_token": "refresh_token",
            "scopes": _EXCHANGE_SCOPES
        }
        
        assert result == expected


class TestTokenCache:
    """Test token cache functionality."""
    
    @patch('eaia.exchange._TOKEN_CACHE_FILE')
    def test_get_token_cache_no_file(self, mock_cache_file):
        """Test getting token cache when file doesn't exist."""
        mock_cache_file.exists.return_value = False
        
        cache = _get_token_cache()
        
        assert cache is not None
        # Should be empty cache
        assert not cache.has_state_changed
    
    @patch('eaia.exchange._TOKEN_CACHE_FILE')
    @patch('builtins.open')
    def test_get_token_cache_with_file(self, mock_open, mock_cache_file):
        """Test getting token cache when file exists."""
        mock_cache_file.exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
        
        with patch('msal.SerializableTokenCache') as mock_cache_class:
            mock_cache = Mock()
            mock_cache_class.return_value = mock_cache
            
            cache = _get_token_cache()
            
            mock_cache.deserialize.assert_called_once_with('{"test": "data"}')
    
    @patch('eaia.exchange._TOKEN_CACHE_FILE')
    @patch('builtins.open')
    def test_save_token_cache(self, mock_open, mock_cache_file):
        """Test saving token cache."""
        mock_cache_file.parent.mkdir = Mock()
        
        mock_cache = Mock()
        mock_cache.has_state_changed = True
        mock_cache.serialize.return_value = '{"test": "data"}'
        
        _save_token_cache(mock_cache)
        
        mock_cache_file.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_open.assert_called_once_with(mock_cache_file, 'w')


class TestScopeValidation:
    """Test scope validation functionality."""
    
    def test_validate_exchange_scopes_valid(self):
        """Test validating scopes that are all included."""
        required_scopes = [
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/User.Read"
        ]
        
        result = validate_exchange_scopes(required_scopes)
        assert result is True
    
    def test_validate_exchange_scopes_invalid(self):
        """Test validating scopes with missing scope."""
        required_scopes = [
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/InvalidScope"
        ]
        
        result = validate_exchange_scopes(required_scopes)
        assert result is False
    
    def test_validate_exchange_scopes_empty(self):
        """Test validating empty scope list."""
        result = validate_exchange_scopes([])
        assert result is True


class TestEnvironmentAuth:
    """Test environment variable authentication."""
    
    def test_get_exchange_auth_from_env_success(self):
        """Test getting auth from environment variables successfully."""
        with patch.dict(os.environ, {
            'EXCHANGE_TENANT_ID': 'test_tenant',
            'EXCHANGE_CLIENT_ID': 'test_client',
            'EXCHANGE_CLIENT_SECRET': 'test_secret'
        }):
            tenant_id, client_id, client_secret = get_exchange_auth_from_env("test@example.com")
            
            assert tenant_id == 'test_tenant'
            assert client_id == 'test_client'
            assert client_secret == 'test_secret'
    
    def test_get_exchange_auth_from_env_missing_vars(self):
        """Test getting auth from environment with missing variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_exchange_auth_from_env("test@example.com")
            
            assert "Missing required environment variables" in str(exc_info.value)
            assert "EXCHANGE_TENANT_ID" in str(exc_info.value)


class TestExchangeAuthentication:
    """Test Exchange authentication functions."""
    
    @pytest.mark.asyncio
    async def test_get_exchange_credentials_missing_params(self):
        """Test authentication with missing parameters."""
        with pytest.raises(ValueError) as exc_info:
            await get_exchange_credentials("", "tenant", "client", "secret")
        
        assert "All authentication parameters" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('eaia.exchange._get_token_cache')
    @patch('eaia.exchange._save_token_cache')
    @patch('msal.ConfidentialClientApplication')
    async def test_get_exchange_credentials_cached_token(self, mock_app_class, mock_save_cache, mock_get_cache):
        """Test authentication with cached token."""
        # Setup mocks
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache
        
        mock_app = Mock()
        mock_app_class.return_value = mock_app
        
        # Mock cached account
        mock_account = {"username": "test@example.com"}
        mock_app.get_accounts.return_value = [mock_account]
        
        # Mock successful silent token acquisition
        mock_result = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token"
        }
        mock_app.acquire_token_silent.return_value = mock_result
        
        # Test
        result = await get_exchange_credentials(
            "test@example.com", "tenant_id", "client_id", "client_secret"
        )
        
        # Verify
        assert isinstance(result, ExchangeCredentials)
        assert result.token == "test_access_token"
        assert result.expires_in == 3600
        assert result.refresh_token == "test_refresh_token"
        
        mock_app.acquire_token_silent.assert_called_once()
        mock_save_cache.assert_called_once_with(mock_cache)
    
    @pytest.mark.asyncio
    @patch('eaia.exchange._get_token_cache')
    @patch('eaia.exchange._save_token_cache')
    @patch('msal.ConfidentialClientApplication')
    async def test_refresh_exchange_token_success(self, mock_app_class, mock_save_cache, mock_get_cache):
        """Test successful token refresh."""
        # Setup mocks
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache
        
        mock_app = Mock()
        mock_app_class.return_value = mock_app
        
        # Mock cached account
        mock_account = {"username": "test@example.com"}
        mock_app.get_accounts.return_value = [mock_account]
        
        # Mock successful token refresh
        mock_result = {
            "access_token": "new_access_token",
            "expires_in": 3600,
            "refresh_token": "new_refresh_token"
        }
        mock_app.acquire_token_silent.return_value = mock_result
        
        # Test
        result = await refresh_exchange_token(
            "test@example.com", "tenant_id", "client_id", "client_secret"
        )
        
        # Verify
        assert isinstance(result, ExchangeCredentials)
        assert result.token == "new_access_token"
        assert result.expires_in == 3600
        assert result.refresh_token == "new_refresh_token"
        
        mock_save_cache.assert_called_once_with(mock_cache)
    
    @pytest.mark.asyncio
    @patch('eaia.exchange._get_token_cache')
    @patch('msal.ConfidentialClientApplication')
    async def test_refresh_exchange_token_no_accounts(self, mock_app_class, mock_get_cache):
        """Test token refresh with no cached accounts."""
        # Setup mocks
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache
        
        mock_app = Mock()
        mock_app_class.return_value = mock_app
        mock_app.get_accounts.return_value = []  # No cached accounts
        
        # Test
        result = await refresh_exchange_token(
            "test@example.com", "tenant_id", "client_id", "client_secret"
        )
        
        # Verify
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
