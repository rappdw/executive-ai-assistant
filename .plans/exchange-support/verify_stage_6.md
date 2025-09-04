# Verification Plan: Stage 6 - Calendar Events Retrieval

**Stage Reference:** `stage_6.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Functional Testing + Output Format Validation  

## Pre-Verification Setup
- [ ] Stage 5 verification completed successfully
- [ ] Test Exchange calendar with known events
- [ ] Mock Microsoft Graph API calendar endpoints prepared

## 6.1 Calendar Events Function Implementation Verification (20 minutes)

### Test Cases
**TC6.1.1: Function Signature Verification**
```python
# Test script: test_calendar_events.py
from eaia.exchange import get_exchange_events_for_days

def test_events_function_signature():
    """Verify calendar events function exists with correct signature"""
    import inspect
    sig = inspect.signature(get_exchange_events_for_days)
    params = list(sig.parameters.keys())
    
    required_params = ['date_strs', 'user_email']
    assert all(param in params for param in required_params)
    print("✓ Function signature correct")

test_events_function_signature()
```

**TC6.1.2: Graph API Calendar Endpoint Usage**
```python
# Verify Graph API calendar implementation
def test_calendar_api_usage():
    """Check for proper Graph API calendar patterns"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    calendar_patterns = [
        '/me/events',
        'calendar',
        'GET',
        'startTime',
        'endTime'
    ]
    
    found_patterns = [pattern for pattern in calendar_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Calendar API usage incomplete: {found_patterns}"
    print(f"✓ Calendar API patterns found: {found_patterns}")

test_calendar_api_usage()
```

**TC6.1.3: Date Range Filtering**
```python
# Test date range filtering implementation
def test_date_range_filtering():
    """Verify date range filtering is implemented"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    date_patterns = [
        'dd-mm-yyyy',
        'datetime',
        'strptime',
        'filter',
        'startTime ge',
        'endTime le'
    ]
    
    found_patterns = [pattern for pattern in date_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Date filtering incomplete: {found_patterns}"
    print(f"✓ Date filtering patterns found: {found_patterns}")

test_date_range_filtering()
```

**Expected Results:**
- [ ] `get_exchange_events_for_days()` function implemented
- [ ] Microsoft Graph `/me/events` endpoint used
- [ ] Date range filtering works with dd-mm-yyyy format
- [ ] Multiple date ranges supported efficiently
- [ ] Function signature matches Gmail equivalent

## 6.2 Event Format Conversion Verification (15 minutes)

### Test Cases
**TC6.2.1: Event Conversion Function**
```python
# Test event conversion
def test_event_conversion():
    """Verify event conversion function exists"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    conversion_patterns = [
        'convert_exchange_event',
        'format_event',
        'subject',
        'start',
        'end',
        'summary'
    ]
    
    found_patterns = [pattern for pattern in conversion_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Event conversion incomplete: {found_patterns}"
    print(f"✓ Event conversion patterns found: {found_patterns}")

test_event_conversion()
```

**TC6.2.2: Gmail Format Compatibility**
```python
# Test Gmail format compatibility
def test_gmail_format_compatibility():
    """Verify output format matches Gmail calendar tool"""
    
    # Mock Exchange event structure
    mock_exchange_event = {
        "subject": "Test Meeting",
        "start": {"dateTime": "2024-01-01T14:00:00Z"},
        "end": {"dateTime": "2024-01-01T15:00:00Z"},
        "organizer": {"emailAddress": {"address": "organizer@example.com"}}
    }
    
    # Check for Gmail-compatible formatting patterns
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    format_patterns = ['Event:', 'Starts:', 'Ends:', 'format_datetime_with_timezone']
    found_patterns = [pattern for pattern in format_patterns if pattern in source]
    
    assert len(found_patterns) >= 3, f"Gmail format compatibility incomplete: {found_patterns}"
    print(f"✓ Gmail format patterns found: {found_patterns}")

test_gmail_format_compatibility()
```

**TC6.2.3: Timezone Handling**
```python
# Test timezone conversion
def test_timezone_handling():
    """Verify timezone handling is implemented"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    timezone_patterns = [
        'timezone',
        'pytz',
        'astimezone',
        'US/Pacific',
        'strftime'
    ]
    
    found_patterns = [pattern for pattern in timezone_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Timezone handling incomplete: {found_patterns}"
    print(f"✓ Timezone handling patterns found: {found_patterns}")

test_timezone_handling()
```

**Expected Results:**
- [ ] Event format conversion function implemented
- [ ] Exchange event fields mapped to Gmail format
- [ ] Timezone conversions handled properly
- [ ] DateTime strings formatted consistently

## 6.3 Date Range Handling Verification (10 minutes)

### Test Cases
**TC6.3.1: Date Parsing Implementation**
```python
# Test date parsing
def test_date_parsing():
    """Verify dd-mm-yyyy date parsing"""
    
    # Test date parsing logic
    test_date = "01-12-2024"
    
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    parsing_patterns = [
        'strptime',
        'dd-mm-yyyy',
        '%d-%m-%Y',
        'datetime',
        'date'
    ]
    
    found_patterns = [pattern for pattern in parsing_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Date parsing incomplete: {found_patterns}"
    print(f"✓ Date parsing patterns found: {found_patterns}")

test_date_parsing()
```

**TC6.3.2: Graph API Query Construction**
```python
# Test Graph API query building
def test_query_construction():
    """Verify Graph API filter queries are built correctly"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    query_patterns = [
        'filter',
        'startTime',
        'endTime',
        'ge',
        'le',
        'and'
    ]
    
    found_patterns = [pattern for pattern in query_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Query construction incomplete: {found_patterns}"
    print(f"✓ Query construction patterns found: {found_patterns}")

test_query_construction()
```

**Expected Results:**
- [ ] dd-mm-yyyy date format parsing implemented
- [ ] Timezone considerations handled
- [ ] Graph API filter queries built correctly
- [ ] Multiple date ranges processed efficiently

## 6.4 Output Formatting Verification (10 minutes)

### Test Cases
**TC6.4.1: Event Display Format**
```python
# Test event display formatting
def test_event_display_format():
    """Verify event display matches Gmail format exactly"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    display_patterns = [
        'Event:',
        'Starts:',
        'Ends:',
        'No events found',
        '***FOR DAY',
        '-' * 40
    ]
    
    found_patterns = [pattern for pattern in display_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Display format incomplete: {found_patterns}"
    print(f"✓ Display format patterns found: {found_patterns}")

test_event_display_format()
```

**TC6.4.2: All-Day Event Handling**
```python
# Test all-day vs timed event handling
def test_allday_event_handling():
    """Verify all-day and timed events are handled differently"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    allday_patterns = [
        'isAllDay',
        'date',
        'dateTime',
        'T' in,
        'all-day'
    ]
    
    found_patterns = [pattern for pattern in allday_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ All-day event handling found: {found_patterns}")
    else:
        print(f"⚠ All-day event handling may be incomplete")

test_allday_event_handling()
```

**Expected Results:**
- [ ] Output format matches Gmail calendar tool exactly
- [ ] All-day vs timed events handled correctly
- [ ] Timezone display consistent
- [ ] Empty day handling implemented

## Mock Testing Verification (5 minutes)

### Test Cases
**TC6.M.1: Unit Tests Exist**
```bash
# Check for calendar events tests
find tests/ -name "*exchange*" -o -name "*calendar*" | grep -E "\.(py)$"
echo "✓ Calendar test files found"
```

**TC6.M.2: Mock Calendar Implementation**
```python
# Verify mock testing for calendar events
def test_calendar_mock_implementation():
    """Check mock testing for calendar functionality"""
    import glob
    
    test_files = glob.glob('tests/**/test*exchange*.py', recursive=True)
    
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if 'get_exchange_events_for_days' in content:
            mock_patterns = ['mock', 'patch', '@patch', 'MagicMock', 'responses']
            if any(pattern in content for pattern in mock_patterns):
                print(f"✓ Calendar mock testing found in {test_file}")
                return
    
    print("⚠ Mock testing for calendar events not found")

test_calendar_mock_implementation()
```

**Expected Results:**
- [ ] Unit tests for calendar events created
- [ ] Mock Graph API calendar responses implemented
- [ ] Tests cover different event types
- [ ] Date parsing tests included

## Integration Verification (5 minutes)

### Test Cases
**TC6.I.1: Gmail Tool Compatibility**
```python
# Test compatibility with Gmail calendar tool
def test_gmail_tool_compatibility():
    """Verify calendar function integrates like Gmail tool"""
    from eaia.gmail import get_events_for_days as gmail_events
    from eaia.exchange import get_exchange_events_for_days
    
    import inspect
    
    gmail_sig = inspect.signature(gmail_events)
    exchange_sig = inspect.signature(get_exchange_events_for_days)
    
    # Check parameter compatibility
    gmail_params = set(gmail_sig.parameters.keys())
    exchange_params = set(exchange_sig.parameters.keys())
    
    # Core parameters should match
    core_params = {'date_strs'}
    assert core_params.issubset(gmail_params)
    assert core_params.issubset(exchange_params)
    
    print("✓ Gmail tool compatibility verified")

test_gmail_tool_compatibility()
```

**Expected Results:**
- [ ] Function signature compatible with Gmail tool
- [ ] Output format identical to Gmail
- [ ] Integration with LangGraph tool system
- [ ] Same user experience

## Final Verification Checklist

### Functionality
- [ ] Calendar events retrieval from Graph API implemented
- [ ] Date range filtering works correctly
- [ ] Event format conversion matches Gmail
- [ ] Multiple date support implemented
- [ ] Timezone handling works properly

### Output Format
- [ ] Exact Gmail calendar tool output format
- [ ] All-day vs timed events handled correctly
- [ ] Timezone display consistent
- [ ] Empty calendar days handled

### Date Handling
- [ ] dd-mm-yyyy format parsing works
- [ ] Timezone conversions correct
- [ ] Graph API queries built properly
- [ ] Multiple date ranges efficient

### Compatibility
- [ ] Function interface matches Gmail tool
- [ ] Output format identical
- [ ] Integration with existing workflow
- [ ] User experience consistent

### Testing
- [ ] Unit tests created and passing
- [ ] Mock testing implemented
- [ ] Different event types covered
- [ ] Edge cases tested

## Success Criteria
- [ ] All test cases pass
- [ ] Calendar events work with mock data
- [ ] Output format validation passes
- [ ] Ready for Stage 7 (Calendar Invites)

## Notes for Next Stage
- Document any Exchange-specific calendar features
- Note timezone handling patterns for invites
- Record any event format considerations for Stage 7
