# Managing API Keys with Keyring

This project now supports storing API keys and secrets in your system's keyring/keychain instead of environment variables. This provides a more secure way to store sensitive credentials.

## Setup

1. Install the project dependencies with Poetry:
```bash
poetry install
```

2. Store your API keys in the keyring:
```python
from eaia.credentials import (
    set_openai_api_key,
    set_anthropic_api_key,
    set_gmail_token,
    set_google_client_secrets,
    set_langsmith_api_key
)

# Store your API keys
set_openai_api_key("your-openai-key")
set_anthropic_api_key("your-anthropic-key")
set_langsmith_api_key("your-langsmith-key")

# For Gmail/Google Calendar integration:
# 1. Store your OAuth token (if you have one)
set_gmail_token("your-gmail-token")

# 2. Store your Google OAuth client secrets JSON
# You can download this from Google Cloud Console (see README.md for specific steps)
with open('path/to/your/client_secrets.json') as f:
    set_google_client_secrets(f.read())
```

## How it Works

The system will check for credentials in this order:
1. Environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
2. System keyring

When the `eaia` package is imported, it automatically loads API keys from keyring into environment variables (if they're not already set). This ensures that both LangChain and the Google API client library can access the credentials in their expected formats.

This means you can:
1. Set environment variables directly (they take precedence)
2. Store credentials in keyring and let them be automatically loaded
3. Use a combination of both approaches

## Environment Variables vs Keyring Names

| Credential | Environment Variable | Keyring Name |
|------------|---------------------|--------------|
| OpenAI API Key | OPENAI_API_KEY | openai_api_key |
| Anthropic API Key | ANTHROPIC_API_KEY | anthropic_api_key |
| LangSmith API Key | LANGSMITH_API_KEY | langsmith_api_key |
| Gmail Token | GMAIL_TOKEN | gmail_token |
| Google Client Secrets | GOOGLE_CLIENT_SECRETS | google_client_secrets |

## Google OAuth Setup

The Gmail/Google Calendar integration uses OAuth2 for authentication. This requires:

1. A client secrets JSON file from Google Cloud Console
   - Download this from your Google Cloud Console (see README.md for specific steps)
   - Store the contents in keyring using `set_google_client_secrets()`
   - The system will use this directly for OAuth authentication

2. An OAuth token (after authentication)
   - This is obtained after the first successful authentication
   - Automatically stored in keyring using `set_gmail_token()`
   - Future sessions will reuse this token from keyring
   - Token is automatically refreshed when expired

## Security Notes

- The keyring/keychain is encrypted and managed by your operating system
- Each credential is stored under the service name "executive_ai_assistant"
- You can remove credentials from the keyring using your system's keychain management tools
- Credentials loaded from keyring into environment variables only exist for the duration of your Python process
- No credentials are ever written to disk - everything is stored securely in keyring
