#!/usr/bin/env python3
"""
Stage 9 Verification Script - Configuration System Updates

This script verifies the configuration system updates for email provider selection
and Exchange-specific configuration parameters.
"""

import sys
import os
import tempfile
import yaml
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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


def test_environment_variable_substitution():
    """Test environment variable substitution functionality."""
    print("Testing environment variable substitution...")
    
    # Set test environment variables
    os.environ["TEST_TENANT"] = "test-tenant-123"
    os.environ["TEST_CLIENT"] = "test-client-456"
    os.environ["TEST_SECRET"] = "test-secret-789"
    
    config_data = {
        "exchange_config": {
            "tenant_id": "${TEST_TENANT}",
            "client_id": "${TEST_CLIENT}",
            "client_secret": "${TEST_SECRET}"
        },
        "static_value": "no_substitution"
    }
    
    result = _substitute_env_vars(config_data)
    
    assert result["exchange_config"]["tenant_id"] == "test-tenant-123"
    assert result["exchange_config"]["client_id"] == "test-client-456"
    assert result["exchange_config"]["client_secret"] == "test-secret-789"
    assert result["static_value"] == "no_substitution"
    
    print("✓ Environment variable substitution working correctly")


def test_gmail_provider_configuration():
    """Test Gmail provider configuration loading."""
    print("Testing Gmail provider configuration...")
    
    config_data = {
        "email_provider": "gmail",
        "gmail_config": {
            "gmail_secret": "test_gmail_secret",
            "gmail_token": "test_gmail_token"
        }
    }
    
    provider_config = _load_provider_config(config_data)
    
    assert provider_config is not None
    assert provider_config.provider == EmailProviderType.GMAIL
    assert provider_config.gmail_config is not None
    assert provider_config.gmail_config.gmail_secret == "test_gmail_secret"
    assert provider_config.gmail_config.gmail_token == "test_gmail_token"
    assert provider_config.exchange_config is None
    
    # Test validation
    assert validate_email_provider_config(provider_config) is True
    
    print("✓ Gmail provider configuration working correctly")


def test_exchange_provider_configuration():
    """Test Exchange provider configuration loading."""
    print("Testing Exchange provider configuration...")
    
    config_data = {
        "email_provider": "exchange",
        "exchange_config": {
            "tenant_id": "test-tenant-id",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret"
        }
    }
    
    provider_config = _load_provider_config(config_data)
    
    assert provider_config is not None
    assert provider_config.provider == EmailProviderType.EXCHANGE
    assert provider_config.exchange_config is not None
    assert provider_config.exchange_config.tenant_id == "test-tenant-id"
    assert provider_config.exchange_config.client_id == "test-client-id"
    assert provider_config.exchange_config.client_secret == "test-client-secret"
    assert provider_config.gmail_config is None
    
    # Test validation
    assert validate_email_provider_config(provider_config) is True
    
    print("✓ Exchange provider configuration working correctly")


def test_backward_compatibility():
    """Test backward compatibility with existing Gmail configurations."""
    print("Testing backward compatibility...")
    
    # Test with no provider specified (should default to Gmail)
    config_data = {
        "email": "test@example.com",
        "name": "Test User"
        # No email_provider specified
    }
    
    provider_config = _load_provider_config(config_data)
    
    assert provider_config is not None
    assert provider_config.provider == EmailProviderType.GMAIL
    assert provider_config.gmail_config is None  # No explicit Gmail config
    assert provider_config.exchange_config is None
    
    # Test validation (should pass for backward compatibility)
    assert validate_email_provider_config(provider_config) is True
    
    print("✓ Backward compatibility working correctly")


def test_configuration_validation():
    """Test configuration validation for different scenarios."""
    print("Testing configuration validation...")
    
    # Test valid Gmail config
    gmail_config = EmailProviderConfig(
        provider=EmailProviderType.GMAIL,
        gmail_config=GmailConfig(gmail_secret="secret", gmail_token="token")
    )
    assert validate_email_provider_config(gmail_config) is True
    
    # Test Gmail config without explicit config (backward compatibility)
    gmail_legacy_config = EmailProviderConfig(
        provider=EmailProviderType.GMAIL,
        gmail_config=None
    )
    assert validate_email_provider_config(gmail_legacy_config) is True
    
    # Test valid Exchange config
    exchange_config = EmailProviderConfig(
        provider=EmailProviderType.EXCHANGE,
        exchange_config=ExchangeConfig(
            tenant_id="tenant",
            client_id="client",
            client_secret="secret"
        )
    )
    assert validate_email_provider_config(exchange_config) is True
    
    # Test Exchange config validation during creation (should raise error)
    try:
        EmailProviderConfig(
            provider=EmailProviderType.EXCHANGE,
            exchange_config=None
        )
        assert False, "Should have raised ValidationError"
    except ValueError:
        pass  # Expected
    
    print("✓ Configuration validation working correctly")


def test_full_configuration_loading():
    """Test full configuration loading with YAML and environment variables."""
    print("Testing full configuration loading...")
    
    # Create temporary YAML config
    yaml_content = """
email: integration@example.com
email_provider: exchange
exchange_config:
  tenant_id: ${INTEGRATION_TENANT_ID}
  client_id: ${INTEGRATION_CLIENT_ID}
  client_secret: ${INTEGRATION_CLIENT_SECRET}
name: Integration Test
"""
    
    # Set environment variables
    os.environ["INTEGRATION_TENANT_ID"] = "integration-tenant"
    os.environ["INTEGRATION_CLIENT_ID"] = "integration-client"
    os.environ["INTEGRATION_CLIENT_SECRET"] = "integration-secret"
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_config_path = f.name
    
    try:
        # Mock the config file path
        from unittest.mock import patch
        with patch('eaia.main.config._ROOT') as mock_root:
            mock_root.joinpath.return_value = Path(temp_config_path)
            
            config_input = {"configurable": {}}  # No email in configurable
            result = get_config(config_input)
            
            # Verify basic config loading
            assert result["email"] == "integration@example.com"
            assert result["name"] == "Integration Test"
            
            # Verify provider configuration
            provider_config = get_email_provider_config(result)
            assert provider_config is not None
            assert provider_config.provider == EmailProviderType.EXCHANGE
            assert provider_config.exchange_config.tenant_id == "integration-tenant"
            assert provider_config.exchange_config.client_id == "integration-client"
            assert provider_config.exchange_config.client_secret == "integration-secret"
            
            # Verify validation
            assert validate_email_provider_config(provider_config) is True
            
    finally:
        # Clean up
        os.unlink(temp_config_path)
        # Clean up environment variables
        for key in ["INTEGRATION_TENANT_ID", "INTEGRATION_CLIENT_ID", "INTEGRATION_CLIENT_SECRET"]:
            if key in os.environ:
                del os.environ[key]
    
    print("✓ Full configuration loading working correctly")


def test_configurable_override():
    """Test configuration loading from configurable parameter."""
    print("Testing configurable parameter override...")
    
    config_input = {
        "configurable": {
            "email": "configurable@example.com",
            "email_provider": "gmail",
            "gmail_config": {
                "gmail_secret": "configurable_secret",
                "gmail_token": "configurable_token"
            },
            "name": "Configurable User"
        }
    }
    
    result = get_config(config_input)
    
    # Verify basic config
    assert result["email"] == "configurable@example.com"
    assert result["name"] == "Configurable User"
    
    # Verify provider configuration
    provider_config = get_email_provider_config(result)
    assert provider_config is not None
    assert provider_config.provider == EmailProviderType.GMAIL
    assert provider_config.gmail_config.gmail_secret == "configurable_secret"
    assert provider_config.gmail_config.gmail_token == "configurable_token"
    
    print("✓ Configurable parameter override working correctly")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Stage 9 Configuration System Updates Verification")
    print("=" * 60)
    
    try:
        test_environment_variable_substitution()
        test_gmail_provider_configuration()
        test_exchange_provider_configuration()
        test_backward_compatibility()
        test_configuration_validation()
        test_full_configuration_loading()
        test_configurable_override()
        
        print("\n" + "=" * 60)
        print("✅ ALL STAGE 9 VERIFICATION TESTS PASSED!")
        print("✅ Configuration system updates are complete and working correctly")
        print("=" * 60)
        
        # Print summary of capabilities
        print("\n📋 Configuration System Capabilities:")
        print("• Email provider selection (Gmail/Exchange)")
        print("• Environment variable substitution")
        print("• Provider-specific configuration validation")
        print("• Backward compatibility with existing Gmail configs")
        print("• Configurable parameter override support")
        print("• Comprehensive error handling and validation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
