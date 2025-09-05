"""
Email Provider Interface Design for EAIA.

This module provides a unified interface for email providers (Gmail and Exchange),
enabling seamless provider switching and consistent functionality across different
email systems.
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, List, Optional, Any, Dict

from eaia.schemas import EmailData

logger = logging.getLogger(__name__)


class EmailProvider(Enum):
    """Enumeration of supported email providers."""
    GMAIL = "gmail"
    EXCHANGE = "exchange"
    
    @classmethod
    def from_string(cls, provider_str: str) -> "EmailProvider":
        """Create EmailProvider from string value."""
        provider_str = provider_str.lower().strip()
        for provider in cls:
            if provider.value == provider_str:
                return provider
        raise ValueError(f"Invalid provider type: {provider_str}. Must be one of: {[p.value for p in cls]}")


class EmailInterface(ABC):
    """Abstract base class defining the email provider interface.
    
    This interface ensures consistent functionality across different email providers
    while allowing for provider-specific implementations and configurations.
    """

    @abstractmethod
    async def fetch_emails(
        self, 
        user_email: str, 
        minutes_since: int = 30,
        **kwargs: Any
    ) -> Iterable[EmailData]:
        """Fetch emails from the provider.
        
        Args:
            user_email: User's email address
            minutes_since: Number of minutes to look back for emails
            **kwargs: Provider-specific additional parameters
            
        Returns:
            Iterable of EmailData objects
            
        Raises:
            Exception: If email fetching fails
        """
        pass

    @abstractmethod
    async def send_email(
        self, 
        message_id: str, 
        response_text: str, 
        user_email: str,
        addn_recipients: Optional[List[str]] = None,
        **kwargs: Any
    ) -> bool:
        """Send an email reply.
        
        Args:
            message_id: ID of the message to reply to
            response_text: Content of the reply
            user_email: User's email address
            addn_recipients: Additional recipients for the reply
            **kwargs: Provider-specific additional parameters
            
        Returns:
            bool: True if email was sent successfully, False otherwise
            
        Raises:
            Exception: If email sending fails
        """
        pass

    @abstractmethod
    async def mark_as_read(
        self, 
        message_id: str, 
        user_email: str,
        **kwargs: Any
    ) -> bool:
        """Mark an email as read.
        
        Args:
            message_id: ID of the message to mark as read
            user_email: User's email address
            **kwargs: Provider-specific additional parameters
            
        Returns:
            bool: True if message was marked as read successfully, False otherwise
            
        Raises:
            Exception: If marking as read fails
        """
        pass

    @abstractmethod
    def get_events_for_days(
        self, 
        date_strs: List[str], 
        user_email: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Get calendar events for specified days.
        
        Args:
            date_strs: List of date strings in dd-mm-yyyy format
            user_email: User's email address (optional, can be from config)
            **kwargs: Provider-specific additional parameters
            
        Returns:
            str: Formatted string of calendar events
            
        Raises:
            Exception: If calendar event retrieval fails
        """
        pass

    @abstractmethod
    def send_calendar_invite(
        self, 
        emails: List[str], 
        title: str, 
        start_time: str, 
        end_time: str, 
        user_email: str,
        timezone: str = "UTC",
        **kwargs: Any
    ) -> bool:
        """Send a calendar invite.
        
        Args:
            emails: List of email addresses to invite
            title: Meeting title/subject
            start_time: Meeting start time in ISO format
            end_time: Meeting end time in ISO format
            user_email: User's email address
            timezone: Timezone for the meeting
            **kwargs: Provider-specific additional parameters
            
        Returns:
            bool: True if calendar invite was sent successfully, False otherwise
            
        Raises:
            Exception: If calendar invite sending fails
        """
        pass

    @abstractmethod
    def get_provider_type(self) -> EmailProvider:
        """Get the provider type.
        
        Returns:
            EmailProvider: The type of this provider
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate provider-specific configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Raises:
            Exception: If configuration validation fails
        """
        pass


class EmailProviderFactory:
    """Factory class for creating email provider instances.
    
    This factory handles provider instantiation based on configuration
    and provides validation for provider-specific requirements.
    """

    @staticmethod
    def create_provider(
        provider_type: EmailProvider,
        config: Optional[Dict[str, Any]] = None
    ) -> EmailInterface:
        """Create an email provider instance.
        
        Args:
            provider_type: Type of provider to create
            config: Provider-specific configuration dictionary
            
        Returns:
            EmailInterface: Instance of the requested provider
            
        Raises:
            ValueError: If provider type is not supported
            Exception: If provider creation fails
        """
        if provider_type == EmailProvider.GMAIL:
            from eaia.email_provider import GmailProvider
            return GmailProvider(config or {})
        elif provider_type == EmailProvider.EXCHANGE:
            from eaia.email_provider import ExchangeProvider
            return ExchangeProvider(config or {})
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    @staticmethod
    def get_provider_from_config(config: Dict[str, Any]) -> EmailInterface:
        """Create provider instance from configuration dictionary.
        
        Args:
            config: Configuration dictionary containing provider_type and provider-specific config
            
        Returns:
            EmailInterface: Configured provider instance
            
        Raises:
            ValueError: If provider_type is missing or invalid
        """
        provider_type = config.get("provider_type")
        if not provider_type:
            raise ValueError("Missing 'provider_type' in configuration")
        
        try:
            provider_enum = EmailProvider.from_string(provider_type)
        except ValueError as e:
            raise ValueError(f"Invalid provider_type in configuration: {e}")
        
        return EmailProviderFactory.create_provider(provider_enum, config)
    
    @staticmethod
    def validate_config(provider_type: EmailProvider, config: Dict[str, Any]) -> bool:
        """Validate configuration for a specific provider type.
        
        Args:
            provider_type: EmailProvider enum value
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if provider_type == EmailProvider.GMAIL:
            required_keys = ["gmail_secret", "gmail_token"]
        elif provider_type == EmailProvider.EXCHANGE:
            required_keys = ["tenant_id", "client_id", "client_secret"]
        else:
            return False
        
        return all(key in config and config[key] for key in required_keys)



class GmailProvider(EmailInterface):
    """Gmail implementation of the EmailInterface.
    
    This class wraps existing Gmail functionality to provide a consistent
    interface while maintaining backward compatibility.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize Gmail provider.
        
        Args:
            config: Gmail-specific configuration dictionary
        """
        self.config = config
        logger.info("Gmail provider initialized")

    async def fetch_emails(
        self, 
        user_email: str, 
        minutes_since: int = 30,
        **kwargs: Any
    ) -> Iterable[EmailData]:
        """Fetch emails using Gmail API."""
        from eaia.gmail import fetch_group_emails
        
        gmail_secret = kwargs.get("gmail_secret", self.config.get("gmail_secret"))
        gmail_token = kwargs.get("gmail_token", self.config.get("gmail_token"))
        
        return await fetch_group_emails(
            to_email=user_email,
            minutes_since=minutes_since,
            gmail_token=gmail_token,
            gmail_secret=gmail_secret
        )

    async def send_email(
        self, 
        message_id: str, 
        response_text: str, 
        user_email: str,
        addn_recipients: Optional[List[str]] = None,
        **kwargs: Any
    ) -> bool:
        """Send email using Gmail API."""
        from eaia.gmail import send_email
        
        gmail_secret = kwargs.get("gmail_secret", self.config.get("gmail_secret"))
        gmail_token = kwargs.get("gmail_token", self.config.get("gmail_token"))
        
        # Gmail send_email function doesn't return bool, so we wrap it
        try:
            send_email(
                email_id=message_id,
                response_text=response_text,
                email_address=user_email,
                gmail_token=gmail_token,
                gmail_secret=gmail_secret
            )
            return True
        except Exception:
            return False

    async def mark_as_read(
        self, 
        message_id: str, 
        user_email: str,
        **kwargs: Any
    ) -> bool:
        """Mark email as read using Gmail API."""
        from eaia.gmail import mark_as_read
        
        gmail_secret = kwargs.get("gmail_secret", self.config.get("gmail_secret"))
        gmail_token = kwargs.get("gmail_token", self.config.get("gmail_token"))
        
        # Gmail mark_as_read function doesn't return bool, so we wrap it
        try:
            mark_as_read(
                message_id=message_id,
                user_email=user_email,
                gmail_token=gmail_token,
                gmail_secret=gmail_secret
            )
            return True
        except Exception:
            return False

    def get_events_for_days(
        self, 
        date_strs: List[str], 
        user_email: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Get calendar events using Gmail/Google Calendar API."""
        from eaia.gmail import get_events_for_days
        
        gmail_secret = kwargs.get("gmail_secret", self.config.get("gmail_secret"))
        gmail_token = kwargs.get("gmail_token", self.config.get("gmail_token"))
        
        return get_events_for_days(
            date_strs=date_strs,
            user_email=user_email,
            gmail_secret=gmail_secret,
            gmail_token=gmail_token
        )

    def send_calendar_invite(
        self, 
        emails: List[str], 
        title: str, 
        start_time: str, 
        end_time: str, 
        user_email: str,
        timezone: str = "UTC",
        **kwargs: Any
    ) -> bool:
        """Send calendar invite using Google Calendar API."""
        from eaia.gmail import send_calendar_invite
        
        gmail_secret = kwargs.get("gmail_secret", self.config.get("gmail_secret"))
        gmail_token = kwargs.get("gmail_token", self.config.get("gmail_token"))
        
        return send_calendar_invite(
            emails=emails,
            title=title,
            start_time=start_time,
            end_time=end_time,
            email_address=user_email,
            timezone=timezone,
            gmail_secret=gmail_secret,
            gmail_token=gmail_token
        )

    def get_provider_type(self) -> EmailProvider:
        """Get the provider type."""
        return EmailProvider.GMAIL

    def validate_configuration(self) -> bool:
        """Validate Gmail configuration."""
        required_keys = ["gmail_secret", "gmail_token"]
        return all(key in self.config for key in required_keys)


class ExchangeProvider(EmailInterface):
    """Exchange implementation of the EmailInterface.
    
    This class wraps Exchange functionality from previous stages to provide
    a consistent interface with Gmail provider.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize Exchange provider.
        
        Args:
            config: Exchange-specific configuration dictionary
        """
        self.config = config
        logger.info("Exchange provider initialized")

    async def fetch_emails(
        self, 
        user_email: str, 
        minutes_since: int = 30,
        **kwargs: Any
    ) -> Iterable[EmailData]:
        """Fetch emails using Microsoft Graph API."""
        from eaia.exchange import fetch_exchange_emails
        
        tenant_id = kwargs.get("tenant_id", self.config.get("tenant_id"))
        client_id = kwargs.get("client_id", self.config.get("client_id"))
        client_secret = kwargs.get("client_secret", self.config.get("client_secret"))
        
        return await fetch_exchange_emails(
            user_email=user_email,
            minutes_since=minutes_since,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    async def send_email(
        self, 
        message_id: str, 
        response_text: str, 
        user_email: str,
        addn_recipients: Optional[List[str]] = None,
        **kwargs: Any
    ) -> bool:
        """Send email using Microsoft Graph API."""
        from eaia.exchange import send_exchange_email
        
        tenant_id = kwargs.get("tenant_id", self.config.get("tenant_id"))
        client_id = kwargs.get("client_id", self.config.get("client_id"))
        client_secret = kwargs.get("client_secret", self.config.get("client_secret"))
        
        return await send_exchange_email(
            message_id=message_id,
            response_text=response_text,
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            addn_recipients=addn_recipients,
            **kwargs
        )

    async def mark_as_read(
        self, 
        message_id: str, 
        user_email: str,
        **kwargs: Any
    ) -> bool:
        """Mark email as read using Microsoft Graph API."""
        from eaia.exchange import mark_exchange_as_read
        
        tenant_id = kwargs.get("tenant_id", self.config.get("tenant_id"))
        client_id = kwargs.get("client_id", self.config.get("client_id"))
        client_secret = kwargs.get("client_secret", self.config.get("client_secret"))
        
        return await mark_exchange_as_read(
            message_id=message_id,
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    def get_events_for_days(
        self, 
        date_strs: List[str], 
        user_email: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Get calendar events using Microsoft Graph API."""
        from eaia.exchange import get_exchange_events_for_days
        
        tenant_id = kwargs.get("tenant_id", self.config.get("tenant_id"))
        client_id = kwargs.get("client_id", self.config.get("client_id"))
        client_secret = kwargs.get("client_secret", self.config.get("client_secret"))
        
        return get_exchange_events_for_days(
            date_strs=date_strs,
            user_email=user_email,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    def send_calendar_invite(
        self, 
        emails: List[str], 
        title: str, 
        start_time: str, 
        end_time: str, 
        user_email: str,
        timezone: str = "UTC",
        **kwargs: Any
    ) -> bool:
        """Send calendar invite using Microsoft Graph API."""
        from eaia.exchange import send_exchange_calendar_invite
        
        tenant_id = kwargs.get("tenant_id", self.config.get("tenant_id"))
        client_id = kwargs.get("client_id", self.config.get("client_id"))
        client_secret = kwargs.get("client_secret", self.config.get("client_secret"))
        
        return send_exchange_calendar_invite(
            emails=emails,
            title=title,
            start_time=start_time,
            end_time=end_time,
            user_email=user_email,
            timezone=timezone,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    def get_provider_type(self) -> EmailProvider:
        """Get the provider type."""
        return EmailProvider.EXCHANGE

    def validate_configuration(self) -> bool:
        """Validate Exchange configuration."""
        required_keys = ["tenant_id", "client_id", "client_secret"]
        return all(key in self.config for key in required_keys)
