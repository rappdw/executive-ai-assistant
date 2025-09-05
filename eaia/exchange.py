"""
Microsoft Exchange integration module for EAIA.

This module provides Exchange/Outlook email and calendar functionality
using Microsoft Graph API, designed to match the Gmail module interface.
"""

import logging
from datetime import datetime, timedelta, time
from typing import Iterable, List, Optional, Any, Dict
import os
import json
from pathlib import Path

import msal
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from eaia.schemas import EmailData

logger = logging.getLogger(__name__)

# Microsoft Graph API scopes required for email and calendar access
_EXCHANGE_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send", 
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/User.Read",
]

# Token cache file location
_TOKEN_CACHE_FILE = Path.home() / ".eaia" / "exchange_token_cache.json"


class ExchangeCredentials:
    """Exchange credentials wrapper compatible with existing patterns."""
    
    def __init__(self, access_token: str, expires_in: int = 3600, refresh_token: Optional[str] = None):
        self.token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.scopes = _EXCHANGE_SCOPES
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert credentials to dictionary format."""
        return {
            "access_token": self.token,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scopes": self.scopes
        }


def _get_token_cache() -> msal.SerializableTokenCache:
    """Get or create token cache for MSAL."""
    cache = msal.SerializableTokenCache()
    
    if _TOKEN_CACHE_FILE.exists():
        try:
            with open(_TOKEN_CACHE_FILE, 'r') as f:
                cache.deserialize(f.read())
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load token cache: {e}")
    
    return cache


def _save_token_cache(cache: msal.SerializableTokenCache) -> None:
    """Save token cache to file."""
    try:
        _TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if cache.has_state_changed:
            with open(_TOKEN_CACHE_FILE, 'w') as f:
                f.write(cache.serialize())
    except IOError as e:
        logger.warning(f"Failed to save token cache: {e}")


async def get_exchange_credentials(
    user_email: str,
    tenant_id: str,
    client_id: str,
    client_secret: str
) -> ExchangeCredentials:
    """Get Microsoft Graph API credentials using MSAL.
    
    Args:
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID
        client_id: Azure AD application client ID
        client_secret: Azure AD application client secret
        
    Returns:
        ExchangeCredentials object containing access token and related auth info
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If MSAL authentication flow fails
    """
    if not all([user_email, tenant_id, client_id, client_secret]):
        raise ValueError("All authentication parameters (user_email, tenant_id, client_id, client_secret) are required")
    
    try:
        # Get token cache
        cache = _get_token_cache()
        
        # Create MSAL confidential client application
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
            token_cache=cache
        )
        
        # Try to get token from cache first
        accounts = app.get_accounts(username=user_email)
        result = None
        
        if accounts:
            logger.info(f"Found cached account for {user_email}")
            # Try to get token silently from cache
            result = app.acquire_token_silent(
                scopes=_EXCHANGE_SCOPES,
                account=accounts[0]
            )
        
        if not result:
            logger.info(f"No cached token found, initiating device flow for {user_email}")
            # Initiate device flow for interactive authentication
            device_flow = app.initiate_device_flow(scopes=_EXCHANGE_SCOPES)
            
            if "user_code" not in device_flow:
                raise Exception("Failed to create device flow")
            
            print(f"\nTo authenticate with Exchange/Outlook:")
            print(f"1. Go to: {device_flow['verification_uri']}")
            print(f"2. Enter code: {device_flow['user_code']}")
            print("3. Complete the authentication process")
            print("Waiting for authentication...")
            
            # Complete device flow
            result = app.acquire_token_by_device_flow(device_flow)
        
        # Save token cache
        _save_token_cache(cache)
        
        # Check if authentication was successful
        if "access_token" not in result:
            error_msg = result.get("error_description", "Unknown authentication error")
            logger.error(f"Authentication failed: {error_msg}")
            raise Exception(f"Authentication failed: {error_msg}")
        
        logger.info(f"Successfully authenticated {user_email}")
        
        # Return credentials object
        return ExchangeCredentials(
            access_token=result["access_token"],
            expires_in=result.get("expires_in", 3600),
            refresh_token=result.get("refresh_token")
        )
        
    except Exception as e:
        logger.error(f"Failed to get Exchange credentials: {e}")
        raise


async def refresh_exchange_token(
    user_email: str,
    tenant_id: str,
    client_id: str,
    client_secret: str
) -> Optional[ExchangeCredentials]:
    """Refresh Exchange access token using cached refresh token.
    
    Args:
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID
        client_id: Azure AD application client ID
        client_secret: Azure AD application client secret
        
    Returns:
        ExchangeCredentials object with new access token, or None if refresh failed
        
    Raises:
        Exception: If token refresh fails
    """
    try:
        # Get token cache
        cache = _get_token_cache()
        
        # Create MSAL confidential client application
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
            token_cache=cache
        )
        
        # Try to get accounts from cache
        accounts = app.get_accounts(username=user_email)
        
        if not accounts:
            logger.warning(f"No cached accounts found for {user_email}")
            return None
        
        # Try to acquire token silently (this will use refresh token if needed)
        result = app.acquire_token_silent(
            scopes=_EXCHANGE_SCOPES,
            account=accounts[0]
        )
        
        # Save updated cache
        _save_token_cache(cache)
        
        if result and "access_token" in result:
            logger.info(f"Successfully refreshed token for {user_email}")
            return ExchangeCredentials(
                access_token=result["access_token"],
                expires_in=result.get("expires_in", 3600),
                refresh_token=result.get("refresh_token")
            )
        else:
            error_msg = result.get("error_description", "Token refresh failed") if result else "No result from token refresh"
            logger.warning(f"Token refresh failed for {user_email}: {error_msg}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to refresh Exchange token: {e}")
        raise


def validate_exchange_scopes(required_scopes: List[str]) -> bool:
    """Validate that required scopes are included in the Exchange scopes.
    
    Args:
        required_scopes: List of required Microsoft Graph scopes
        
    Returns:
        bool: True if all required scopes are available, False otherwise
    """
    return all(scope in _EXCHANGE_SCOPES for scope in required_scopes)


def get_exchange_auth_from_env(user_email: str) -> tuple[str, str, str]:
    """Get Exchange authentication parameters from environment variables.
    
    Args:
        user_email: User's Exchange email address (for logging)
        
    Returns:
        tuple: (tenant_id, client_id, client_secret)
        
    Raises:
        ValueError: If required environment variables are not set
    """
    tenant_id = os.getenv("EXCHANGE_TENANT_ID")
    client_id = os.getenv("EXCHANGE_CLIENT_ID") 
    client_secret = os.getenv("EXCHANGE_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        missing = []
        if not tenant_id:
            missing.append("EXCHANGE_TENANT_ID")
        if not client_id:
            missing.append("EXCHANGE_CLIENT_ID")
        if not client_secret:
            missing.append("EXCHANGE_CLIENT_SECRET")
        raise ValueError(f"Missing required environment variables for {user_email}: {', '.join(missing)}")
    
    return tenant_id, client_id, client_secret


async def fetch_exchange_emails(
    user_email: str,
    minutes_since: int = 30,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> Iterable[EmailData]:
    """Fetch Exchange emails from the last N minutes.
    
    Args:
        user_email: User's Exchange email address
        minutes_since: Number of minutes back to fetch emails (default: 30)
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)
        
    Yields:
        EmailData: Email data matching the Gmail module format
        
    Raises:
        ValueError: If authentication fails
        Exception: If API call fails
    """
    logger.info(f"Fetching Exchange emails for {user_email} from last {minutes_since} minutes")
    
    # Get authentication parameters
    if not all([tenant_id, client_id, client_secret]):
        tenant_id, client_id, client_secret = get_exchange_auth_from_env()
    
    # Get authenticated credentials
    try:
        credentials = await get_exchange_credentials(
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    except Exception as e:
        logger.error(f"Failed to get Exchange credentials: {e}")
        raise ValueError(f"Authentication failed: {e}")
    
    # Calculate time filter for Microsoft Graph API
    from datetime import datetime, timedelta, timezone
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes_since)
    filter_time = cutoff_time.isoformat().replace('+00:00', 'Z')
    
    # Build Microsoft Graph API request
    graph_url = "https://graph.microsoft.com/v1.0/me/messages"
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    # Query parameters for filtering and pagination
    params = {
        "$filter": f"receivedDateTime ge {filter_time}",
        "$orderby": "receivedDateTime desc",
        "$top": 50,  # Page size
        "$select": "id,conversationId,subject,from,toRecipients,receivedDateTime,body,isRead"
    }
    
    emails = []
    next_link = None
    
    try:
        import requests
        import asyncio
        
        while True:
            # Use next_link if available, otherwise use base URL with params
            if next_link:
                response = requests.get(next_link, headers=headers, timeout=30)
            else:
                response = requests.get(graph_url, headers=headers, params=params, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, waiting {retry_after} seconds")
                await asyncio.sleep(retry_after)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # Process messages in this page
            messages = data.get('value', [])
            for message in messages:
                try:
                    email_data = convert_exchange_message_to_email_data(message)
                    emails.append(email_data)
                except Exception as e:
                    logger.warning(f"Failed to convert message {message.get('id', 'unknown')}: {e}")
                    continue
            
            # Check for next page
            next_link = data.get('@odata.nextLink')
            if not next_link:
                break
                
            logger.debug(f"Fetched {len(messages)} messages, continuing to next page")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Microsoft Graph API request failed: {e}")
        raise Exception(f"Failed to fetch emails from Exchange: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching Exchange emails: {e}")
        raise
    
    logger.info(f"Successfully fetched {len(emails)} Exchange emails")
    return emails


def convert_exchange_message_to_email_data(exchange_msg: dict) -> EmailData:
    """Convert Exchange message format to EmailData schema.
    
    Args:
        exchange_msg: Raw message from Microsoft Graph API
        
    Returns:
        EmailData: Converted email data matching Gmail module format
        
    Raises:
        KeyError: If required fields are missing from exchange message
        ValueError: If message format is invalid
    """
    try:
        # Extract basic message information
        message_id = exchange_msg["id"]
        thread_id = exchange_msg.get("conversationId", message_id)  # Fallback to message ID
        subject = exchange_msg.get("subject", "")
        received_time = exchange_msg.get("receivedDateTime", "")
        
        # Extract sender information
        from_info = exchange_msg.get("from", {})
        if from_info and "emailAddress" in from_info:
            from_email = from_info["emailAddress"].get("address", "")
        else:
            from_email = ""
        
        # Extract recipient information (use first recipient as primary)
        to_recipients = exchange_msg.get("toRecipients", [])
        if to_recipients and len(to_recipients) > 0:
            to_email = to_recipients[0]["emailAddress"].get("address", "")
        else:
            to_email = ""
        
        # Extract and process message body
        body_content = extract_exchange_message_body(exchange_msg.get("body", {}))
        
        return EmailData(
            id=message_id,
            thread_id=thread_id,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            page_content=body_content,
            send_time=received_time
        )
        
    except KeyError as e:
        logger.error(f"Missing required field in Exchange message: {e}")
        raise KeyError(f"Invalid Exchange message format: missing {e}")
    except Exception as e:
        logger.error(f"Error converting Exchange message: {e}")
        raise ValueError(f"Failed to convert Exchange message: {e}")


def extract_exchange_message_body(body: dict) -> str:
    """Extract message body content from Exchange message body object.
    
    Args:
        body: Body object from Microsoft Graph message
        
    Returns:
        str: Plain text content of the message body
    """
    import re
    from html import unescape
    
    if not body:
        return "No message body available."
    
    content = body.get("content", "")
    content_type = body.get("contentType", "text").lower()
    
    if not content:
        return "No message body available."
    
    # Handle HTML content
    if content_type == "html":
        try:
            # Remove HTML tags and decode HTML entities
            # First remove script and style elements completely
            content = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML tags but keep the content
            content = re.sub(r'<[^>]+>', '', content)
            
            # Decode HTML entities
            content = unescape(content)
            
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
        except Exception as e:
            logger.warning(f"Failed to parse HTML content: {e}")
            # Fall back to raw content if HTML parsing fails
    
    # Handle plain text content (or fallback from HTML)
    if content_type == "text" or not content.strip():
        # Clean up whitespace for plain text
        content = re.sub(r'\s+', ' ', content).strip() if content else ""
    
    return content if content else "No message body available."


def send_exchange_email(
    message_id: str,
    response_text: str,
    user_email: str,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    addn_recipients: Optional[List[str]] = None,
    **kwargs: Any
) -> bool:
    """Send a reply to an Exchange email.
    
    Args:
        message_id: ID of the original message to reply to
        response_text: Text content of the reply
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)
        addn_recipients: Additional recipients for the reply
        **kwargs: Additional parameters for future extensibility
        
    Returns:
        bool: True if email was sent successfully, False otherwise
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If API call fails
    """
    # TODO: Implement Exchange email sending using Microsoft Graph API
    # This will be implemented in Stage 4
    raise NotImplementedError("Exchange email sending will be implemented in Stage 4")


def mark_exchange_as_read(
    message_id: str,
    user_email: str,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> bool:
    """Mark an Exchange email as read.
    
    Args:
        message_id: ID of the message to mark as read
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)
        
    Returns:
        bool: True if message was marked as read successfully, False otherwise
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If API call fails
    """
    # TODO: Implement Exchange message status update using Microsoft Graph API
    # This will be implemented in Stage 5
    raise NotImplementedError("Exchange message status update will be implemented in Stage 5")


class ExchangeCalInput(BaseModel):
    """Input schema for Exchange calendar operations."""
    date_strs: List[str] = Field(
        description="The days for which to retrieve events. Each day should be represented by dd-mm-yyyy string."
    )


@tool(args_schema=ExchangeCalInput)
def get_exchange_events_for_days(
    date_strs: List[str],
    user_email: Optional[str] = None,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> str:
    """Retrieve Exchange calendar events for specified days.
    
    Retrieves events for a list of days. If you want to check for multiple days, 
    call this with multiple inputs.

    Input in the format of ['dd-mm-yyyy', 'dd-mm-yyyy']

    Args:
        date_strs: The days for which to retrieve events (dd-mm-yyyy string).
        user_email: User's Exchange email address (optional, can be from config)
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)

    Returns:
        str: Formatted string containing availability for those days.
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If API call fails
    """
    # TODO: Implement Exchange calendar event retrieval using Microsoft Graph API
    # This will be implemented in Stage 6
    raise NotImplementedError("Exchange calendar event retrieval will be implemented in Stage 6")


def send_exchange_calendar_invite(
    emails: List[str],
    title: str,
    start_time: str,
    end_time: str,
    user_email: str,
    timezone: str = "UTC",
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> bool:
    """Send an Exchange calendar invite.
    
    Args:
        emails: List of email addresses to invite
        title: Meeting title/subject
        start_time: Meeting start time in ISO format (e.g., '2024-07-01T14:00:00')
        end_time: Meeting end time in ISO format (e.g., '2024-07-01T15:00:00')
        user_email: User's Exchange email address
        timezone: Timezone for the meeting (default: UTC)
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)
        
    Returns:
        bool: True if calendar invite was sent successfully, False otherwise
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If API call fails
    """
    # TODO: Implement Exchange calendar invite sending using Microsoft Graph API
    # This will be implemented in Stage 7
    raise NotImplementedError("Exchange calendar invite sending will be implemented in Stage 7")


# Helper functions for future implementation

def _get_auth_from_env() -> tuple[str, str, str]:
    """Get authentication parameters from environment variables.
    
    Returns:
        tuple: (tenant_id, client_id, client_secret)
        
    Raises:
        ValueError: If required environment variables are not set
    """
    tenant_id = os.getenv("EXCHANGE_TENANT_ID")
    client_id = os.getenv("EXCHANGE_CLIENT_ID") 
    client_secret = os.getenv("EXCHANGE_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        missing = []
        if not tenant_id:
            missing.append("EXCHANGE_TENANT_ID")
        if not client_id:
            missing.append("EXCHANGE_CLIENT_ID")
        if not client_secret:
            missing.append("EXCHANGE_CLIENT_SECRET")
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return tenant_id, client_id, client_secret


def _format_exchange_datetime_with_timezone(dt_str: str, timezone: str = "UTC") -> str:
    """Format a datetime string with the specified timezone for Exchange.
    
    Args:
        dt_str: The datetime string to format
        timezone: The timezone to use for formatting
        
    Returns:
        str: A formatted datetime string with the timezone abbreviation
    """
    # TODO: Implement datetime formatting for Exchange
    # This will be implemented alongside calendar functionality
    raise NotImplementedError("DateTime formatting will be implemented with calendar functionality")


def _print_exchange_events(events: List[dict]) -> str:
    """Print Exchange events in a human-readable format.
    
    Args:
        events: List of Exchange events to format
        
    Returns:
        str: Formatted string representation of events
    """
    # TODO: Implement event formatting for Exchange
    # This will be implemented alongside calendar functionality
    raise NotImplementedError("Event formatting will be implemented with calendar functionality")
