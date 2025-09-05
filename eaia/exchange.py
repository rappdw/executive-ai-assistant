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


def _get_original_message(message_id: str, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get the original message for reply context.
    
    Args:
        message_id: ID of the original message
        credentials: Authentication credentials dictionary
        
    Returns:
        Dict containing the original message data, or None if not found
    """
    import requests
    
    try:
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        graph_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        
        response = requests.get(graph_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get original message. Status: {response.status_code}, Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed when getting original message: {e}")
        return None


def get_exchange_recipients(original_message: Dict[str, Any], addn_recipients: Optional[List[str]] = None) -> Dict[str, List[Dict[str, str]]]:
    """Extract recipients from original message and add additional recipients.
    
    Args:
        original_message: The original Exchange message
        addn_recipients: Additional recipient email addresses
        
    Returns:
        Dict with 'toRecipients', 'ccRecipients', and 'bccRecipients' lists
    """
    recipients = {
        "toRecipients": [],
        "ccRecipients": [],
        "bccRecipients": []
    }
    
    # Add the sender of the original message as the primary recipient
    sender = original_message.get("from", {}).get("emailAddress", {})
    if sender.get("address"):
        recipients["toRecipients"].append({
            "emailAddress": {
                "address": sender["address"],
                "name": sender.get("name", sender["address"])
            }
        })
    
    # Add original CC recipients (excluding the current user)
    original_cc = original_message.get("ccRecipients", [])
    for cc_recipient in original_cc:
        email_addr = cc_recipient.get("emailAddress", {})
        if email_addr.get("address"):
            recipients["ccRecipients"].append({
                "emailAddress": {
                    "address": email_addr["address"],
                    "name": email_addr.get("name", email_addr["address"])
                }
            })
    
    # Add additional recipients to CC if provided
    if addn_recipients:
        for email in addn_recipients:
            recipients["ccRecipients"].append({
                "emailAddress": {
                    "address": email,
                    "name": email
                }
            })
    
    return recipients


def create_exchange_message(
    original_message: Dict[str, Any],
    response_text: str,
    recipients: Dict[str, List[Dict[str, str]]],
    user_email: str
) -> Dict[str, Any]:
    """Create a properly formatted Exchange message for sending.
    
    Args:
        original_message: The original message being replied to
        response_text: The reply text content
        recipients: Recipients dictionary from get_exchange_recipients
        user_email: The sender's email address
        
    Returns:
        Dict containing the formatted message for Microsoft Graph API
    """
    # Build the reply subject
    original_subject = original_message.get("subject", "")
    if not original_subject.lower().startswith("re:"):
        reply_subject = f"Re: {original_subject}"
    else:
        reply_subject = original_subject
    
    # Create message body with proper formatting
    message_body = {
        "contentType": "text",
        "content": response_text
    }
    
    # Build the message structure for Graph API
    message = {
        "subject": reply_subject,
        "body": message_body,
        "toRecipients": recipients["toRecipients"],
        "ccRecipients": recipients["ccRecipients"],
        "bccRecipients": recipients["bccRecipients"]
    }
    
    # Add reply threading headers for proper conversation threading
    conversation_id = original_message.get("conversationId")
    if conversation_id:
        # Use internetMessageHeaders to maintain threading
        message["internetMessageHeaders"] = [
            {
                "name": "In-Reply-To",
                "value": original_message.get("internetMessageId", "")
            },
            {
                "name": "References", 
                "value": original_message.get("internetMessageId", "")
            }
        ]
    
    return message


async def send_exchange_email(
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
    import requests
    
    try:
        # Get authentication credentials
        credentials = await get_exchange_credentials(
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Get original message for reply context
        original_message = _get_original_message(message_id, credentials)
        if not original_message:
            raise ValueError(f"Could not retrieve original message with ID: {message_id}")
        
        # Get recipients for the reply
        recipients = get_exchange_recipients(original_message, addn_recipients)
        
        # Create the reply message
        reply_message = create_exchange_message(
            original_message=original_message,
            response_text=response_text,
            recipients=recipients,
            user_email=user_email
        )
        
        # Send the email via Microsoft Graph API
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        graph_url = "https://graph.microsoft.com/v1.0/me/sendMail"
        
        # Retry logic for transient failures
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    graph_url,
                    headers=headers,
                    json={"message": reply_message},
                    timeout=30
                )
                
                if response.status_code == 202:  # Accepted - email queued for sending
                    logger.info(f"Email reply sent successfully for message ID: {message_id}")
                    return True
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                    import asyncio
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    error_msg = f"Failed to send email. Status: {response.status_code}, Response: {response.text}"
                    logger.error(error_msg)
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(error_msg)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    raise Exception(f"Failed to send email after {max_retries} attempts: {e}")
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
        
    except Exception as e:
        logger.error(f"Error sending Exchange email: {e}")
        raise


async def mark_exchange_as_read(
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
    import requests
    import asyncio
    
    try:
        # Validate message ID format
        if not message_id or not isinstance(message_id, str):
            raise ValueError("Invalid message ID provided")
        
        # Get authentication credentials
        credentials = await get_exchange_credentials(
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Build Graph API request
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        graph_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        
        # Payload to mark message as read
        payload = {
            "isRead": True
        }
        
        # Retry logic for transient failures
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.patch(
                    graph_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"Message {message_id} marked as read successfully")
                    return True
                elif response.status_code == 404:
                    logger.error(f"Message {message_id} not found")
                    raise ValueError(f"Message with ID {message_id} not found")
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    error_msg = f"Failed to mark message as read. Status: {response.status_code}, Response: {response.text}"
                    logger.error(error_msg)
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(error_msg)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    raise Exception(f"Failed to mark message as read after {max_retries} attempts: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
        
    except Exception as e:
        logger.error(f"Error marking Exchange message as read: {e}")
        raise


async def mark_exchange_messages_as_read_batch(
    message_ids: List[str],
    user_email: str,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> Dict[str, bool]:
    """Mark multiple Exchange emails as read using batch operations.
    
    Args:
        message_ids: List of message IDs to mark as read
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)
        
    Returns:
        Dict[str, bool]: Dictionary mapping message IDs to success status
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If API call fails
    """
    import requests
    import asyncio
    
    if not message_ids:
        return {}
    
    try:
        # Get authentication credentials
        credentials = await get_exchange_credentials(
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Build Graph API batch request
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Create batch request payload
        batch_requests = []
        for i, message_id in enumerate(message_ids):
            if not message_id or not isinstance(message_id, str):
                logger.warning(f"Skipping invalid message ID: {message_id}")
                continue
                
            batch_requests.append({
                "id": str(i),
                "method": "PATCH",
                "url": f"/me/messages/{message_id}",
                "body": {"isRead": True},
                "headers": {"Content-Type": "application/json"}
            })
        
        if not batch_requests:
            logger.warning("No valid message IDs provided for batch operation")
            return {}
        
        batch_payload = {"requests": batch_requests}
        graph_batch_url = "https://graph.microsoft.com/v1.0/$batch"
        
        # Execute batch request with retry logic
        max_retries = 3
        results = {}
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    graph_batch_url,
                    headers=headers,
                    json=batch_payload,
                    timeout=60  # Longer timeout for batch operations
                )
                
                if response.status_code == 200:
                    batch_response = response.json()
                    
                    # Process batch response
                    for i, batch_result in enumerate(batch_response.get("responses", [])):
                        request_id = int(batch_result.get("id", i))
                        if request_id < len(message_ids):
                            message_id = message_ids[request_id]
                            status_code = batch_result.get("status", 500)
                            
                            if status_code == 200:
                                results[message_id] = True
                                logger.info(f"Message {message_id} marked as read successfully")
                            elif status_code == 404:
                                results[message_id] = False
                                logger.warning(f"Message {message_id} not found")
                            else:
                                results[message_id] = False
                                logger.error(f"Failed to mark message {message_id} as read. Status: {status_code}")
                    
                    return results
                    
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Batch operation rate limited, retrying after {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    error_msg = f"Batch operation failed. Status: {response.status_code}, Response: {response.text}"
                    logger.error(error_msg)
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(error_msg)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Batch request failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    raise Exception(f"Failed to execute batch operation after {max_retries} attempts: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # If we get here, all attempts failed
        return {msg_id: False for msg_id in message_ids}
        
    except Exception as e:
        logger.error(f"Error in batch mark as read operation: {e}")
        raise


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
    import asyncio
    from .main.config import get_config
    from langchain_core.runnables.config import ensure_config
    
    try:
        # Get user email from config if not provided
        if not user_email:
            config = ensure_config()
            user_config = get_config(config)
            user_email = user_config["email"]
        
        # Run async calendar retrieval
        return asyncio.run(_fetch_exchange_calendar_events(
            date_strs=date_strs,
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        ))
        
    except Exception as e:
        logger.error(f"Error retrieving Exchange calendar events: {e}")
        raise


async def _fetch_exchange_calendar_events(
    date_strs: List[str],
    user_email: str,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> str:
    """Fetch Exchange calendar events for specified days using Microsoft Graph API.
    
    Args:
        date_strs: List of date strings in dd-mm-yyyy format
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID (optional, can be from env)
        client_id: Azure AD client ID (optional, can be from env)
        client_secret: Azure AD client secret (optional, can be from env)
        
    Returns:
        str: Formatted string containing events for the specified days
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
        Exception: If API call fails
    """
    import requests
    import asyncio
    from datetime import datetime, time
    
    try:
        # Get authentication credentials
        credentials = await get_exchange_credentials(
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        results = ""
        
        for date_str in date_strs:
            try:
                # Parse date string (dd-mm-yyyy format)
                day = datetime.strptime(date_str, "%d-%m-%Y").date()
                
                # Create start and end of day in ISO format
                start_of_day = datetime.combine(day, time.min).isoformat() + "Z"
                end_of_day = datetime.combine(day, time.max).isoformat() + "Z"
                
                # Build Graph API URL with filters
                graph_url = "https://graph.microsoft.com/v1.0/me/events"
                params = {
                    "$filter": f"start/dateTime ge '{start_of_day}' and end/dateTime le '{end_of_day}'",
                    "$orderby": "start/dateTime",
                    "$select": "subject,start,end,location,bodyPreview,isAllDay,organizer,attendees"
                }
                
                # Execute API call with retry logic
                max_retries = 3
                events = []
                
                for attempt in range(max_retries):
                    try:
                        response = requests.get(
                            graph_url,
                            headers=headers,
                            params=params,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            events_data = response.json()
                            events = events_data.get("value", [])
                            break
                            
                        elif response.status_code == 429:  # Rate limited
                            retry_after = int(response.headers.get('Retry-After', 60))
                            logger.warning(f"Calendar API rate limited, retrying after {retry_after} seconds")
                            await asyncio.sleep(retry_after)
                            continue
                            
                        else:
                            error_msg = f"Failed to retrieve calendar events. Status: {response.status_code}, Response: {response.text}"
                            logger.error(error_msg)
                            if attempt == max_retries - 1:  # Last attempt
                                raise Exception(error_msg)
                                
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Calendar request failed on attempt {attempt + 1}: {e}")
                        if attempt == max_retries - 1:  # Last attempt
                            raise Exception(f"Failed to retrieve calendar events after {max_retries} attempts: {e}")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                # Format events for this day
                results += f"***FOR DAY {date_str}***\n\n" + _format_exchange_events(events)
                
            except ValueError as e:
                logger.error(f"Invalid date format '{date_str}': {e}")
                results += f"***FOR DAY {date_str}***\n\nError: Invalid date format. Expected dd-mm-yyyy.\n\n"
                
        return results
        
    except Exception as e:
        logger.error(f"Error fetching Exchange calendar events: {e}")
        raise


def _format_exchange_events(events: List[dict]) -> str:
    """Format Exchange events to match Gmail calendar output format.
    
    Args:
        events: List of Exchange event dictionaries from Graph API
        
    Returns:
        str: Formatted events string matching Gmail format
    """
    if not events:
        return "No events found for this day.\n\n"
    
    result = ""
    
    for event in events:
        try:
            # Convert Exchange event to Gmail-compatible format
            converted_event = _convert_exchange_event(event)
            
            start = converted_event["start"].get("dateTime", converted_event["start"].get("date"))
            end = converted_event["end"].get("dateTime", converted_event["end"].get("date"))
            summary = converted_event.get("summary", "No Title")
            
            # Format datetime if it contains time information
            if "T" in start:  # Only format if it's a datetime
                start = _format_datetime_with_timezone(start)
                end = _format_datetime_with_timezone(end)
            
            result += f"Event: {summary}\n"
            result += f"Starts: {start}\n"
            result += f"Ends: {end}\n"
            result += "-" * 40 + "\n"
            
        except Exception as e:
            logger.warning(f"Error formatting event: {e}")
            # Include basic event info even if formatting fails
            subject = event.get("subject", "Unknown Event")
            result += f"Event: {subject}\n"
            result += f"Error: Could not format event details\n"
            result += "-" * 40 + "\n"
    
    return result


def _convert_exchange_event(exchange_event: dict) -> dict:
    """Convert Exchange event format to Gmail-compatible format.
    
    Args:
        exchange_event: Exchange event dictionary from Graph API
        
    Returns:
        dict: Event in Gmail-compatible format
    """
    try:
        # Map Exchange event fields to Gmail format
        converted = {
            "summary": exchange_event.get("subject", "No Title"),
            "start": {},
            "end": {}
        }
        
        # Handle start time
        start_info = exchange_event.get("start", {})
        if exchange_event.get("isAllDay", False):
            # All-day event - use date only
            start_date = start_info.get("dateTime", "").split("T")[0] if start_info.get("dateTime") else ""
            converted["start"]["date"] = start_date
        else:
            # Timed event - use dateTime
            converted["start"]["dateTime"] = start_info.get("dateTime", "")
            converted["start"]["timeZone"] = start_info.get("timeZone", "UTC")
        
        # Handle end time
        end_info = exchange_event.get("end", {})
        if exchange_event.get("isAllDay", False):
            # All-day event - use date only
            end_date = end_info.get("dateTime", "").split("T")[0] if end_info.get("dateTime") else ""
            converted["end"]["date"] = end_date
        else:
            # Timed event - use dateTime
            converted["end"]["dateTime"] = end_info.get("dateTime", "")
            converted["end"]["timeZone"] = end_info.get("timeZone", "UTC")
        
        # Add optional fields if available
        if "location" in exchange_event and exchange_event["location"]:
            converted["location"] = exchange_event["location"].get("displayName", "")
        
        if "bodyPreview" in exchange_event:
            converted["description"] = exchange_event["bodyPreview"]
        
        return converted
        
    except Exception as e:
        logger.error(f"Error converting Exchange event: {e}")
        # Return minimal event structure
        return {
            "summary": exchange_event.get("subject", "Unknown Event"),
            "start": {"dateTime": exchange_event.get("start", {}).get("dateTime", "")},
            "end": {"dateTime": exchange_event.get("end", {}).get("dateTime", "")}
        }


def _format_datetime_with_timezone(dt_str: str, timezone: str = "US/Pacific") -> str:
    """Format a datetime string with the specified timezone.
    
    Args:
        dt_str: The datetime string to format
        timezone: The timezone to use for formatting (default: US/Pacific)
        
    Returns:
        str: Formatted datetime string with timezone abbreviation
    """
    try:
        import pytz
        from datetime import datetime
        
        # Parse the datetime string
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        
        # Convert to specified timezone
        tz = pytz.timezone(timezone)
        dt = dt.astimezone(tz)
        
        # Format as expected by Gmail format
        return dt.strftime("%Y-%m-%d %I:%M %p %Z")
        
    except Exception as e:
        logger.warning(f"Error formatting datetime '{dt_str}': {e}")
        # Return original string if formatting fails
        return dt_str


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
