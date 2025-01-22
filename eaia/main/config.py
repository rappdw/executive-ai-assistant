"""
Configuration loading for EAIA.

This module handles loading configuration either from LangGraph Cloud or local config file.
"""

import os
import platform
import shutil
import yaml
from pathlib import Path


def get_config_dir() -> Path:
    """
    Get the OS-specific configuration directory for EAIA.
    
    Returns:
        Path to the configuration directory
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "eaia"
    elif system == "Linux":
        # Use XDG Base Directory specification
        xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        return Path(xdg_config) / "eaia"
    elif system == "Windows":
        return Path(os.environ["APPDATA"]) / "eaia"
    else:
        # Fallback to ~/.eaia for unknown systems
        return Path.home() / ".eaia"


def get_config_file() -> Path:
    """
    Get the path to the config.yaml file.
    
    Returns:
        Path to the config.yaml file
    """
    return get_config_dir() / "config.yaml"


def ensure_config_exists() -> None:
    """
    Ensure the config directory and file exist.
    Copies the default config if none exists.
    """
    config_dir = get_config_dir()
    config_file = get_config_file()
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # If config file doesn't exist, copy the default
    if not config_file.exists():
        default_config = Path(__file__).parent / "config.template.yaml"
        if default_config.exists():
            shutil.copy2(default_config, config_file)


def get_config(config: dict):
    """
    Get configuration, either from LangGraph Cloud or local config file.
    
    When running in LangGraph Cloud, configuration comes from the config["configurable"] dict.
    When running locally, configuration comes from the OS-specific config file location.
    
    Args:
        config: Configuration dict that may contain LangGraph Cloud configuration
        
    Returns:
        Complete configuration dictionary
    """
    # If running in LangGraph Cloud, use the provided configuration
    if config.get("configurable", {}).get("email"):
        return config["configurable"]
    
    # Otherwise, we're running locally - ensure config exists and load it
    ensure_config_exists()
    with open(get_config_file()) as stream:
        return yaml.safe_load(stream)
