"""
Executive AI Assistant package.
"""
from eaia.credentials import load_credentials_to_env

# Load credentials from keyring into environment variables on package import
load_credentials_to_env()