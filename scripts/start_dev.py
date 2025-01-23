#!/usr/bin/env python3
"""
Script to start the development server with credentials loaded from keyring.

This script ensures that all necessary credentials (OpenAI, Anthropic, Gmail, etc.)
are loaded from the system keyring into environment variables before starting the
development server.

The credentials are loaded by importing the eaia package, which triggers the
load_credentials_to_env() function in eaia/credentials.py. This function checks
for each credential in the environment variables and, if not found, loads them
from the system keyring.
"""

import os
import subprocess
import sys

# Import eaia to trigger credentials loading from keyring into environment
# This is done via eaia/__init__.py which imports credentials.py
# credentials.py then calls load_credentials_to_env() which loads:
# - OpenAI API key
# - Anthropic API key
# - Gmail token
# - Google client secrets
# - LangSmith API key
import eaia

def main():
    # Run langgraph dev with the current environment, which now includes
    # all credentials loaded from the keyring
    process = subprocess.Popen(
        ["langgraph", "dev"],
        env=os.environ,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()
