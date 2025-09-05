import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from eaia.schemas import EmailProviderConfig, EmailProviderType, ExchangeConfig, GmailConfig

_ROOT = Path(__file__).absolute().parent
logger = logging.getLogger(__name__)


def _substitute_env_vars(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively substitute environment variables in configuration values."""
    if isinstance(config_dict, dict):
        return {k: _substitute_env_vars(v) for k, v in config_dict.items()}
    elif isinstance(config_dict, str) and config_dict.startswith("${") and config_dict.endswith("}"):
        env_var = config_dict[2:-1]  # Remove ${ and }
        return os.getenv(env_var, config_dict)  # Return original if env var not found
    else:
        return config_dict


def _load_provider_config(config_data: Dict[str, Any]) -> Optional[EmailProviderConfig]:
    """Load and validate email provider configuration."""
    try:
        # Get provider type (default to gmail for backward compatibility)
        provider_str = config_data.get("email_provider", "gmail")
        provider = EmailProviderType(provider_str)
        
        # Load provider-specific configurations
        gmail_config = None
        exchange_config = None
        
        if "gmail_config" in config_data and config_data["gmail_config"]:
            gmail_data = config_data["gmail_config"]
            # Filter out None values and empty strings
            gmail_data = {k: v for k, v in gmail_data.items() if v and v != ""}
            if gmail_data:
                gmail_config = GmailConfig(**gmail_data)
        
        if "exchange_config" in config_data and config_data["exchange_config"]:
            exchange_data = config_data["exchange_config"]
            # Filter out None values and empty strings
            exchange_data = {k: v for k, v in exchange_data.items() if v and v != ""}
            if exchange_data:
                exchange_config = ExchangeConfig(**exchange_data)
        
        # Create and validate provider configuration
        provider_config = EmailProviderConfig(
            provider=provider,
            gmail_config=gmail_config,
            exchange_config=exchange_config
        )
        
        logger.info(f"Loaded email provider configuration: {provider.value}")
        return provider_config
        
    except Exception as e:
        logger.warning(f"Failed to load provider configuration: {e}")
        return None


def get_config(config: dict):
    """Load configuration with email provider support.
    
    This loads things either ALL from configurable, or all from the config.yaml.
    This is done intentionally to enforce an "all or nothing" configuration.
    Now includes email provider configuration loading and validation.
    """
    if "email" in config["configurable"]:
        config_data = config["configurable"]
    else:
        with open(_ROOT.joinpath("config.yaml")) as stream:
            config_data = yaml.safe_load(stream)
    
    # Substitute environment variables
    config_data = _substitute_env_vars(config_data)
    
    # Load email provider configuration
    provider_config = _load_provider_config(config_data)
    if provider_config:
        config_data["email_provider_config"] = provider_config
    
    return config_data


def get_email_provider_config(config_data: Dict[str, Any]) -> Optional[EmailProviderConfig]:
    """Extract email provider configuration from loaded config data."""
    return config_data.get("email_provider_config")


def validate_email_provider_config(provider_config: EmailProviderConfig) -> bool:
    """Validate email provider configuration completeness."""
    try:
        if provider_config.provider == EmailProviderType.GMAIL:
            # For Gmail, allow legacy configuration loading if no explicit config
            return True
        elif provider_config.provider == EmailProviderType.EXCHANGE:
            # Exchange requires explicit configuration
            if not provider_config.exchange_config:
                logger.error("Exchange provider selected but no exchange_config provided")
                return False
            return True
        else:
            logger.error(f"Unsupported email provider: {provider_config.provider}")
            return False
    except Exception as e:
        logger.error(f"Error validating email provider configuration: {e}")
        return False
