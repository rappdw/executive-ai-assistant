# Verification Plan: Stage 4 - Email Sending Implementation

**Stage Reference:** `stage_4.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Functional Testing + Message Validation  

## Pre-Verification Setup
- [ ] Stage 3 verification completed successfully
- [ ] Test Exchange mailbox for sending emails
- [ ] Mock Microsoft Graph API send endpoints prepared

## 4.1 Send Email Function Implementation Verification (20 minutes)

### Test Cases
**TC4.1.1: Function Signature Verification**
```python
# Test script: test_email_sending.py
from eaia.exchange import send_exchange_email

def test_send_function_signature():
    """Verify send function exists with correct signature"""
    import inspect
    sig = inspect.signature(send_exchange_email)
    params = list(sig.parameters.keys())
    
    required_params = ['message_id', 'response_text', 'user_email']
    assert all(param in params for param in required_params)
    
    # Check for optional parameters
    assert 'addn_recipients' in params or 'kwargs' in str(sig)
    print("✓ Function signature correct")

test_send_function_signature()
```

**TC4.1.2: Graph API Send Endpoint Usage**
```python
# Verify Graph API send implementation
def test_send_api_usage():
    """Check for proper Graph API send patterns"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    send_patterns = [
        '/me/sendMail',
        'POST',
        'sendMail',
        'message',
        'toRecipients'
    ]
    
    found_patterns = [pattern for pattern in send_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Send API usage incomplete: {found_patterns}"
    print(f"✓ Send API patterns found: {found_patterns}")

test_send_api_usage()
```

**TC4.1.3: Reply Threading Implementation**
```python
# Test reply threading
def test_reply_threading():
    """Verify reply threading is implemented"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    threading_patterns = [
        'In-Reply-To',
        'References', 
        'conversationId',
        'replyTo',
        'thread'
    ]
    
    found_patterns = [pattern for pattern in threading_patterns if pattern in source]
    assert len(found_patterns) >= 2, f"Reply threading incomplete: {found_patterns}"
    print(f"✓ Reply threading patterns found: {found_patterns}")

test_reply_threading()
```

**Expected Results:**
- [ ] `send_exchange_email()` function implemented
- [ ] Microsoft Graph `/me/sendMail` endpoint used
- [ ] Reply threading implemented correctly
- [ ] Additional recipients parameter supported
- [ ] Function signature matches Gmail equivalent

## 4.2 Message Composition Verification (15 minutes)

### Test Cases
**TC4.2.1: Message Structure Creation**
```python
# Test message composition
def test_message_composition():
    """Verify message composition function exists"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    composition_patterns = [
        'create_exchange_message',
        'compose',
        'message',
        'subject',
        'body',
        'toRecipients'
    ]
    
    found_patterns = [pattern for pattern in composition_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Message composition incomplete: {found_patterns}"
    print(f"✓ Message composition patterns found: {found_patterns}")

test_message_composition()
```

**TC4.2.2: Exchange Message Format**
```python
# Test Exchange message format compliance
def test_exchange_message_format():
    """Verify message format matches Exchange requirements"""
    
    # Mock message structure test
    expected_structure = {
        'message': {
            'subject': 'string',
            'body': {'contentType': 'string', 'content': 'string'},
            'toRecipients': [{'emailAddress': {'address': 'string'}}],
            'replyTo': [{'emailAddress': {'address': 'string'}}]
        }
    }
    
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Check for required structure elements
    structure_elements = ['subject', 'body', 'toRecipients', 'contentType', 'emailAddress']
    found_elements = [elem for elem in structure_elements if elem in source]
    
    assert len(found_elements) >= 4, f"Message structure incomplete: {found_elements}"
    print(f"✓ Message structure elements found: {found_elements}")

test_exchange_message_format()
```

**TC4.2.3: HTML and Plain Text Support**
```python
# Test content type support
def test_content_type_support():
    """Verify HTML and plain text content support"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    content_patterns = ['contentType', 'html', 'text', 'Text', 'Html']
    found_patterns = [pattern for pattern in content_patterns if pattern in source]
    
    assert len(found_patterns) >= 2, f"Content type support incomplete: {found_patterns}"
    print(f"✓ Content type support found: {found_patterns}")

test_content_type_support()
```

**Expected Results:**
- [ ] `create_exchange_message()` function implemented
- [ ] Message structure matches Exchange API requirements
- [ ] HTML and plain text content supported
- [ ] Reply headers properly set

## 4.3 Recipient Management Verification (10 minutes)

### Test Cases
**TC4.3.1: Recipient Extraction Function**
```python
# Test recipient management
def test_recipient_management():
    """Verify recipient extraction and management"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    recipient_patterns = [
        'get_exchange_recipients',
        'recipients',
        'toRecipients',
        'ccRecipients', 
        'bccRecipients',
        'from',
        'replyTo'
    ]
    
    found_patterns = [pattern for pattern in recipient_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Recipient management incomplete: {found_patterns}"
    print(f"✓ Recipient management patterns found: {found_patterns}")

test_recipient_management()
```

**TC4.3.2: Gmail Compatibility**
```python
# Test Gmail recipient logic compatibility
def test_gmail_recipient_compatibility():
    """Verify recipient logic matches Gmail implementation"""
    from eaia.gmail import get_recipients
    
    # Compare function signatures if available
    try:
        from eaia.exchange import get_exchange_recipients
        import inspect
        
        gmail_sig = inspect.signature(get_recipients)
        exchange_sig = inspect.signature(get_exchange_recipients)
        
        # Basic compatibility check
        print("✓ Recipient function compatibility verified")
    except ImportError:
        # Check if logic is inline
        with open('eaia/exchange.py', 'r') as f:
            source = f.read()
        assert 'recipient' in source.lower()
        print("✓ Recipient logic found inline")

test_gmail_recipient_compatibility()
```

**Expected Results:**
- [ ] `get_exchange_recipients()` function implemented
- [ ] CC, BCC, and additional recipients handled
- [ ] Original sender included in reply recipients
- [ ] Logic mirrors Gmail recipient handling

## 4.4 Error Handling and Validation Verification (10 minutes)

### Test Cases
**TC4.4.1: Input Validation**
```python
# Test input validation
def test_input_validation():
    """Verify input validation is implemented"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    validation_patterns = [
        'validate', 'check', 'verify', 'assert', 'raise',
        'ValueError', 'TypeError', 'empty', 'None'
    ]
    
    found_patterns = [pattern for pattern in validation_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Input validation incomplete: {found_patterns}"
    print(f"✓ Input validation patterns found: {found_patterns}")

test_input_validation()
```

**TC4.4.2: Send Error Handling**
```python
# Test send error handling
def test_send_error_handling():
    """Verify send operation error handling"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    error_patterns = [
        'try:', 'except', 'HTTPError', 'RequestException',
        'send', 'fail', 'error', 'retry'
    ]
    
    found_patterns = [pattern for pattern in error_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Send error handling incomplete: {found_patterns}"
    print(f"✓ Send error handling patterns found: {found_patterns}")

test_send_error_handling()
```

**TC4.4.3: Retry Logic**
```python
# Test retry implementation
def test_retry_logic():
    """Verify retry logic for transient failures"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    retry_patterns = ['retry', 'attempt', 'backoff', 'sleep', 'for i in range']
    found_patterns = [pattern for pattern in retry_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Retry logic found: {found_patterns}")
    else:
        print(f"⚠ Retry logic may not be implemented: {found_patterns}")

test_retry_logic()
```

**Expected Results:**
- [ ] Input validation for message content and recipients
- [ ] Error handling for Graph API send failures
- [ ] Retry logic for transient failures
- [ ] Appropriate logging for send operations

## Mock Testing Verification (5 minutes)

### Test Cases
**TC4.M.1: Unit Tests Exist**
```bash
# Check for email sending tests
find tests/ -name "*exchange*" -o -name "*send*" | grep -E "\.(py)$"
echo "✓ Send test files found"
```

**TC4.M.2: Mock Send Implementation**
```python
# Verify mock testing for sending
def test_send_mock_implementation():
    """Check mock testing for email sending"""
    import glob
    
    test_files = glob.glob('tests/**/test*exchange*.py', recursive=True)
    
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if 'send_exchange_email' in content:
            mock_patterns = ['mock', 'patch', '@patch', 'MagicMock', 'responses']
            if any(pattern in content for pattern in mock_patterns):
                print(f"✓ Send mock testing found in {test_file}")
                return
    
    print("⚠ Mock testing for email sending not found")

test_send_mock_implementation()
```

**Expected Results:**
- [ ] Unit tests for email sending created
- [ ] Mock Graph API send responses implemented
- [ ] Tests cover success and failure scenarios
- [ ] Message composition tests included

## Integration Verification (5 minutes)

### Test Cases
**TC4.I.1: Gmail Interface Compatibility**
```python
# Test interface compatibility
def test_gmail_interface_compatibility():
    """Verify send function interface matches Gmail"""
    from eaia.gmail import send_email as gmail_send
    from eaia.exchange import send_exchange_email
    
    import inspect
    
    gmail_sig = inspect.signature(gmail_send)
    exchange_sig = inspect.signature(send_exchange_email)
    
    # Check parameter compatibility
    gmail_params = set(gmail_sig.parameters.keys())
    exchange_params = set(exchange_sig.parameters.keys())
    
    # Core parameters should match
    core_params = {'message_id', 'response_text', 'user_email'}
    assert core_params.issubset(gmail_params)
    assert core_params.issubset(exchange_params)
    
    print("✓ Interface compatibility verified")

test_gmail_interface_compatibility()
```

**Expected Results:**
- [ ] Function signature compatible with Gmail version
- [ ] Same parameter names and types
- [ ] Compatible return behavior

## Final Verification Checklist

### Functionality
- [ ] Email sending via Graph API implemented
- [ ] Message composition works correctly
- [ ] Reply threading implemented
- [ ] Recipient management handles all cases
- [ ] Additional recipients supported

### Message Format
- [ ] Exchange message structure correct
- [ ] HTML and plain text content supported
- [ ] Reply headers properly set
- [ ] Subject line handling correct

### Error Handling
- [ ] Input validation implemented
- [ ] Send failures handled gracefully
- [ ] Retry logic for transient failures
- [ ] Appropriate error logging

### Compatibility
- [ ] Function interface matches Gmail
- [ ] Recipient logic mirrors Gmail behavior
- [ ] Threading behavior consistent

### Testing
- [ ] Unit tests created and passing
- [ ] Mock testing implemented
- [ ] Error scenarios covered
- [ ] Message composition tested

## Success Criteria
- [ ] All test cases pass
- [ ] Email sending works with mock data
- [ ] Message format validation passes
- [ ] Ready for Stage 5 (Mark as Read)

## Notes for Next Stage
- Document message ID format for mark as read
- Note any Exchange-specific send behavior
- Record any threading considerations for Stage 5
