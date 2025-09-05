from typing import Annotated, List, Literal, Optional
from langgraph.graph.message import AnyMessage
from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict
from enum import Enum

from langgraph.graph import add_messages


class EmailData(TypedDict):
    id: str
    thread_id: str
    from_email: str
    subject: str
    page_content: str
    send_time: str
    to_email: str


class RespondTo(BaseModel):
    logic: str = Field(
        description="logic on WHY the response choice is the way it is", default=""
    )
    response: Literal["no", "email", "notify", "question"] = "no"


class ResponseEmailDraft(BaseModel):
    """Draft of an email to send as a response."""

    content: str
    new_recipients: List[str]


class NewEmailDraft(BaseModel):
    """Draft of a new email to send."""

    content: str
    recipients: List[str]


class ReWriteEmail(BaseModel):
    """Logic for rewriting an email"""

    tone_logic: str = Field(
        description="Logic for what the tone of the rewritten email should be"
    )
    rewritten_content: str = Field(description="Content rewritten with the new tone")


class Question(BaseModel):
    """Question to ask user."""

    content: str


class Ignore(BaseModel):
    """Call this to ignore the email. Only call this if user has said to do so."""

    ignore: bool


class MeetingAssistant(BaseModel):
    """Call this to have user's meeting assistant look at it."""

    call: bool


class SendCalendarInvite(BaseModel):
    """Call this to send a calendar invite."""

    emails: List[str] = Field(
        description="List of emails to send the calendar invitation for. Do NOT make any emails up!"
    )
    title: str = Field(description="Name of the meeting")
    start_time: str = Field(
        description="Start time for the meeting, should be in `2024-07-01T14:00:00` format"
    )
    end_time: str = Field(
        description="End time for the meeting, should be in `2024-07-01T14:00:00` format"
    )


class EmailProviderType(str, Enum):
    """Enumeration of supported email providers."""
    GMAIL = "gmail"
    EXCHANGE = "exchange"


class ExchangeConfig(BaseModel):
    """Configuration for Exchange email provider."""
    tenant_id: str = Field(description="Azure AD tenant ID")
    client_id: str = Field(description="Azure AD application client ID")
    client_secret: str = Field(description="Azure AD application client secret")
    
    @field_validator('tenant_id', 'client_id', 'client_secret')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Exchange configuration values cannot be empty")
        return v.strip()


class GmailConfig(BaseModel):
    """Configuration for Gmail email provider."""
    gmail_secret: Optional[str] = Field(default=None, description="Gmail API secret")
    gmail_token: Optional[str] = Field(default=None, description="Gmail API token")
    
    @field_validator('gmail_secret', 'gmail_token')
    @classmethod
    def validate_gmail_config(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Gmail configuration values cannot be empty")
        return v.strip() if v else v


class EmailProviderConfig(BaseModel):
    """Configuration for email provider selection and settings."""
    provider: EmailProviderType = Field(default=EmailProviderType.GMAIL, description="Email provider to use")
    gmail_config: Optional[GmailConfig] = Field(default=None, description="Gmail-specific configuration")
    exchange_config: Optional[ExchangeConfig] = Field(default=None, description="Exchange-specific configuration")
    
    @field_validator('gmail_config')
    @classmethod
    def validate_gmail_config_when_provider_gmail(cls, v, info):
        # Allow None for backward compatibility - will use legacy config loading
        return v
    
    @field_validator('exchange_config')
    @classmethod
    def validate_exchange_config_when_provider_exchange(cls, v, info):
        if hasattr(info, 'data') and info.data.get('provider') == EmailProviderType.EXCHANGE and v is None:
            raise ValueError("Exchange configuration is required when provider is 'exchange'")
        return v


# Needed to mix Pydantic with TypedDict
def convert_obj(o, m):
    if isinstance(m, dict):
        return RespondTo(**m)
    else:
        return m


class State(TypedDict):
    email: EmailData
    triage: Annotated[RespondTo, convert_obj]
    messages: Annotated[List[AnyMessage], add_messages]


email_template = """From: {author}
To: {to}
Subject: {subject}

{email_thread}"""
