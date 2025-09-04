# Exchange Support Specification

## Overview

This specification outlines the implementation plan for adding Microsoft Exchange support to the Executive AI Assistant (EAIA) project. The current implementation supports Gmail through Google APIs, and we need to extend this to support Exchange through Microsoft Graph API while maintaining the same interface and functionality.

## Current Gmail Implementation Analysis

### Architecture Overview
The current Gmail implementation consists of:

1. **Authentication**: Uses `langchain_auth.Client` with Google OAuth2 for authentication
2. **Core Module**: `eaia/gmail.py` - Contains all Gmail-specific functionality
3. **Schemas**: `eaia/schemas.py` - Defines `EmailData` and related data structures
4. **Integration**: Integrated into LangGraph workflow via `eaia/main/graph.py`

### Key Functions in Gmail Implementation

#### Authentication
- `get_credentials(user_email, langsmith_api_key)` - OAuth2 authentication with Google
- Uses scopes: `gmail.modify` and `calendar`

#### Email Operations
- `fetch_group_emails()` - Retrieves emails from Gmail
- `send_email()` - Sends email responses
- `mark_as_read()` - Marks emails as read
- `extract_message_part()` - Parses email content from Gmail API format

#### Calendar Operations
- `get_events_for_days()` - Retrieves calendar events
- `send_calendar_invite()` - Creates and sends calendar invitations

### Data Flow
1. Email fetching → `EmailData` schema → LangGraph processing
2. Response generation → Email sending via Gmail API
3. Calendar integration for meeting scheduling

## Exchange Support Requirements

### Microsoft Graph API Integration

#### Required Dependencies
Add to `pyproject.toml`:
```toml
"msal>=1.24.0",           # Microsoft Authentication Library
"msgraph-core>=0.2.2",   # Microsoft Graph Core SDK
"requests>=2.31.0",      # HTTP requests (if not already present)
```

#### Authentication Requirements
- **App Registration**: Requires Azure AD app registration
- **Permissions**: Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, User.Read
- **Authentication Flow**: OAuth2 with MSAL (Microsoft Authentication Library)
- **Scopes**: `https://graph.microsoft.com/Mail.ReadWrite`, `https://graph.microsoft.com/Calendars.ReadWrite`

### Implementation Plan

#### Phase 1: Core Exchange Module (`eaia/exchange.py`)

Create a new module that mirrors the Gmail implementation structure:

```python
# Key functions to implement:
async def get_exchange_credentials(user_email: str, tenant_id: str, client_id: str, client_secret: str)
async def fetch_exchange_emails(user_email: str, minutes_since: int = 30)
def send_exchange_email(message_id: str, response_text: str, user_email: str, ...)
def mark_exchange_as_read(message_id: str, user_email: str, ...)
def get_exchange_events_for_days(date_strs: list[str], user_email: str, ...)
def send_exchange_calendar_invite(emails: list, title: str, start_time: str, end_time: str, ...)
```

#### Phase 2: Unified Email Interface

Create an abstraction layer to handle both Gmail and Exchange:

```python
# eaia/email_provider.py
from abc import ABC, abstractmethod
from enum import Enum

class EmailProvider(Enum):
    GMAIL = "gmail"
    EXCHANGE = "exchange"

class EmailInterface(ABC):
    @abstractmethod
    async def fetch_emails(self, user_email: str, minutes_since: int) -> Iterable[EmailData]
    
    @abstractmethod
    def send_email(self, email_id: str, response_text: str, user_email: str, **kwargs)
    
    @abstractmethod
    def mark_as_read(self, message_id: str, user_email: str)
    
    # ... other abstract methods
```

#### Phase 3: Configuration Updates

Update configuration system to support provider selection:

```yaml
# config.yaml additions
email_provider: "gmail"  # or "exchange"
exchange_config:
  tenant_id: "${EXCHANGE_TENANT_ID}"
  client_id: "${EXCHANGE_CLIENT_ID}"
  client_secret: "${EXCHANGE_CLIENT_SECRET}"
```

#### Phase 4: Schema Extensions

Extend existing schemas to handle Exchange-specific data:

```python
# eaia/schemas.py additions
class ExchangeEmailData(EmailData):
    # Exchange-specific fields if needed
    conversation_id: str  # Exchange conversation threading
    importance: str       # High/Normal/Low
    
class EmailProviderConfig(BaseModel):
    provider: EmailProvider
    gmail_config: Optional[dict] = None
    exchange_config: Optional[dict] = None
```

### Microsoft Graph API Mapping

#### Email Operations Mapping

| Gmail API | Microsoft Graph API | Notes |
|-----------|-------------------|-------|
| `messages().list()` | `GET /me/messages` | Query parameters differ |
| `messages().get()` | `GET /me/messages/{id}` | Response format differs |
| `messages().send()` | `POST /me/sendMail` | Request body format differs |
| `messages().modify()` | `PATCH /me/messages/{id}` | Different property names |

#### Calendar Operations Mapping

| Gmail API | Microsoft Graph API | Notes |
|-----------|-------------------|-------|
| `events().list()` | `GET /me/events` | Similar functionality |
| `events().insert()` | `POST /me/events` | Different request format |

### Data Format Conversion

#### Email Message Conversion
Exchange messages need conversion to match `EmailData` schema:

```python
def convert_exchange_message_to_email_data(exchange_msg: dict) -> EmailData:
    return {
        "id": exchange_msg["id"],
        "thread_id": exchange_msg["conversationId"],
        "from_email": exchange_msg["from"]["emailAddress"]["address"],
        "to_email": exchange_msg["toRecipients"][0]["emailAddress"]["address"],
        "subject": exchange_msg["subject"],
        "page_content": exchange_msg["body"]["content"],
        "send_time": exchange_msg["receivedDateTime"],
    }
```

### Authentication Flow

#### Exchange Authentication Process
1. **App Registration**: Register app in Azure AD
2. **Consent**: Admin or user consent for required permissions
3. **Token Acquisition**: Use MSAL to get access tokens
4. **Token Refresh**: Handle token refresh automatically

```python
# Pseudo-code for Exchange authentication
async def get_exchange_credentials(tenant_id: str, client_id: str, client_secret: str):
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=f"https://login.microsoftonline.com/{tenant_id}"
    )
    
    # Implement OAuth2 flow similar to Gmail
    # Return credentials object compatible with existing interface
```

### Integration Points

#### LangGraph Integration
- Modify `eaia/main/graph.py` to use provider-agnostic email interface
- Update node functions to work with both providers
- Maintain existing workflow logic

#### Configuration Integration
- Extend `eaia/main/config.py` to handle provider selection
- Add validation for provider-specific configuration
- Maintain backward compatibility with existing Gmail configs

### Error Handling and Resilience

#### Exchange-Specific Error Handling
- **Rate Limiting**: Microsoft Graph has different rate limits than Gmail
- **Authentication Errors**: Handle Azure AD authentication failures
- **API Differences**: Handle different error response formats
- **Tenant-Specific Issues**: Handle multi-tenant scenarios

### Testing Strategy

#### Unit Tests
- Test Exchange API integration separately
- Test email format conversion functions
- Test authentication flow (with mocking)

#### Integration Tests
- Test end-to-end email processing with Exchange
- Test calendar integration with Exchange
- Test provider switching functionality

#### Compatibility Tests
- Ensure Gmail functionality remains unchanged
- Test configuration migration scenarios

### Security Considerations

#### Exchange Security Requirements
- **Client Secret Management**: Secure storage of Azure AD client secrets
- **Token Storage**: Secure token caching and refresh
- **Permissions**: Principle of least privilege for Graph API permissions
- **Multi-Tenant**: Consider tenant isolation if supporting multiple organizations

### Deployment Considerations

#### Environment Variables
```bash
# New environment variables for Exchange
EXCHANGE_TENANT_ID=your-tenant-id
EXCHANGE_CLIENT_ID=your-client-id
EXCHANGE_CLIENT_SECRET=your-client-secret
EMAIL_PROVIDER=exchange  # or gmail
```

#### Migration Path
1. **Phase 1**: Deploy with Gmail as default, Exchange as opt-in
2. **Phase 2**: Allow runtime provider switching
3. **Phase 3**: Support multiple providers per user (if needed)

### Performance Considerations

#### API Rate Limits
- **Gmail**: 1 billion quota units per day
- **Exchange**: 10,000 requests per 10 minutes per app per tenant
- Implement appropriate throttling and retry logic

#### Caching Strategy
- Cache Exchange tokens appropriately
- Consider caching email metadata for performance
- Implement efficient pagination for large mailboxes

### Documentation Requirements

#### User Documentation
- Setup guide for Azure AD app registration
- Configuration examples for Exchange
- Migration guide from Gmail to Exchange

#### Developer Documentation
- API mapping documentation
- Extension points for additional providers
- Troubleshooting guide for common Exchange issues

## Implementation Timeline

### Phase 1 (Week 1-2): Foundation
- [ ] Create `eaia/exchange.py` module
- [ ] Implement basic authentication with MSAL
- [ ] Add required dependencies to `pyproject.toml`

### Phase 2 (Week 2-3): Core Functionality
- [ ] Implement email fetching from Exchange
- [ ] Implement email sending via Exchange
- [ ] Implement calendar operations for Exchange

### Phase 3 (Week 3-4): Integration
- [ ] Create unified email interface
- [ ] Update configuration system
- [ ] Integrate with existing LangGraph workflow

### Phase 4 (Week 4-5): Testing and Polish
- [ ] Comprehensive testing suite
- [ ] Error handling and resilience
- [ ] Documentation and examples

### Phase 5 (Week 5-6): Deployment
- [ ] Production deployment preparation
- [ ] Migration tools and documentation
- [ ] Performance optimization

## Success Criteria

1. **Functional Parity**: Exchange implementation provides same functionality as Gmail
2. **Seamless Integration**: Existing workflows work unchanged with Exchange
3. **Configuration Flexibility**: Easy switching between providers
4. **Performance**: Exchange operations perform comparably to Gmail
5. **Security**: Proper handling of Exchange authentication and permissions
6. **Documentation**: Complete setup and usage documentation
7. **Testing**: Comprehensive test coverage for Exchange functionality

## Risks and Mitigations

### Technical Risks
- **API Differences**: Microsoft Graph API may have limitations not present in Gmail API
  - *Mitigation*: Thorough API analysis and feature mapping
- **Authentication Complexity**: Azure AD authentication more complex than Google OAuth
  - *Mitigation*: Use proven MSAL library and follow Microsoft best practices

### Business Risks
- **Maintenance Overhead**: Supporting two providers increases complexity
  - *Mitigation*: Good abstraction layer and comprehensive testing
- **Feature Divergence**: Providers may have different capabilities
  - *Mitigation*: Define common feature set and document limitations

## Future Considerations

### Additional Providers
- Design allows for adding other email providers (Outlook.com, Yahoo, etc.)
- Consider standardizing on a common email protocol abstraction

### Advanced Features
- **Hybrid Scenarios**: Users with both Gmail and Exchange accounts
- **Provider-Specific Features**: Leverage unique capabilities of each provider
- **Real-time Notifications**: Webhook support for both providers
