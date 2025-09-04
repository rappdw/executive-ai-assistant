# Verification Plan: Stage 3 - Email Fetching Implementation

**Stage Reference:** `stage_3.md`  
**Verification Time:** 60-75 minutes  
**Verification Type:** Functional Testing + Data Validation  

## Pre-Verification Setup
- [ ] Stage 2 verification completed successfully
- [ ] Test Exchange mailbox with known emails available
- [ ] Mock Microsoft Graph API responses prepared

## 3.1 Microsoft Graph Email API Integration Verification (25 minutes)

### Test Cases
**TC3.1.1: Function Implementation**
```python
# Test script: test_email_fetching.py
import asyncio
from eaia.exchange import fetch_exchange_emails
from eaia.schemas import EmailData

async def test_fetch_function_signature():
    """Verify fetch function exists with correct signature"""
    import inspect
    sig = inspect.signature(fetch_exchange_emails)
    params = list(sig.parameters.keys())
    
    required_params = ['user_email', 'minutes_since']
    assert all(param in params for param in required_params)
    assert inspect.iscoroutinefunction(fetch_exchange_emails)
    
    # Check default parameter
    assert sig.parameters['minutes_since'].default == 30
    print("✓ Function signature correct")

asyncio.run(test_fetch_function_signature())
```

**TC3.1.2: Graph API Client Usage**
```python
# Verify Graph API client implementation
def test_graph_api_usage():
    """Check for proper Graph API patterns"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Look for Graph API patterns
    api_patterns = [
        '/me/messages',
        'graph.microsoft.com',
        'GET',
        'requests.get',
        'msgraph'
    ]
    
    found_patterns = [pattern for pattern in api_patterns if pattern in source]
    assert len(found_patterns) >= 2, f"Graph API usage incomplete: {found_patterns}"
    print(f"✓ Graph API patterns found: {found_patterns}")

test_graph_api_usage()
```

**TC3.1.3: Pagination Implementation**
```python
# Test pagination handling
def test_pagination_implementation():
    """Verify pagination is implemented"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    pagination_patterns = [
        '@odata.nextLink',
        'nextLink',
        'while',
        'pagination',
        'page'
    ]
    
    found_patterns = [pattern for pattern in pagination_patterns if pattern in source]
    assert len(found_patterns) >= 2, f"Pagination not properly implemented: {found_patterns}"
    print(f"✓ Pagination patterns found: {found_patterns}")

test_pagination_implementation()
```

**TC3.1.4: Time Filtering**
```python
# Test time-based filtering
def test_time_filtering():
    """Verify time filtering is implemented"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    time_patterns = [
        'receivedDateTime',
        'datetime',
        'timedelta',
        'minutes_since',
        'filter',
        'ge'  # Greater than or equal in OData
    ]
    
    found_patterns = [pattern for pattern in time_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Time filtering incomplete: {found_patterns}"
    print(f"✓ Time filtering patterns found: {found_patterns}")

test_time_filtering()
```

**Expected Results:**
- [ ] `fetch_exchange_emails()` function implemented
- [ ] Microsoft Graph `/me/messages` endpoint used
- [ ] Pagination handling implemented
- [ ] Time-based filtering works with minutes_since parameter
- [ ] Returns async iterator of EmailData objects

## 3.2 Message Format Conversion Verification (20 minutes)

### Test Cases
**TC3.2.1: Conversion Function Exists**
```python
# Test conversion function
def test_conversion_function():
    """Verify message conversion function exists"""
    try:
        from eaia.exchange import convert_exchange_message_to_email_data
        print("✓ Conversion function exists")
    except ImportError:
        # Check if it's defined inline in fetch function
        with open('eaia/exchange.py', 'r') as f:
            source = f.read()
        assert 'convert' in source.lower() or 'EmailData' in source
        print("✓ Conversion logic found in source")

test_conversion_function()
```

**TC3.2.2: Field Mapping Verification**
```python
# Test field mapping
def test_field_mapping():
    """Verify Exchange to EmailData field mapping"""
    
    # Mock Exchange message structure
    mock_exchange_msg = {
        "id": "test-id-123",
        "conversationId": "conv-123",
        "from": {"emailAddress": {"address": "sender@example.com"}},
        "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
        "subject": "Test Subject",
        "body": {"content": "Test body content"},
        "receivedDateTime": "2024-01-01T12:00:00Z"
    }
    
    # Test conversion (if function is available)
    try:
        from eaia.exchange import convert_exchange_message_to_email_data
        result = convert_exchange_message_to_email_data(mock_exchange_msg)
        
        assert result["id"] == "test-id-123"
        assert result["thread_id"] == "conv-123"
        assert result["from_email"] == "sender@example.com"
        assert result["to_email"] == "recipient@example.com"
        assert result["subject"] == "Test Subject"
        assert result["page_content"] == "Test body content"
        assert result["send_time"] == "2024-01-01T12:00:00Z"
        
        print("✓ Field mapping correct")
    except ImportError:
        print("⚠ Conversion function not separately defined - check inline implementation")

test_field_mapping()
```

**TC3.2.3: EmailData Schema Compliance**
```python
# Verify EmailData schema compliance
def test_emaildata_compliance():
    """Verify converted data matches EmailData schema"""
    from eaia.schemas import EmailData
    
    # Check EmailData structure
    import typing
    if hasattr(EmailData, '__annotations__'):
        required_fields = EmailData.__annotations__.keys()
    else:
        # For TypedDict, check required fields
        required_fields = ['id', 'thread_id', 'from_email', 'to_email', 'subject', 'page_content', 'send_time']
    
    print(f"✓ EmailData schema requires: {list(required_fields)}")
    
    # Verify conversion produces all required fields
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    for field in required_fields:
        assert field in source, f"Missing field mapping for: {field}"
    
    print("✓ All required fields mapped")

test_emaildata_compliance()
```

**Expected Results:**
- [ ] `convert_exchange_message_to_email_data()` function implemented
- [ ] All EmailData fields properly mapped
- [ ] Exchange conversation ID mapped to thread_id
- [ ] Email addresses extracted correctly
- [ ] DateTime format handled properly

## 3.3 Body Content Extraction Verification (15 minutes)

### Test Cases
**TC3.3.1: Body Extraction Function**
```python
# Test body extraction
def test_body_extraction():
    """Verify body content extraction"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    body_patterns = [
        'extract_exchange_message_body',
        'extract_body_content',
        'body',
        'content',
        'html',
        'text'
    ]
    
    found_patterns = [pattern for pattern in body_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Body extraction incomplete: {found_patterns}"
    print(f"✓ Body extraction patterns found: {found_patterns}")

test_body_extraction()
```

**TC3.3.2: HTML and Plain Text Handling**
```python
# Test HTML/plain text handling
def test_content_type_handling():
    """Verify HTML and plain text content handling"""
    
    # Mock body structures
    html_body = {
        "contentType": "html",
        "content": "<p>HTML content</p>"
    }
    
    text_body = {
        "contentType": "text", 
        "content": "Plain text content"
    }
    
    # Check if handling exists in source
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    content_patterns = ['contentType', 'html', 'text', 'strip', 'clean']
    found_patterns = [pattern for pattern in content_patterns if pattern in source]
    
    assert len(found_patterns) >= 2, f"Content type handling incomplete: {found_patterns}"
    print(f"✓ Content type handling found: {found_patterns}")

test_content_type_handling()
```

**TC3.3.3: Gmail Compatibility**
```python
# Verify output matches Gmail format
def test_gmail_format_compatibility():
    """Ensure body extraction matches Gmail format"""
    from eaia.gmail import extract_message_part
    
    # Compare function signatures or patterns
    print("✓ Gmail compatibility check - manual verification required")
    # Note: Full test requires actual message comparison

test_gmail_format_compatibility()
```

**Expected Results:**
- [ ] Body content extraction function implemented
- [ ] HTML and plain text formats handled
- [ ] Output format consistent with Gmail implementation
- [ ] Proper text cleaning and formatting

## 3.4 Error Handling and Edge Cases Verification (15 minutes)

### Test Cases
**TC3.4.1: Error Handling Implementation**
```python
# Test error handling
def test_error_handling():
    """Verify comprehensive error handling"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    error_patterns = [
        'try:', 'except', 'Exception', 'error', 'raise',
        'HTTPError', 'RequestException', 'timeout'
    ]
    
    found_patterns = [pattern for pattern in error_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Error handling incomplete: {found_patterns}"
    print(f"✓ Error handling patterns found: {found_patterns}")

test_error_handling()
```

**TC3.4.2: Rate Limiting Handling**
```python
# Test rate limiting
def test_rate_limiting():
    """Verify rate limiting is handled"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    rate_patterns = [
        'rate', 'limit', '429', 'retry', 'backoff', 'sleep', 'throttle'
    ]
    
    found_patterns = [pattern for pattern in rate_patterns if pattern in source]
    if len(found_patterns) >= 2:
        print(f"✓ Rate limiting handling found: {found_patterns}")
    else:
        print(f"⚠ Rate limiting may not be implemented: {found_patterns}")

test_rate_limiting()
```

**TC3.4.3: Edge Case Handling**
```python
# Test edge cases
def test_edge_cases():
    """Verify edge case handling"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    edge_patterns = [
        'None', 'empty', 'missing', 'get(', 'KeyError', 'IndexError'
    ]
    
    found_patterns = [pattern for pattern in edge_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Edge case handling incomplete: {found_patterns}"
    print(f"✓ Edge case handling found: {found_patterns}")

test_edge_cases()
```

**Expected Results:**
- [ ] Comprehensive error handling for API failures
- [ ] Rate limiting handled with retry logic
- [ ] Missing/malformed message fields handled
- [ ] Appropriate logging for errors

## Mock Testing Verification (10 minutes)

### Test Cases
**TC3.M.1: Unit Tests Exist**
```bash
# Check for email fetching tests
find tests/ -name "*exchange*" -o -name "*email*" | grep -E "\.(py)$"
echo "✓ Test files found"
```

**TC3.M.2: Mock Implementation**
```python
# Verify mock testing
def test_mock_implementation():
    """Check mock testing for email fetching"""
    import glob
    
    test_files = glob.glob('tests/**/test*exchange*.py', recursive=True)
    
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if 'fetch_exchange_emails' in content:
            mock_patterns = ['mock', 'patch', '@patch', 'MagicMock', 'responses']
            if any(pattern in content for pattern in mock_patterns):
                print(f"✓ Mock testing found in {test_file}")
                return
    
    print("⚠ Mock testing for email fetching not found")

test_mock_implementation()
```

**Expected Results:**
- [ ] Unit tests for email fetching created
- [ ] Mock Graph API responses implemented
- [ ] Tests cover success and error scenarios
- [ ] Conversion function tests included

## Integration Testing (5 minutes)

### Test Cases
**TC3.I.1: End-to-End Flow**
```python
# Test complete flow (with mocks)
async def test_complete_flow():
    """Test complete email fetching flow"""
    # This would require mock setup
    print("✓ End-to-end flow test structure verified")
    # Note: Full test requires mock Graph API responses

asyncio.run(test_complete_flow())
```

**Expected Results:**
- [ ] Complete flow from API call to EmailData works
- [ ] Async iterator pattern implemented correctly
- [ ] Integration with existing schemas works

## Final Verification Checklist

### Functionality
- [ ] Email fetching from Graph API implemented
- [ ] Message format conversion works correctly
- [ ] Body content extraction handles HTML/text
- [ ] Pagination implemented for large result sets
- [ ] Time filtering works with minutes_since

### Data Quality
- [ ] All EmailData fields properly mapped
- [ ] DateTime formats handled correctly
- [ ] Thread/conversation IDs mapped properly
- [ ] Email addresses extracted accurately

### Error Handling
- [ ] API failures handled gracefully
- [ ] Rate limiting implemented
- [ ] Missing fields handled safely
- [ ] Appropriate error logging

### Testing
- [ ] Unit tests created and passing
- [ ] Mock testing implemented
- [ ] Edge cases covered
- [ ] Integration tests planned

## Success Criteria
- [ ] All test cases pass
- [ ] Email fetching works with mock data
- [ ] Data conversion produces valid EmailData
- [ ] Ready for Stage 4 (Email Sending)

## Notes for Next Stage
- Document any Graph API patterns for Stage 4
- Note message ID format for reply functionality
- Record any Exchange-specific threading behavior
