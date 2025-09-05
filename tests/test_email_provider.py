"""
Unit tests for Email Provider Interface implementations.

This module tests the unified email provider interface, factory pattern,
and both Gmail and Exchange provider implementations.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

from eaia.email_provider import (
    EmailProvider,
    EmailProviderFactory,
    GmailProvider,
    ExchangeProvider,
    EmailInterface
)
from eaia.schemas import EmailData


class TestEmailProviderEnum:
    """Test EmailProvider enumeration."""

    def test_email_provider_values(self):
        """Test EmailProvider enum values."""
        assert EmailProvider.GMAIL.value == "gmail"
        assert EmailProvider.EXCHANGE.value == "exchange"

    def test_email_provider_from_string(self):
        """Test creating EmailProvider from string."""
        assert EmailProvider("gmail") == EmailProvider.GMAIL
        assert EmailProvider("exchange") == EmailProvider.EXCHANGE

    def test_email_provider_invalid_string(self):
        """Test creating EmailProvider from invalid string."""
        with pytest.raises(ValueError):
            EmailProvider("invalid")


class TestEmailProviderFactory:
    """Test EmailProviderFactory functionality."""

    def test_create_gmail_provider(self):
        """Test creating Gmail provider."""
        config = {"gmail_secret": "secret", "gmail_token": "token"}
        provider = EmailProviderFactory.create_provider(EmailProvider.GMAIL, config)
        
        assert isinstance(provider, GmailProvider)
        assert provider.get_provider_type() == EmailProvider.GMAIL

    def test_create_exchange_provider(self):
        """Test creating Exchange provider."""
        config = {"tenant_id": "tenant", "client_id": "client", "client_secret": "secret"}
        provider = EmailProviderFactory.create_provider(EmailProvider.EXCHANGE, config)
        
        assert isinstance(provider, ExchangeProvider)
        assert provider.get_provider_type() == EmailProvider.EXCHANGE

    def test_create_provider_invalid_type(self):
        """Test creating provider with invalid type."""
        with pytest.raises(ValueError, match="Unsupported provider type"):
            EmailProviderFactory.create_provider("invalid", {})

    def test_get_provider_from_config_gmail(self):
        """Test getting Gmail provider from config."""
        config = {
            "provider_type": "gmail",
            "gmail_secret": "secret",
            "gmail_token": "token"
        }
        provider = EmailProviderFactory.get_provider_from_config(config)
        
        assert isinstance(provider, GmailProvider)
        assert provider.get_provider_type() == EmailProvider.GMAIL

    def test_get_provider_from_config_exchange(self):
        """Test getting Exchange provider from config."""
        config = {
            "provider_type": "exchange",
            "tenant_id": "tenant",
            "client_id": "client",
            "client_secret": "secret"
        }
        provider = EmailProviderFactory.get_provider_from_config(config)
        
        assert isinstance(provider, ExchangeProvider)
        assert provider.get_provider_type() == EmailProvider.EXCHANGE

    def test_get_provider_from_config_missing_type(self):
        """Test getting provider from config without provider type."""
        config = {"gmail_secret": "secret"}
        
        with pytest.raises(ValueError, match="Missing 'provider_type' in configuration"):
            EmailProviderFactory.get_provider_from_config(config)

    def test_get_provider_from_config_invalid_type(self):
        """Test getting provider from config with invalid type."""
        config = {"provider_type": "invalid"}
        
        with pytest.raises(ValueError, match="Invalid provider type"):
            EmailProviderFactory.get_provider_from_config(config)

    def test_validate_gmail_config_valid(self):
        """Test validating valid Gmail configuration."""
        config = {"gmail_secret": "secret", "gmail_token": "token"}
        
        assert EmailProviderFactory.validate_config(EmailProvider.GMAIL, config)

    def test_validate_gmail_config_invalid(self):
        """Test validating invalid Gmail configuration."""
        config = {"gmail_secret": "secret"}  # Missing gmail_token
        
        assert not EmailProviderFactory.validate_config(EmailProvider.GMAIL, config)

    def test_validate_exchange_config_valid(self):
        """Test validating valid Exchange configuration."""
        config = {"tenant_id": "tenant", "client_id": "client", "client_secret": "secret"}
        
        assert EmailProviderFactory.validate_config(EmailProvider.EXCHANGE, config)

    def test_validate_exchange_config_invalid(self):
        """Test validating invalid Exchange configuration."""
        config = {"tenant_id": "tenant", "client_id": "client"}  # Missing client_secret
        
        assert not EmailProviderFactory.validate_config(EmailProvider.EXCHANGE, config)


class TestGmailProvider:
    """Test GmailProvider implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {"gmail_secret": "test_secret", "gmail_token": "test_token"}
        self.provider = GmailProvider(self.config)

    def test_gmail_provider_initialization(self):
        """Test Gmail provider initialization."""
        assert self.provider.config == self.config
        assert self.provider.get_provider_type() == EmailProvider.GMAIL

    def test_validate_configuration_valid(self):
        """Test Gmail configuration validation with valid config."""
        assert self.provider.validate_configuration()

    def test_validate_configuration_invalid(self):
        """Test Gmail configuration validation with invalid config."""
        invalid_provider = GmailProvider({"gmail_secret": "secret"})  # Missing token
        assert not invalid_provider.validate_configuration()

    @pytest.mark.asyncio
    async def test_fetch_emails(self):
        """Test Gmail email fetching."""
        mock_emails = [
            EmailData(
                id="1",
                thread_id="thread1",
                from_email="sender@example.com",
                to_email="user@example.com",
                subject="Test Email",
                page_content="Test content",
                send_time="2024-01-01T10:00:00Z"
            )
        ]
        
        with patch('eaia.gmail.fetch_group_emails', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_emails
            
            result = await self.provider.fetch_emails("user@example.com", 30)
            
            assert result == mock_emails
            mock_fetch.assert_called_once_with(
                to_email="user@example.com",
                minutes_since=30,
                gmail_token="test_token",
                gmail_secret="test_secret"
            )

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test Gmail email sending."""
        with patch('eaia.gmail.send_email') as mock_send:
            mock_send.return_value = True
            
            result = await self.provider.send_email(
                "msg123", "Reply text", "user@example.com"
            )
            
            assert result is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_as_read(self):
        """Test Gmail mark as read."""
        with patch('eaia.gmail.mark_as_read') as mock_mark:
            mock_mark.return_value = None
            
            result = await self.provider.mark_as_read("msg123", "user@example.com")
            
            assert result is True
            mock_mark.assert_called_once()

    def test_get_events_for_days(self):
        """Test Gmail calendar events retrieval."""
        with patch('eaia.gmail.get_events_for_days') as mock_events:
            mock_events.return_value = "Event list"
            
            result = self.provider.get_events_for_days(["01-01-2024"], "user@example.com")
            
            assert result == "Event list"
            mock_events.assert_called_once()

    def test_send_calendar_invite(self):
        """Test Gmail calendar invite sending."""
        with patch('eaia.gmail.send_calendar_invite') as mock_invite:
            mock_invite.return_value = True
            
            result = self.provider.send_calendar_invite(
                ["attendee@example.com"],
                "Meeting",
                "2024-01-01T14:00:00",
                "2024-01-01T15:00:00",
                "user@example.com"
            )
            
            assert result is True
            mock_invite.assert_called_once()


class TestExchangeProvider:
    """Test ExchangeProvider implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "tenant_id": "test_tenant",
            "client_id": "test_client",
            "client_secret": "test_secret"
        }
        self.provider = ExchangeProvider(self.config)

    def test_exchange_provider_initialization(self):
        """Test Exchange provider initialization."""
        assert self.provider.config == self.config
        assert self.provider.get_provider_type() == EmailProvider.EXCHANGE

    def test_validate_configuration_valid(self):
        """Test Exchange configuration validation with valid config."""
        assert self.provider.validate_configuration()

    def test_validate_configuration_invalid(self):
        """Test Exchange configuration validation with invalid config."""
        invalid_provider = ExchangeProvider({"tenant_id": "tenant"})  # Missing client_id and client_secret
        assert not invalid_provider.validate_configuration()

    @pytest.mark.asyncio
    async def test_fetch_emails(self):
        """Test Exchange email fetching."""
        mock_emails = [
            EmailData(
                id="1",
                thread_id="thread1",
                from_email="sender@example.com",
                to_email="user@example.com",
                subject="Test Email",
                page_content="Test content",
                send_time="2024-01-01T10:00:00Z"
            )
        ]
        
        with patch('eaia.exchange.fetch_exchange_emails', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_emails
            
            result = await self.provider.fetch_emails("user@example.com", 30)
            
            assert result == mock_emails
            mock_fetch.assert_called_once_with(
                user_email="user@example.com",
                minutes_since=30,
                tenant_id="test_tenant",
                client_id="test_client",
                client_secret="test_secret"
            )

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test Exchange email sending."""
        with patch('eaia.exchange.send_exchange_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            result = await self.provider.send_email(
                "msg123", "Reply text", "user@example.com"
            )
            
            assert result is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_as_read(self):
        """Test Exchange mark as read."""
        with patch('eaia.exchange.mark_exchange_as_read', new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = True
            
            result = await self.provider.mark_as_read("msg123", "user@example.com")
            
            assert result is True
            mock_mark.assert_called_once()

    def test_get_events_for_days(self):
        """Test Exchange calendar events retrieval."""
        with patch('eaia.exchange.get_exchange_events_for_days') as mock_events:
            mock_events.return_value = "Event list"
            
            result = self.provider.get_events_for_days(["01-01-2024"], "user@example.com")
            
            assert result == "Event list"
            mock_events.assert_called_once()

    def test_send_calendar_invite(self):
        """Test Exchange calendar invite sending."""
        with patch('eaia.exchange.send_exchange_calendar_invite') as mock_invite:
            mock_invite.return_value = True
            
            result = self.provider.send_calendar_invite(
                ["attendee@example.com"],
                "Meeting",
                "2024-01-01T14:00:00",
                "2024-01-01T15:00:00",
                "user@example.com"
            )
            
            assert result is True
            mock_invite.assert_called_once()


class TestProviderIntegration:
    """Test provider integration and interface compliance."""

    def test_gmail_provider_implements_interface(self):
        """Test that Gmail provider implements EmailInterface."""
        config = {"gmail_secret": "secret", "gmail_token": "token"}
        provider = GmailProvider(config)
        
        assert isinstance(provider, EmailInterface)
        
        # Check all abstract methods are implemented
        assert hasattr(provider, 'fetch_emails')
        assert hasattr(provider, 'send_email')
        assert hasattr(provider, 'mark_as_read')
        assert hasattr(provider, 'get_events_for_days')
        assert hasattr(provider, 'send_calendar_invite')
        assert hasattr(provider, 'get_provider_type')
        assert hasattr(provider, 'validate_configuration')

    def test_exchange_provider_implements_interface(self):
        """Test that Exchange provider implements EmailInterface."""
        config = {"tenant_id": "tenant", "client_id": "client", "client_secret": "secret"}
        provider = ExchangeProvider(config)
        
        assert isinstance(provider, EmailInterface)
        
        # Check all abstract methods are implemented
        assert hasattr(provider, 'fetch_emails')
        assert hasattr(provider, 'send_email')
        assert hasattr(provider, 'mark_as_read')
        assert hasattr(provider, 'get_events_for_days')
        assert hasattr(provider, 'send_calendar_invite')
        assert hasattr(provider, 'get_provider_type')
        assert hasattr(provider, 'validate_configuration')

    def test_provider_factory_creates_compatible_instances(self):
        """Test that factory creates instances compatible with EmailInterface."""
        gmail_config = {"gmail_secret": "secret", "gmail_token": "token"}
        exchange_config = {"tenant_id": "tenant", "client_id": "client", "client_secret": "secret"}
        
        gmail_provider = EmailProviderFactory.create_provider(EmailProvider.GMAIL, gmail_config)
        exchange_provider = EmailProviderFactory.create_provider(EmailProvider.EXCHANGE, exchange_config)
        
        assert isinstance(gmail_provider, EmailInterface)
        assert isinstance(exchange_provider, EmailInterface)
        
        assert gmail_provider.get_provider_type() == EmailProvider.GMAIL
        assert exchange_provider.get_provider_type() == EmailProvider.EXCHANGE

    def test_provider_switching_compatibility(self):
        """Test that providers can be switched seamlessly."""
        gmail_config = {
            "provider_type": "gmail",
            "gmail_secret": "secret",
            "gmail_token": "token"
        }
        exchange_config = {
            "provider_type": "exchange",
            "tenant_id": "tenant",
            "client_id": "client",
            "client_secret": "secret"
        }
        
        # Create providers from config
        gmail_provider = EmailProviderFactory.get_provider_from_config(gmail_config)
        exchange_provider = EmailProviderFactory.get_provider_from_config(exchange_config)
        
        # Both should implement the same interface
        providers = [gmail_provider, exchange_provider]
        
        for provider in providers:
            assert isinstance(provider, EmailInterface)
            assert callable(provider.fetch_emails)
            assert callable(provider.send_email)
            assert callable(provider.mark_as_read)
            assert callable(provider.get_events_for_days)
            assert callable(provider.send_calendar_invite)
            assert callable(provider.get_provider_type)
            assert callable(provider.validate_configuration)

    def test_configuration_parameter_passing(self):
        """Test that configuration parameters are passed correctly."""
        # Test Gmail provider with kwargs override
        gmail_config = {"gmail_secret": "config_secret", "gmail_token": "config_token"}
        gmail_provider = GmailProvider(gmail_config)
        
        with patch('eaia.gmail.fetch_group_emails', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            
            # Test with config values
            asyncio.run(gmail_provider.fetch_emails("user@example.com"))
            
            # Test with kwargs override
            asyncio.run(gmail_provider.fetch_emails(
                "user@example.com",
                gmail_secret="override_secret",
                gmail_token="override_token"
            ))
            
            # Verify both calls were made
            assert mock_fetch.call_count == 2

    def test_error_handling_consistency(self):
        """Test that error handling is consistent across providers."""
        gmail_config = {"gmail_secret": "secret", "gmail_token": "token"}
        exchange_config = {"tenant_id": "tenant", "client_id": "client", "client_secret": "secret"}
        
        gmail_provider = GmailProvider(gmail_config)
        exchange_provider = ExchangeProvider(exchange_config)
        
        # Both providers should handle configuration validation the same way
        assert gmail_provider.validate_configuration()
        assert exchange_provider.validate_configuration()
        
        # Invalid configurations should return False
        invalid_gmail = GmailProvider({})
        invalid_exchange = ExchangeProvider({})
        
        assert not invalid_gmail.validate_configuration()
        assert not invalid_exchange.validate_configuration()
