"""
Microsoft Exchange integration module for EAIA.

This module provides Exchange/Outlook email and calendar functionality
using Microsoft Graph API, designed to match the Gmail module interface.
"""

import logging
from datetime import datetime, timedelta, time
from typing import Iterable, List, Optional, Any
import os

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from eaia.schemas import EmailData

logger = logging.getLogger(__name__)

# Microsoft Graph API scopes required for email and calendar access
_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send", 
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/User.Read",
]


async def get_exchange_credentials(
    user_email: str,
    tenant_id: str,
    client_id: str,
    client_secret: str
) -> dict:
    """Get Microsoft Graph API credentials using MSAL.
    
    Args:
        user_email: User's Exchange email address
        tenant_id: Azure AD tenant ID
        client_id: Azure AD application client ID
        client_secret: Azure AD application client secret
        
    Returns:
        Dictionary containing access token and related auth info
        
    Raises:
        ValueError: If authentication fails or required parameters are missing
    """
    # TODO: Implement MSAL authentication flow
    # This will be implemented in Stage 2
    raise NotImplementedError("Exchange authentication will be implemented in Stage 2")


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
    # TODO: Implement Exchange email fetching using Microsoft Graph API
    # This will be implemented in Stage 3
    raise NotImplementedError("Exchange email fetching will be implemented in Stage 3")


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
