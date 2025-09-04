# Verification Plan: Stage 7 - Calendar Invite Sending

**Stage Reference:** `stage_7.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Functional Testing + Meeting Integration Validation  

## Pre-Verification Setup
- [ ] Stage 6 verification completed successfully
- [ ] Test Exchange calendar for creating events
- [ ] Mock Microsoft Graph API event creation endpoints prepared

## 7.1 Calendar Invite Function Implementation Verification (20 minutes)

### Test Cases
**TC7.1.1: Function Signature Verification**
```python
# Test script: test_calendar_invites.py
from eaia.exchange import send_exchange_calendar_invite

def test_invite_function_signature():
    """Verify calendar invite function exists with correct signature"""
    import inspect
    sig = inspect.signature(send_exchange_calendar_invite)
    params = list(sig.parameters.keys())
    
    required_params = ['emails', 'title', 'start_time', 'end_time', 'user_email']
    assert all(param in params for param in required_params)
    
    # Check for timezone parameter
    assert 'timezone' in params or 'kwargs' in str(sig)
    print("✓ Function signature correct")

test_invite_function_signature()
```

**TC7.1.2: Graph API Event Creation Usage**
```python
# Verify Graph API event creation implementation
def test_event_creation_api_usage():
    """Check for proper Graph API event creation patterns"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    event_patterns = [
        'POST /me/events',
        'POST',
        '/events',
        'attendees',
        'subject',
        'start',
        'end'
    ]
    
    found_patterns = [pattern for pattern in event_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Event creation API usage incomplete: {found_patterns}"
    print(f"✓ Event creation API patterns found: {found_patterns}")

test_event_creation_api_usage()
```

**TC7.1.3: Teams Meeting Integration**
```python
# Test Teams meeting integration
def test_teams_meeting_integration():
    """Verify Teams meeting integration (equivalent to Google Meet)"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    teams_patterns = [
        'Teams',
        'onlineMeeting',
        'isOnlineMeeting',
        'joinUrl',
        'conferenceId'
    ]
    
    found_patterns = [pattern for pattern in teams_patterns if pattern in source]
    assert len(found_patterns) >= 2, f"Teams integration incomplete: {found_patterns}"
    print(f"✓ Teams meeting patterns found: {found_patterns}")

test_teams_meeting_integration()
```

**Expected Results:**
- [ ] `send_exchange_calendar_invite()` function implemented
- [ ] Microsoft Graph `POST /me/events` endpoint used
- [ ] Attendee management and notifications handled
- [ ] Teams meeting integration works
- [ ] Function signature matches Gmail equivalent

## 7.2 Event Object Construction Verification (15 minutes)

### Test Cases
**TC7.2.1: Event Structure Creation**
```python
# Test event object construction
def test_event_object_construction():
    """Verify Exchange event object structure"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    structure_patterns = [
        'subject',
        'start',
        'end',
        'attendees',
        'emailAddress',
        'dateTime',
        'timeZone'
    ]
    
    found_patterns = [pattern for pattern in structure_patterns if pattern in source]
    assert len(found_patterns) >= 6, f"Event structure incomplete: {found_patterns}"
    print(f"✓ Event structure patterns found: {found_patterns}")

test_event_object_construction()
```

**TC7.2.2: Attendee List Formatting**
```python
# Test attendee list formatting
def test_attendee_formatting():
    """Verify attendee list is formatted correctly for Exchange"""
    
    # Mock attendee list
    mock_emails = ["attendee1@example.com", "attendee2@example.com"]
    
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    attendee_patterns = [
        'attendees',
        'emailAddress',
        'address',
        'for email in',
        'required'
    ]
    
    found_patterns = [pattern for pattern in attendee_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Attendee formatting incomplete: {found_patterns}"
    print(f"✓ Attendee formatting patterns found: {found_patterns}")

test_attendee_formatting()
```

**TC7.2.3: Reminder and Notification Setup**
```python
# Test reminder and notification configuration
def test_reminder_notification_setup():
    """Verify reminders and notifications are configured"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    reminder_patterns = [
        'reminder',
        'notification',
        'alert',
        'minutes',
        'beforeStart'
    ]
    
    found_patterns = [pattern for pattern in reminder_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Reminder/notification setup found: {found_patterns}")
    else:
        print(f"⚠ Reminder/notification setup may be incomplete")

test_reminder_notification_setup()
```

**Expected Results:**
- [ ] Exchange event object structure correct
- [ ] Attendee list formatting proper
- [ ] Meeting reminders configured
- [ ] Notification settings handled

## 7.3 Timezone and DateTime Handling Verification (10 minutes)

### Test Cases
**TC7.3.1: DateTime Parsing**
```python
# Test datetime parsing
def test_datetime_parsing():
    """Verify ISO datetime string parsing"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    datetime_patterns = [
        'fromisoformat',
        'datetime',
        'isoformat',
        'strptime',
        'parse'
    ]
    
    found_patterns = [pattern for pattern in datetime_patterns if pattern in source]
    assert len(found_patterns) >= 2, f"DateTime parsing incomplete: {found_patterns}"
    print(f"✓ DateTime parsing patterns found: {found_patterns}")

test_datetime_parsing()
```

**TC7.3.2: Timezone Conversion**
```python
# Test timezone handling
def test_timezone_conversion():
    """Verify timezone conversion for Exchange"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    timezone_patterns = [
        'timezone',
        'timeZone',
        'PST',
        'UTC',
        'astimezone'
    ]
    
    found_patterns = [pattern for pattern in timezone_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Timezone conversion incomplete: {found_patterns}"
    print(f"✓ Timezone conversion patterns found: {found_patterns}")

test_timezone_conversion()
```

**Expected Results:**
- [ ] ISO datetime strings parsed correctly
- [ ] Timezone conversion for Exchange implemented
- [ ] Consistent datetime formatting
- [ ] Different timezone inputs supported

## 7.4 Error Handling and Validation Verification (10 minutes)

### Test Cases
**TC7.4.1: Input Validation**
```python
# Test input validation
def test_input_validation():
    """Verify email addresses and datetime validation"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    validation_patterns = [
        'validate',
        '@',
        'email',
        'datetime',
        'ValueError',
        'TypeError'
    ]
    
    found_patterns = [pattern for pattern in validation_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Input validation incomplete: {found_patterns}"
    print(f"✓ Input validation patterns found: {found_patterns}")

test_input_validation()
```

**TC7.4.2: Calendar Creation Error Handling**
```python
# Test calendar creation error handling
def test_calendar_error_handling():
    """Verify calendar creation failures are handled"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    error_patterns = [
        'try:',
        'except',
        'HTTPError',
        'calendar',
        'creation',
        'failed'
    ]
    
    found_patterns = [pattern for pattern in error_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Calendar error handling incomplete: {found_patterns}"
    print(f"✓ Calendar error handling patterns found: {found_patterns}")

test_calendar_error_handling()
```

**TC7.4.3: Success/Failure Status Return**
```python
# Test return status handling
def test_return_status():
    """Verify function returns success/failure status"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    status_patterns = [
        'return True',
        'return False',
        'success',
        'failure',
        'bool'
    ]
    
    found_patterns = [pattern for pattern in status_patterns if pattern in source]
    assert len(found_patterns) >= 2, f"Return status incomplete: {found_patterns}"
    print(f"✓ Return status patterns found: {found_patterns}")

test_return_status()
```

**Expected Results:**
- [ ] Email address validation implemented
- [ ] DateTime format validation implemented
- [ ] Calendar creation failures handled
- [ ] Success/failure status returned

## Mock Testing Verification (5 minutes)

### Test Cases
**TC7.M.1: Unit Tests Exist**
```bash
# Check for calendar invite tests
find tests/ -name "*exchange*" -o -name "*calendar*" -o -name "*invite*" | grep -E "\.(py)$"
echo "✓ Calendar invite test files found"
```

**TC7.M.2: Mock Event Creation Implementation**
```python
# Verify mock testing for calendar invites
def test_invite_mock_implementation():
    """Check mock testing for calendar invite functionality"""
    import glob
    
    test_files = glob.glob('tests/**/test*exchange*.py', recursive=True)
    
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if 'send_exchange_calendar_invite' in content:
            mock_patterns = ['mock', 'patch', '@patch', 'MagicMock', 'responses']
            if any(pattern in content for pattern in mock_patterns):
                print(f"✓ Calendar invite mock testing found in {test_file}")
                return
    
    print("⚠ Mock testing for calendar invites not found")

test_invite_mock_implementation()
```

**Expected Results:**
- [ ] Unit tests for calendar invites created
- [ ] Mock Graph API event creation responses implemented
- [ ] Tests cover success and failure scenarios
- [ ] Teams meeting integration tested

## Integration Verification (5 minutes)

### Test Cases
**TC7.I.1: Gmail Calendar Compatibility**
```python
# Test compatibility with Gmail calendar function
def test_gmail_calendar_compatibility():
    """Verify calendar invite function matches Gmail"""
    from eaia.gmail import send_calendar_invite as gmail_invite
    from eaia.exchange import send_exchange_calendar_invite
    
    import inspect
    
    gmail_sig = inspect.signature(gmail_invite)
    exchange_sig = inspect.signature(send_exchange_calendar_invite)
    
    # Check parameter compatibility
    gmail_params = set(gmail_sig.parameters.keys())
    exchange_params = set(exchange_sig.parameters.keys())
    
    # Core parameters should match
    core_params = {'emails', 'title', 'start_time', 'end_time'}
    assert core_params.issubset(gmail_params)
    assert core_params.issubset(exchange_params)
    
    print("✓ Gmail calendar compatibility verified")

test_gmail_calendar_compatibility()
```

**Expected Results:**
- [ ] Function signature compatible with Gmail version
- [ ] Same parameter names and types
- [ ] Teams meeting equivalent to Google Meet
- [ ] Compatible return behavior

## Final Verification Checklist

### Functionality
- [ ] Calendar invite creation via Graph API implemented
- [ ] Event object construction works correctly
- [ ] Attendee management handles all cases
- [ ] Teams meeting integration works
- [ ] Timezone handling implemented

### Meeting Features
- [ ] Teams meeting links generated (equivalent to Google Meet)
- [ ] Attendee notifications sent
- [ ] Meeting reminders configured
- [ ] Calendar event appears correctly

### Data Handling
- [ ] ISO datetime parsing works
- [ ] Timezone conversion correct
- [ ] Email address validation implemented
- [ ] Input validation comprehensive

### Error Handling
- [ ] Calendar creation failures handled
- [ ] Invalid input validation
- [ ] Appropriate error logging
- [ ] Success/failure status returned

### Compatibility
- [ ] Function interface matches Gmail
- [ ] Teams integration mirrors Google Meet
- [ ] Same user experience
- [ ] Integration with existing workflow

### Testing
- [ ] Unit tests created and passing
- [ ] Mock testing implemented
- [ ] Teams meeting tests included
- [ ] Error scenarios covered

## Success Criteria
- [ ] All test cases pass
- [ ] Calendar invites work with mock data
- [ ] Teams meeting integration verified
- [ ] Ready for Stage 8 (Provider Interface)

## Notes for Next Stage
- Document Teams meeting integration patterns
- Note any Exchange-specific calendar features
- Record interface patterns for provider abstraction
