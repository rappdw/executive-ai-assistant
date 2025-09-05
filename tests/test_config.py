#!/usr/bin/env python3
"""
Unit tests for configuration system with email provider support.

This module tests the configuration loading, validation, and provider selection
functionality including backward compatibility and environment variable substitution.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, mock_open
from pathlib import Path

from eaia.main.config import (
    get_config,
    get_email_provider_config,
    validate_email_provider_config,
    _substitute_env_vars,
    _load_provider_config
)
from eaia.schemas import (
    EmailProviderConfig,
    EmailProviderType,
    ExchangeConfig,
    GmailConfig
)


class TestEnvironmentVariableSubstitution:
    """Test environment variable substitution functionality."""

    def test_substitute_simple_env_var(self):
        """Test substitution of simple environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            config = {"key": "${TEST_VAR}"}
            result = _substitute_env_vars(config)
            assert result["key"] == "test_value"

    def test_substitute_nested_env_vars(self):
        """Test substitution in nested dictionary."""
        with patch.dict(os.environ, {"TENANT_ID": "tenant123", "CLIENT_ID": "client456"}):
            config = {
                "exchange_config": {
                    "tenant_id": "${TENANT_ID}",
                    "client_id": "${CLIENT_ID}",
                    "client_secret": "hardcoded_secret"
                }
            }
            result = _substitute_env_vars(config)
            assert result["exchange_config"]["tenant_id"] == "tenant123"
            assert result["exchange_config"]["client_id"] == "client456"
            assert result["exchange_config"]["client_secret"] == "hardcoded_secret"

    def test_substitute_missing_env_var(self):
        """Test behavior when environment variable is missing."""
        config = {"key": "${MISSING_VAR}"}
        result = _substitute_env_vars(config)
        assert result["key"] == "${MISSING_VAR}"  # Should return original

    def test_substitute_non_env_var_strings(self):
        """Test that non-env-var strings are left unchanged."""
        config = {"key": "normal_string", "key2": "string_with_${partial"}
        result = _substitute_env_vars(config)
        assert result["key"] == "normal_string"
        assert result["key2"] == "string_with_${partial"


class TestProviderConfigLoading:
    """Test email provider configuration loading."""

    def test_load_gmail_provider_config(self):
        """Test loading Gmail provider configuration."""
        config_data = {
            "email_provider": "gmail",
            "gmail_config": {
                "gmail_secret": "test_secret",
                "gmail_token": "test_token"
            }
        }
        
        provider_config = _load_provider_config(config_data)
        
        assert provider_config is not None
        assert provider_config.provider == EmailProviderType.GMAIL
        assert provider_config.gmail_config is not None
        assert provider_config.gmail_config.gmail_secret == "test_secret"
        assert provider_config.gmail_config.gmail_token == "test_token"
        assert provider_config.exchange_config is None

    def test_load_exchange_provider_config(self):
        """Test loading Exchange provider configuration."""
        config_data = {
            "email_provider": "exchange",
            "exchange_config": {
                "tenant_id": "tenant123",
                "client_id": "client456",
                "client_secret": "secret789"
            }
        }
        
        provider_config = _load_provider_config(config_data)
        
        assert provider_config is not None
        assert provider_config.provider == EmailProviderType.EXCHANGE
        assert provider_config.exchange_config is not None
        assert provider_config.exchange_config.tenant_id == "tenant123"
        assert provider_config.exchange_config.client_id == "client456"
        assert provider_config.exchange_config.client_secret == "secret789"
        assert provider_config.gmail_config is None

    def test_load_default_provider_config(self):
        """Test loading default provider configuration (Gmail)."""
        config_data = {}  # No provider specified
        
        provider_config = _load_provider_config(config_data)
        
        assert provider_config is not None
        assert provider_config.provider == EmailProviderType.GMAIL
        assert provider_config.gmail_config is None  # No explicit config
        assert provider_config.exchange_config is None

    def test_load_provider_config_with_empty_values(self):
        """Test loading provider config with empty/None values."""
        config_data = {
            "email_provider": "gmail",
            "gmail_config": {
                "gmail_secret": "",
                "gmail_token": None
            }
        }
        
        provider_config = _load_provider_config(config_data)
        
        assert provider_config is not None
        assert provider_config.provider == EmailProviderType.GMAIL
        assert provider_config.gmail_config is None  # Should be None due to empty values

    def test_load_provider_config_invalid_provider(self):
        """Test loading provider config with invalid provider type."""
        config_data = {
            "email_provider": "invalid_provider"
        }
        
        provider_config = _load_provider_config(config_data)
        
        assert provider_config is None  # Should return None for invalid provider


class TestConfigValidation:
    """Test configuration validation functionality."""

    def test_validate_gmail_provider_config(self):
        """Test validation of Gmail provider configuration."""
        provider_config = EmailProviderConfig(
            provider=EmailProviderType.GMAIL,
            gmail_config=GmailConfig(gmail_secret="secret", gmail_token="token")
        )
        
        assert validate_email_provider_config(provider_config) is True

    def test_validate_gmail_provider_config_no_explicit_config(self):
        """Test validation of Gmail provider without explicit config (backward compatibility)."""
        provider_config = EmailProviderConfig(
            provider=EmailProviderType.GMAIL,
            gmail_config=None
        )
        
        assert validate_email_provider_config(provider_config) is True

    def test_validate_exchange_provider_config(self):
        """Test validation of Exchange provider configuration."""
        provider_config = EmailProviderConfig(
            provider=EmailProviderType.EXCHANGE,
            exchange_config=ExchangeConfig(
                tenant_id="tenant123",
                client_id="client456", 
                client_secret="secret789"
            )
        )
        
        assert validate_email_provider_config(provider_config) is True

    def test_validate_exchange_provider_config_missing_config(self):
        """Test validation of Exchange provider without required config."""
        # This should raise a ValidationError during creation due to Pydantic validation
        with pytest.raises(ValueError, match="Exchange configuration is required"):
            EmailProviderConfig(
                provider=EmailProviderType.EXCHANGE,
                exchange_config=None
            )


class TestGetConfig:
    """Test main configuration loading functionality."""

    def test_get_config_from_configurable(self):
        """Test loading configuration from configurable parameter."""
        config_input = {
            "configurable": {
                "email": "test@example.com",
                "email_provider": "gmail",
                "gmail_config": {
                    "gmail_secret": "test_secret",
                    "gmail_token": "test_token"
                }
            }
        }
        
        result = get_config(config_input)
        
        assert "email" in result
        assert result["email"] == "test@example.com"
        assert "email_provider_config" in result
        assert result["email_provider_config"].provider == EmailProviderType.GMAIL

    @patch("builtins.open", new_callable=mock_open, read_data="""
email: test@example.com
email_provider: exchange
exchange_config:
  tenant_id: ${EXCHANGE_TENANT_ID}
  client_id: ${EXCHANGE_CLIENT_ID}
  client_secret: ${EXCHANGE_CLIENT_SECRET}
""")
    def test_get_config_from_yaml_with_env_vars(self, mock_file):
        """Test loading configuration from YAML with environment variables."""
        with patch.dict(os.environ, {
            "EXCHANGE_TENANT_ID": "tenant123",
            "EXCHANGE_CLIENT_ID": "client456",
            "EXCHANGE_CLIENT_SECRET": "secret789"
        }):
            config_input = {"configurable": {}}  # No email in configurable
            
            result = get_config(config_input)
            
            assert result["email"] == "test@example.com"
            assert "email_provider_config" in result
            provider_config = result["email_provider_config"]
            assert provider_config.provider == EmailProviderType.EXCHANGE
            assert provider_config.exchange_config.tenant_id == "tenant123"
            assert provider_config.exchange_config.client_id == "client456"
            assert provider_config.exchange_config.client_secret == "secret789"

    @patch("builtins.open", new_callable=mock_open, read_data="""
email: test@example.com
# No email_provider specified - should default to gmail
""")
    def test_get_config_backward_compatibility(self, mock_file):
        """Test backward compatibility with existing configurations."""
        config_input = {"configurable": {}}  # No email in configurable
        
        result = get_config(config_input)
        
        assert result["email"] == "test@example.com"
        assert "email_provider_config" in result
        provider_config = result["email_provider_config"]
        assert provider_config.provider == EmailProviderType.GMAIL


class TestGetEmailProviderConfig:
    """Test email provider configuration extraction."""

    def test_get_email_provider_config_present(self):
        """Test extracting email provider config when present."""
        provider_config = EmailProviderConfig(provider=EmailProviderType.GMAIL)
        config_data = {"email_provider_config": provider_config}
        
        result = get_email_provider_config(config_data)
        
        assert result == provider_config

    def test_get_email_provider_config_missing(self):
        """Test extracting email provider config when missing."""
        config_data = {"other_key": "value"}
        
        result = get_email_provider_config(config_data)
        
        assert result is None


class TestSchemaValidation:
    """Test Pydantic schema validation."""

    def test_exchange_config_validation_success(self):
        """Test successful Exchange configuration validation."""
        config = ExchangeConfig(
            tenant_id="tenant123",
            client_id="client456",
            client_secret="secret789"
        )
        
        assert config.tenant_id == "tenant123"
        assert config.client_id == "client456"
        assert config.client_secret == "secret789"

    def test_exchange_config_validation_empty_values(self):
        """Test Exchange configuration validation with empty values."""
        with pytest.raises(ValueError, match="Exchange configuration values cannot be empty"):
            ExchangeConfig(
                tenant_id="",
                client_id="client456",
                client_secret="secret789"
            )

    def test_gmail_config_validation_success(self):
        """Test successful Gmail configuration validation."""
        config = GmailConfig(
            gmail_secret="secret123",
            gmail_token="token456"
        )
        
        assert config.gmail_secret == "secret123"
        assert config.gmail_token == "token456"

    def test_gmail_config_validation_none_values(self):
        """Test Gmail configuration validation with None values."""
        config = GmailConfig(
            gmail_secret=None,
            gmail_token="token456"
        )
        
        assert config.gmail_secret is None
        assert config.gmail_token == "token456"

    def test_email_provider_config_exchange_missing_config(self):
        """Test EmailProviderConfig validation when Exchange config is missing."""
        with pytest.raises(ValueError, match="Exchange configuration is required"):
            EmailProviderConfig(
                provider=EmailProviderType.EXCHANGE,
                exchange_config=None
            )

    def test_email_provider_config_gmail_missing_config_allowed(self):
        """Test EmailProviderConfig validation allows missing Gmail config."""
        config = EmailProviderConfig(
            provider=EmailProviderType.GMAIL,
            gmail_config=None
        )
        
        assert config.provider == EmailProviderType.GMAIL
        assert config.gmail_config is None


class TestIntegration:
    """Integration tests for complete configuration flow."""

    @patch("builtins.open", new_callable=mock_open, read_data="""
email: integration@example.com
email_provider: exchange
exchange_config:
  tenant_id: ${EXCHANGE_TENANT_ID}
  client_id: ${EXCHANGE_CLIENT_ID}
  client_secret: ${EXCHANGE_CLIENT_SECRET}
""")
    def test_full_exchange_configuration_flow(self, mock_file):
        """Test complete Exchange configuration loading and validation flow."""
        with patch.dict(os.environ, {
            "EXCHANGE_TENANT_ID": "integration-tenant",
            "EXCHANGE_CLIENT_ID": "integration-client",
            "EXCHANGE_CLIENT_SECRET": "integration-secret"
        }):
            config_input = {"configurable": {}}
            
            # Load configuration
            result = get_config(config_input)
            
            # Extract provider configuration
            provider_config = get_email_provider_config(result)
            
            # Validate configuration
            is_valid = validate_email_provider_config(provider_config)
            
            assert is_valid is True
            assert provider_config.provider == EmailProviderType.EXCHANGE
            assert provider_config.exchange_config.tenant_id == "integration-tenant"
            assert provider_config.exchange_config.client_id == "integration-client"
            assert provider_config.exchange_config.client_secret == "integration-secret"

    @patch("builtins.open", new_callable=mock_open, read_data="""
email: legacy@example.com
# Legacy configuration without explicit provider settings
""")
    def test_full_backward_compatibility_flow(self, mock_file):
        """Test complete backward compatibility flow for existing Gmail installations."""
        config_input = {"configurable": {}}
        
        # Load configuration
        result = get_config(config_input)
        
        # Extract provider configuration
        provider_config = get_email_provider_config(result)
        
        # Validate configuration
        is_valid = validate_email_provider_config(provider_config)
        
        assert is_valid is True
        assert provider_config.provider == EmailProviderType.GMAIL
        assert provider_config.gmail_config is None  # Legacy mode
        assert provider_config.exchange_config is None
