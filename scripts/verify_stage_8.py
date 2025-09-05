#!/usr/bin/env python3
"""
Stage 8 Verification Script - Email Provider Interface

This script verifies the unified email provider interface implementation
by testing provider instantiation, configuration validation, and interface compliance.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eaia.email_provider import (
    EmailProvider,
    EmailProviderFactory,
    GmailProvider,
    ExchangeProvider,
    EmailInterface
)


def test_provider_enum():
    """Test EmailProvider enum functionality."""
    print("Testing EmailProvider enum...")
    
    # Test enum values
    assert EmailProvider.GMAIL.value == "gmail"
    assert EmailProvider.EXCHANGE.value == "exchange"
    
    # Test from_string method
    assert EmailProvider.from_string("gmail") == EmailProvider.GMAIL
    assert EmailProvider.from_string("exchange") == EmailProvider.EXCHANGE
    
    try:
        EmailProvider.from_string("invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ EmailProvider enum tests passed")


def test_factory_pattern():
    """Test EmailProviderFactory functionality."""
    print("Testing EmailProviderFactory...")
    
    # Test Gmail provider creation
    gmail_config = {
        "gmail_secret": "test_secret",
        "gmail_token": "test_token"
    }
    gmail_provider = EmailProviderFactory.create_provider(EmailProvider.GMAIL, gmail_config)
    assert isinstance(gmail_provider, GmailProvider)
    assert isinstance(gmail_provider, EmailInterface)
    
    # Test Exchange provider creation
    exchange_config = {
        "tenant_id": "test_tenant",
        "client_id": "test_client",
        "client_secret": "test_secret"
    }
    exchange_provider = EmailProviderFactory.create_provider(EmailProvider.EXCHANGE, exchange_config)
    assert isinstance(exchange_provider, ExchangeProvider)
    assert isinstance(exchange_provider, EmailInterface)
    
    # Test provider from config
    config_with_type = {
        "provider_type": "gmail",
        "gmail_secret": "test_secret",
        "gmail_token": "test_token"
    }
    provider = EmailProviderFactory.get_provider_from_config(config_with_type)
    assert isinstance(provider, GmailProvider)
    
    print("✓ EmailProviderFactory tests passed")


def test_configuration_validation():
    """Test configuration validation for both providers."""
    print("Testing configuration validation...")
    
    # Test valid Gmail config
    valid_gmail_config = {
        "gmail_secret": "test_secret",
        "gmail_token": "test_token"
    }
    assert EmailProviderFactory.validate_config(EmailProvider.GMAIL, valid_gmail_config) == True
    
    # Test invalid Gmail config
    invalid_gmail_config = {
        "gmail_secret": "test_secret"
        # Missing gmail_token
    }
    assert EmailProviderFactory.validate_config(EmailProvider.GMAIL, invalid_gmail_config) == False
    
    # Test valid Exchange config
    valid_exchange_config = {
        "tenant_id": "test_tenant",
        "client_id": "test_client",
        "client_secret": "test_secret"
    }
    assert EmailProviderFactory.validate_config(EmailProvider.EXCHANGE, valid_exchange_config) == True
    
    # Test invalid Exchange config
    invalid_exchange_config = {
        "tenant_id": "test_tenant",
        "client_id": "test_client"
        # Missing client_secret
    }
    assert EmailProviderFactory.validate_config(EmailProvider.EXCHANGE, invalid_exchange_config) == False
    
    print("✓ Configuration validation tests passed")


def test_interface_compliance():
    """Test that both providers implement the EmailInterface correctly."""
    print("Testing interface compliance...")
    
    # Test Gmail provider interface
    gmail_config = {
        "gmail_secret": "test_secret",
        "gmail_token": "test_token"
    }
    gmail_provider = GmailProvider(gmail_config)
    
    # Check all required methods exist
    assert hasattr(gmail_provider, 'fetch_emails')
    assert hasattr(gmail_provider, 'send_email')
    assert hasattr(gmail_provider, 'mark_as_read')
    assert hasattr(gmail_provider, 'get_events_for_days')
    assert hasattr(gmail_provider, 'send_calendar_invite')
    assert hasattr(gmail_provider, 'get_provider_type')
    assert hasattr(gmail_provider, 'validate_configuration')
    
    # Check provider type
    assert gmail_provider.get_provider_type() == EmailProvider.GMAIL
    
    # Test Exchange provider interface
    exchange_config = {
        "tenant_id": "test_tenant",
        "client_id": "test_client",
        "client_secret": "test_secret"
    }
    exchange_provider = ExchangeProvider(exchange_config)
    
    # Check all required methods exist
    assert hasattr(exchange_provider, 'fetch_emails')
    assert hasattr(exchange_provider, 'send_email')
    assert hasattr(exchange_provider, 'mark_as_read')
    assert hasattr(exchange_provider, 'get_events_for_days')
    assert hasattr(exchange_provider, 'send_calendar_invite')
    assert hasattr(exchange_provider, 'get_provider_type')
    assert hasattr(exchange_provider, 'validate_configuration')
    
    # Check provider type
    assert exchange_provider.get_provider_type() == EmailProvider.EXCHANGE
    
    print("✓ Interface compliance tests passed")


def test_provider_switching():
    """Test switching between providers using the factory."""
    print("Testing provider switching...")
    
    # Create Gmail provider
    gmail_config = {
        "provider_type": "gmail",
        "gmail_secret": "test_secret",
        "gmail_token": "test_token"
    }
    gmail_provider = EmailProviderFactory.get_provider_from_config(gmail_config)
    assert gmail_provider.get_provider_type() == EmailProvider.GMAIL
    
    # Create Exchange provider
    exchange_config = {
        "provider_type": "exchange",
        "tenant_id": "test_tenant",
        "client_id": "test_client",
        "client_secret": "test_secret"
    }
    exchange_provider = EmailProviderFactory.get_provider_from_config(exchange_config)
    assert exchange_provider.get_provider_type() == EmailProvider.EXCHANGE
    
    # Test that both providers have the same interface
    gmail_methods = set(dir(gmail_provider))
    exchange_methods = set(dir(exchange_provider))
    
    # Check that both have the core interface methods
    required_methods = {
        'fetch_emails', 'send_email', 'mark_as_read',
        'get_events_for_days', 'send_calendar_invite',
        'get_provider_type', 'validate_configuration'
    }
    
    assert required_methods.issubset(gmail_methods)
    assert required_methods.issubset(exchange_methods)
    
    print("✓ Provider switching tests passed")


def test_error_handling():
    """Test error handling in factory and providers."""
    print("Testing error handling...")
    
    # Test invalid provider type
    try:
        EmailProviderFactory.create_provider("invalid_type", {})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test missing provider type in config
    try:
        EmailProviderFactory.get_provider_from_config({})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test invalid provider type in config
    try:
        EmailProviderFactory.get_provider_from_config({"provider_type": "invalid"})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ Error handling tests passed")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Stage 8 Email Provider Interface Verification")
    print("=" * 60)
    
    try:
        test_provider_enum()
        test_factory_pattern()
        test_configuration_validation()
        test_interface_compliance()
        test_provider_switching()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ ALL STAGE 8 VERIFICATION TESTS PASSED!")
        print("✅ Email Provider Interface implementation is complete and working correctly")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
