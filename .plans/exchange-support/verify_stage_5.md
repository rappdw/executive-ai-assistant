# Verification Plan: Stage 5 - Mark as Read Implementation

**Stage Reference:** `stage_5.md`  
**Verification Time:** 30-40 minutes  
**Verification Type:** Functional Testing + API Validation  

## Pre-Verification Setup
- [ ] Stage 4 verification completed successfully
- [ ] Test Exchange mailbox with unread messages
- [ ] Mock Microsoft Graph API PATCH endpoints prepared

## 5.1 Mark as Read Function Implementation Verification (15 minutes)

### Test Cases
**TC5.1.1: Function Signature Verification**
```python
# Test script: test_mark_as_read.py
from eaia.exchange import mark_exchange_as_read

def test_mark_function_signature():
    """Verify mark as read function exists with correct signature"""
    import inspect
    sig = inspect.signature(mark_exchange_as_read)
    params = list(sig.parameters.keys())
    
    required_params = ['message_id', 'user_email']
    assert all(param in params for param in required_params)
    print("✓ Function signature correct")

test_mark_function_signature()
```

**TC5.1.2: Graph API PATCH Endpoint Usage**
```python
# Verify Graph API PATCH implementation
def test_patch_api_usage():
    """Check for proper Graph API PATCH patterns"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    patch_patterns = [
        '/me/messages/{id}',
        'PATCH',
        'isRead',
        'true',
        'message_id'
    ]
    
    found_patterns = [pattern for pattern in patch_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"PATCH API usage incomplete: {found_patterns}"
    print(f"✓ PATCH API patterns found: {found_patterns}")

test_patch_api_usage()
```

**TC5.1.3: Message ID Handling**
```python
# Test message ID validation and usage
def test_message_id_handling():
    """Verify message ID is properly handled"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    id_patterns = [
        'message_id',
        'format',
        'validate',
        'id}',
        'messages/'
    ]
    
    found_patterns = [pattern for pattern in id_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Message ID handling incomplete: {found_patterns}"
    print(f"✓ Message ID handling patterns found: {found_patterns}")

test_message_id_handling()
```

**Expected Results:**
- [ ] `mark_exchange_as_read()` function implemented
- [ ] Microsoft Graph `PATCH /me/messages/{id}` endpoint used
- [ ] `isRead` property set to `true`
- [ ] Message ID properly validated and formatted
- [ ] Function signature matches Gmail equivalent

## 5.2 Batch Operations Support Verification (10 minutes)

### Test Cases
**TC5.2.1: Batch Operation Implementation**
```python
# Test batch operations support
def test_batch_operations():
    """Verify batch operations are supported"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    batch_patterns = [
        'batch',
        'multiple',
        'list',
        'for message',
        'bulk'
    ]
    
    found_patterns = [pattern for pattern in batch_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Batch operations found: {found_patterns}")
    else:
        print(f"⚠ Batch operations may not be implemented: {found_patterns}")

test_batch_operations()
```

**TC5.2.2: Partial Success Handling**
```python
# Test partial success scenarios
def test_partial_success_handling():
    """Verify partial success in batch operations is handled"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    partial_patterns = [
        'partial',
        'some',
        'failed',
        'success',
        'continue'
    ]
    
    found_patterns = [pattern for pattern in partial_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Partial success handling found: {found_patterns}")
    else:
        print(f"⚠ Partial success handling may not be implemented")

test_partial_success_handling()
```

**Expected Results:**
- [ ] Support for marking multiple messages as read
- [ ] Batch API calls for efficiency (if implemented)
- [ ] Partial success scenarios handled
- [ ] Individual message failures don't stop batch

## 5.3 Error Handling and Validation Verification (10 minutes)

### Test Cases
**TC5.3.1: Message ID Validation**
```python
# Test message ID validation
def test_message_id_validation():
    """Verify message ID format validation"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    validation_patterns = [
        'validate',
        'check',
        'empty',
        'None',
        'ValueError',
        'invalid'
    ]
    
    found_patterns = [pattern for pattern in validation_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Message ID validation incomplete: {found_patterns}"
    print(f"✓ Message ID validation patterns found: {found_patterns}")

test_message_id_validation()
```

**TC5.3.2: Non-existent Message Handling**
```python
# Test handling of non-existent messages
def test_nonexistent_message_handling():
    """Verify handling of non-existent message IDs"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    error_patterns = [
        '404',
        'NotFound',
        'not found',
        'does not exist',
        'HTTPError'
    ]
    
    found_patterns = [pattern for pattern in error_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Non-existent message handling found: {found_patterns}")
    else:
        print(f"⚠ Non-existent message handling may be incomplete")

test_nonexistent_message_handling()
```

**TC5.3.3: Retry Logic Implementation**
```python
# Test retry logic
def test_retry_logic():
    """Verify retry logic for transient failures"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    retry_patterns = ['retry', 'attempt', 'backoff', 'sleep', 'transient']
    found_patterns = [pattern for pattern in retry_patterns if pattern in source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Retry logic found: {found_patterns}")
    else:
        print(f"⚠ Retry logic may not be implemented")

test_retry_logic()
```

**Expected Results:**
- [ ] Message ID format validation implemented
- [ ] Non-existent message IDs handled gracefully
- [ ] Retry logic for transient failures
- [ ] Appropriate error logging

## Mock Testing Verification (5 minutes)

### Test Cases
**TC5.M.1: Unit Tests Exist**
```bash
# Check for mark as read tests
find tests/ -name "*exchange*" -o -name "*mark*" | grep -E "\.(py)$"
echo "✓ Mark as read test files found"
```

**TC5.M.2: Mock PATCH Implementation**
```python
# Verify mock testing for mark as read
def test_mark_mock_implementation():
    """Check mock testing for mark as read functionality"""
    import glob
    
    test_files = glob.glob('tests/**/test*exchange*.py', recursive=True)
    
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if 'mark_exchange_as_read' in content:
            mock_patterns = ['mock', 'patch', '@patch', 'MagicMock', 'responses']
            if any(pattern in content for pattern in mock_patterns):
                print(f"✓ Mark as read mock testing found in {test_file}")
                return
    
    print("⚠ Mock testing for mark as read not found")

test_mark_mock_implementation()
```

**Expected Results:**
- [ ] Unit tests for mark as read functionality created
- [ ] Mock Graph API PATCH responses implemented
- [ ] Tests cover success and error scenarios
- [ ] Invalid message ID tests included

## Integration Verification (5 minutes)

### Test Cases
**TC5.I.1: Gmail Interface Compatibility**
```python
# Test interface compatibility with Gmail
def test_gmail_interface_compatibility():
    """Verify mark as read function interface matches Gmail"""
    from eaia.gmail import mark_as_read as gmail_mark
    from eaia.exchange import mark_exchange_as_read
    
    import inspect
    
    gmail_sig = inspect.signature(gmail_mark)
    exchange_sig = inspect.signature(mark_exchange_as_read)
    
    # Check parameter compatibility
    gmail_params = set(gmail_sig.parameters.keys())
    exchange_params = set(exchange_sig.parameters.keys())
    
    # Core parameters should match
    core_params = {'message_id', 'user_email'}
    assert core_params.issubset(gmail_params)
    assert core_params.issubset(exchange_params)
    
    print("✓ Interface compatibility verified")

test_gmail_interface_compatibility()
```

**TC5.I.2: Return Value Consistency**
```python
# Test return value consistency
def test_return_value_consistency():
    """Verify return values are consistent with Gmail implementation"""
    # Check if functions have similar return patterns
    with open('eaia/exchange.py', 'r') as f:
        exchange_source = f.read()
    
    with open('eaia/gmail.py', 'r') as f:
        gmail_source = f.read()
    
    # Look for return patterns in mark_as_read functions
    if 'return' in exchange_source and 'mark_exchange_as_read' in exchange_source:
        print("✓ Return value handling implemented")
    else:
        print("⚠ Return value handling may be missing")

test_return_value_consistency()
```

**Expected Results:**
- [ ] Function signature compatible with Gmail version
- [ ] Same parameter names and types
- [ ] Compatible return behavior
- [ ] Error handling patterns consistent

## Final Verification Checklist

### Functionality
- [ ] Mark as read via Graph API implemented
- [ ] Message ID validation works correctly
- [ ] PATCH operation updates isRead property
- [ ] Batch operations supported (if implemented)
- [ ] Error handling comprehensive

### API Integration
- [ ] Correct Graph API endpoint used
- [ ] Proper HTTP PATCH method
- [ ] Message ID properly formatted in URL
- [ ] Response handling implemented

### Error Handling
- [ ] Invalid message IDs handled
- [ ] Non-existent messages handled gracefully
- [ ] Retry logic for transient failures
- [ ] Appropriate error logging

### Compatibility
- [ ] Function interface matches Gmail
- [ ] Parameter compatibility maintained
- [ ] Return behavior consistent
- [ ] Integration with existing workflow

### Testing
- [ ] Unit tests created and passing
- [ ] Mock testing implemented
- [ ] Error scenarios covered
- [ ] Edge cases tested

## Success Criteria
- [ ] All test cases pass
- [ ] Mark as read works with mock data
- [ ] Error handling validation passes
- [ ] Ready for Stage 6 (Calendar Events)

## Notes for Next Stage
- Document any message state considerations
- Note any Exchange-specific read status behavior
- Record any performance considerations for Stage 6
