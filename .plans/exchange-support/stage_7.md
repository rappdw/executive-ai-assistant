# Stage 7: Calendar Invite Sending

**Estimated Time:** 2-3 hours  
**Prerequisites:** Stage 6 completed  
**Dependencies:** Stage 6  

## Objective
Implement calendar invite creation and sending using Microsoft Graph API, maintaining compatibility with the existing Gmail calendar interface.

## Tasks

### 7.1 Calendar Invite Function Implementation (90 minutes)
- Implement `send_exchange_calendar_invite()` function
- Use Microsoft Graph `POST /me/events` endpoint
- Handle attendee management and notifications
- Support meeting creation with proper timezone handling

**Key implementation points:**
```python
def send_exchange_calendar_invite(
    emails: list, 
    title: str, 
    start_time: str, 
    end_time: str, 
    user_email: str, 
    timezone="PST"
):
    # Parse datetime strings
    # Build event object with attendees
    # Create event via Graph API
    # Handle Teams meeting integration
```

### 7.2 Event Object Construction (45 minutes)
- Build proper Exchange event structure
- Handle attendee list formatting
- Set up meeting reminders and notifications
- Configure Teams meeting integration (equivalent to Google Meet)

### 7.3 Timezone and DateTime Handling (30 minutes)
- Parse ISO datetime strings correctly
- Handle timezone conversion for Exchange
- Ensure consistent datetime formatting
- Support different timezone inputs

### 7.4 Error Handling and Validation (15 minutes)
- Validate email addresses and datetime formats
- Handle calendar creation failures
- Add appropriate error logging
- Return success/failure status

## Acceptance Criteria
- [ ] `send_exchange_calendar_invite()` creates calendar events successfully
- [ ] Attendees receive meeting invitations
- [ ] Function signature matches Gmail equivalent
- [ ] Teams meeting integration works (equivalent to Google Meet)
- [ ] Proper timezone handling
- [ ] Unit tests for calendar invite creation

## Verification Steps
1. Create a calendar invite with multiple attendees
2. Verify attendees receive invitations
3. Check that meeting appears in Exchange calendar
4. Test Teams meeting link generation
5. Verify timezone handling works correctly

## Notes
- Maintain same function signature as Gmail version
- Teams meeting integration should mirror Google Meet functionality
- Consider Exchange-specific meeting features
- Ensure proper error handling and logging

## Next Stage
Stage 8: Email Provider Interface Design
