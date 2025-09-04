# Stage 8: Email Provider Interface Design

**Estimated Time:** 2-3 hours  
**Prerequisites:** Stage 7 completed  
**Dependencies:** Stage 7  

## Objective
Create a unified email provider interface that abstracts Gmail and Exchange implementations, enabling seamless provider switching.

## Tasks

### 8.1 Abstract Base Interface Design (60 minutes)
- Create `eaia/email_provider.py` with abstract base class
- Define `EmailInterface` with all required methods
- Create `EmailProvider` enum for provider types
- Ensure interface covers all existing functionality

**Key interface definition:**
```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable

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
    
    @abstractmethod
    def get_events_for_days(self, date_strs: list[str], user_email: str)
    
    @abstractmethod
    def send_calendar_invite(self, emails: list, title: str, start_time: str, end_time: str, user_email: str, **kwargs)
```

### 8.2 Gmail Provider Implementation (45 minutes)
- Create `GmailProvider` class implementing `EmailInterface`
- Wrap existing Gmail functions in the interface
- Ensure no breaking changes to existing functionality
- Add proper error handling and logging

### 8.3 Exchange Provider Implementation (45 minutes)
- Create `ExchangeProvider` class implementing `EmailInterface`
- Wrap Exchange functions from previous stages
- Ensure consistent error handling across providers
- Add provider-specific configuration handling

### 8.4 Provider Factory Pattern (30 minutes)
- Create `EmailProviderFactory` class
- Implement provider instantiation based on configuration
- Add validation for provider-specific requirements
- Handle provider switching logic

## Acceptance Criteria
- [ ] `EmailInterface` abstract base class defined with all methods
- [ ] `GmailProvider` implements interface without breaking existing functionality
- [ ] `ExchangeProvider` implements interface with all Exchange functions
- [ ] `EmailProviderFactory` can create providers based on configuration
- [ ] Unit tests for interface implementations
- [ ] All existing Gmail functionality works through new interface

## Verification Steps
1. Create Gmail provider instance and test all methods
2. Create Exchange provider instance and test all methods
3. Test provider factory with different configurations
4. Verify existing Gmail workflows still work
5. Run interface compliance tests

## Notes
- Maintain backward compatibility with existing Gmail code
- Ensure consistent error handling patterns across providers
- Add comprehensive logging for provider operations
- Consider future extensibility for additional providers

## Next Stage
Stage 9: Configuration System Updates
