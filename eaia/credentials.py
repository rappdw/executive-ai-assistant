"""
Module for managing API credentials using either environment variables or keyring.
"""
import os
from typing import Optional
import keyring
import json
from pathlib import Path

# Service names for keyring
KEYRING_SERVICE = "executive_ai_assistant"
OPENAI_KEY_NAME = "openai_api_key"
ANTHROPIC_KEY_NAME = "anthropic_api_key"
GMAIL_TOKEN_NAME = "gmail_token"
GOOGLE_CLIENT_SECRETS_NAME = "google_client_secrets"
LANGSMITH_KEY_NAME = "langsmith_api_key"

def get_credential(env_var: str, keyring_name: str) -> Optional[str]:
    """
    Get a credential from either environment variable or keyring.
    Tries environment variable first, then falls back to keyring.
    
    Args:
        env_var: Name of the environment variable
        keyring_name: Name of the key in keyring
        
    Returns:
        The credential value or None if not found
    """
    # Try environment variable first
    value = os.getenv(env_var)
    if value:
        return value
        
    # Fall back to keyring
    return keyring.get_password(keyring_name, KEYRING_SERVICE)

def set_credential_in_keyring(keyring_name: str, value: str) -> None:
    """
    Store a credential in the system keyring.
    
    Args:
        keyring_name: Name of the key in keyring
        value: The credential value to store
    """
    keyring.set_password(keyring_name, KEYRING_SERVICE, value)

def get_openai_api_key() -> Optional[str]:
    """Get the OpenAI API key."""
    return get_credential("OPENAI_API_KEY", OPENAI_KEY_NAME)

def get_anthropic_api_key() -> Optional[str]:
    """Get the Anthropic API key."""
    return get_credential("ANTHROPIC_API_KEY", ANTHROPIC_KEY_NAME)

def get_gmail_token() -> Optional[str]:
    """Get the Gmail token."""
    return get_credential("GMAIL_TOKEN", GMAIL_TOKEN_NAME)

def get_google_client_secrets() -> Optional[str]:
    """Get Google OAuth client secrets JSON from keyring."""
    return get_credential("GOOGLE_CLIENT_SECRETS", GOOGLE_CLIENT_SECRETS_NAME)

def get_langsmith_api_key() -> Optional[str]:
    """Get the LangSmith API key."""
    return get_credential("LANGSMITH_API_KEY", LANGSMITH_KEY_NAME)

# Helper functions to store credentials in keyring
def set_openai_api_key(key: str) -> None:
    """Store OpenAI API key in keyring."""
    set_credential_in_keyring(OPENAI_KEY_NAME, key)

def set_anthropic_api_key(key: str) -> None:
    """Store Anthropic API key in keyring."""
    set_credential_in_keyring(ANTHROPIC_KEY_NAME, key)

def set_gmail_token(token: str) -> None:
    """Store Gmail token in keyring."""
    set_credential_in_keyring(GMAIL_TOKEN_NAME, token)

def set_google_client_secrets(secrets_json: str) -> None:
    """Store Google OAuth client secrets JSON in keyring."""
    set_credential_in_keyring(GOOGLE_CLIENT_SECRETS_NAME, secrets_json)

def set_langsmith_api_key(key: str) -> None:
    """Store LangSmith API key in keyring."""
    set_credential_in_keyring(LANGSMITH_KEY_NAME, key)

def load_credentials_to_env() -> None:
    """
    Load credentials from keyring into environment variables if they're not already set.
    This ensures LangChain and other libraries can access the credentials through
    their expected environment variables.
    """
    # Only set environment variables if they're not already set
    if not os.getenv("OPENAI_API_KEY"):
        key = get_openai_api_key()
        if key:
            os.environ["OPENAI_API_KEY"] = key
            
    if not os.getenv("ANTHROPIC_API_KEY"):
        key = get_anthropic_api_key()
        if key:
            os.environ["ANTHROPIC_API_KEY"] = key
            
    if not os.getenv("GMAIL_TOKEN"):
        token = get_gmail_token()
        if token:
            os.environ["GMAIL_TOKEN"] = token
            
    if not os.getenv("GOOGLE_CLIENT_SECRETS"):
        secrets_json = get_google_client_secrets()
        if secrets_json:
            os.environ["GOOGLE_CLIENT_SECRETS"] = secrets_json
            
    if not os.getenv("LANGSMITH_API_KEY"):
        key = get_langsmith_api_key()
        if key:
            os.environ["LANGSMITH_API_KEY"] = key
