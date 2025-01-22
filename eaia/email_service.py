"""
Email Service Module

This module provides a unified interface for email and calendar operations. It currently wraps the Gmail
implementation but is designed to be extensible for supporting multiple email service providers in the future
(e.g., Microsoft Graph API).

The module handles:
1. Email Operations:
   - Fetching unread emails
   - Marking emails as read
   - Sending emails and replies
2. Calendar Operations:
   - Fetching calendar events
   - Sending calendar invites

All functions accept optional Gmail credentials which can be provided either via parameters or retrieved
from the system keyring if not specified.
"""

import logging
from datetime import datetime
from typing import Iterable, List, Optional, Dict

from zen_email_service.reader import GmailAPIEmailReader, GraphAPIEmailReader
from eaia.schemas import EmailData
from eaia.gmail import (
    mark_as_read as gmail_mark_as_read,
    get_events_for_days as gmail_get_events,
    send_calendar_invite as gmail_send_calendar_invite,
    send_email as gmail_send_email,
)

logger = logging.getLogger(__name__)

def fetch_group_emails(
    to_email: str,
    minutes_since: int = 30,
    service: str = "gmail",
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
) -> Iterable[EmailData]:
    """
    Fetch unread emails from a group email address within a specified time window.

    Args:
        to_email: The email address to fetch messages for
        minutes_since: Only fetch emails from the last N minutes
        service: Email service to use ("gmail" or "ms"). Defaults to "gmail"
        gmail_token: Optional Gmail API token. If not provided, will attempt to fetch from keyring
        gmail_secret: Optional Gmail API secret. If not provided, will attempt to fetch from keyring

    Returns:
        An iterable of EmailData objects containing the email messages

    Raises:
        ValueError: If credentials cannot be found in keyring when not provided as parameters
                   or if an invalid service is specified
    """
    if service not in ["gmail", "ms"]:
        raise ValueError('service must be either "gmail" or "ms"')
        
    if service == "gmail":
        reader = GmailAPIEmailReader()
    else:
        reader = GraphAPIEmailReader()
        
    zen_emails = reader.fetch_emails(
        minutes_since=minutes_since,
        include_read=False,
        all_folders=False,
        use_tqdm=False
    )
    
    # Convert zen_email_service.EmailData to schemas.EmailData
    for email in zen_emails:
        yield EmailData(
            id=email.id,
            thread_id=email.thread_id,
            from_email=email.sender,
            subject=email.subject,
            page_content=email.body,
            send_time=email.received_date,
            to_email=email.recipients[0] if email.recipients else to_email
        )

def mark_as_read(
    message_id: str,
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
) -> None:
    """
    Mark an email message as read.

    Args:
        message_id: The ID of the message to mark as read
        gmail_token: Optional Gmail API token. If not provided, will attempt to fetch from keyring
        gmail_secret: Optional Gmail API secret. If not provided, will attempt to fetch from keyring

    Raises:
        ValueError: If credentials cannot be found in keyring when not provided as parameters
    """
    gmail_mark_as_read(
        message_id,
        gmail_token=gmail_token,
        gmail_secret=gmail_secret,
    )

def get_events_for_days(
    date_strs: List[str],
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
) -> List[Dict]:
    """
    Retrieve calendar events for specified dates.

    Args:
        date_strs: List of date strings in YYYY-MM-DD format
        gmail_token: Optional Gmail API token. If not provided, will attempt to fetch from keyring
        gmail_secret: Optional Gmail API secret. If not provided, will attempt to fetch from keyring

    Returns:
        List of calendar event dictionaries containing event details

    Raises:
        ValueError: If credentials cannot be found in keyring when not provided as parameters
    """
    return gmail_get_events(
        date_strs,
        gmail_token=gmail_token,
        gmail_secret=gmail_secret,
    )

def send_calendar_invite(
    emails: List[str],
    title: str,
    start_time: str,
    end_time: str,
    email_address: str,
    timezone: str = "PST",
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
) -> None:
    """
    Send a calendar invitation to specified email addresses.

    Args:
        emails: List of email addresses to send the invite to
        title: Title/subject of the calendar event
        start_time: Start time of the event (ISO format)
        end_time: End time of the event (ISO format)
        email_address: The sender's email address
        timezone: Timezone for the event (default: "PST")
        gmail_token: Optional Gmail API token. If not provided, will attempt to fetch from keyring
        gmail_secret: Optional Gmail API secret. If not provided, will attempt to fetch from keyring

    Raises:
        ValueError: If credentials cannot be found in keyring when not provided as parameters
    """
    gmail_send_calendar_invite(
        emails,
        title,
        start_time,
        end_time,
        email_address,
        timezone=timezone,
        gmail_token=gmail_token,
        gmail_secret=gmail_secret,
    )

def send_email(
    email_id: str,
    response_text: str,
    email_address: str,
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
    addn_receipients: Optional[List[str]] = None,
) -> None:
    """
    Send an email response.

    Args:
        email_id: ID of the email being responded to
        response_text: Content of the email response
        email_address: The sender's email address
        gmail_token: Optional Gmail API token. If not provided, will attempt to fetch from keyring
        gmail_secret: Optional Gmail API secret. If not provided, will attempt to fetch from keyring
        addn_receipients: Optional list of additional recipients

    Raises:
        ValueError: If credentials cannot be found in keyring when not provided as parameters
    """
    gmail_send_email(
        email_id,
        response_text,
        email_address,
        gmail_token=gmail_token,
        gmail_secret=gmail_secret,
        addn_receipients=addn_receipients,
    )
