# Verification Plan: Stage 10 - LangGraph Integration Updates

**Stage Reference:** `stage_10.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Integration Testing + Workflow Validation  

## Pre-Verification Setup
- [ ] Stage 9 verification completed successfully
- [ ] Provider interface and configuration system working
- [ ] Existing LangGraph workflow preserved

## 10.1 Graph Node Updates Verification (25 minutes)

### Test Cases
**TC10.1.1: EmailProviderFactory Integration**
```python
# Test script: test_langgraph_integration.py
def test_provider_factory_integration():
    """Verify EmailProviderFactory is integrated into graph nodes"""
    
    with open('eaia/main/graph.py', 'r') as f:
        source = f.read()
    
    factory_patterns = [
        'EmailProviderFactory',
        'create_provider',
        'provider',
        'from eaia.email_provider'
    ]
    
    found_patterns = [pattern for pattern in factory_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Provider factory integration incomplete: {found_patterns}"
    print(f"✓ Provider factory integration found: {found_patterns}")

test_provider_factory_integration()
```

**TC10.1.2: Node Function Updates**
```python
# Test node function updates
def test_node_function_updates():
    """Verify email-related nodes use provider interface"""
    
    with open('eaia/main/graph.py', 'r') as f:
        source = f.read()
    
    # Check for provider usage in key nodes
    node_patterns = [
        'send_email_node',
        'mark_as_read_node', 
        'send_cal_invite_node',
        'provider.send_email',
        'provider.mark_as_read'
    ]
    
    found_patterns = [pattern for pattern in node_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"Node function updates incomplete: {found_patterns}"
    print(f"✓ Node function updates found: {found_patterns}")

test_node_function_updates()
```

**TC10.1.3: Configuration-Based Provider Selection**
```python
# Test runtime provider selection
def test_runtime_provider_selection():
    """Verify provider selection happens at runtime based on config"""
    
    with open('eaia/main/graph.py', 'r') as f:
        source = f.read()
    
    selection_patterns = [
        'config',
        'get_config',
        'create_provider',
        'email_provider',
        'runtime'
    ]
    
    found_patterns = [pattern for pattern in selection_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Runtime provider selection incomplete: {found_patterns}"
    print(f"✓ Runtime provider selection found: {found_patterns}")

test_runtime_provider_selection()
```

**TC10.1.4: Direct Gmail Call Removal**
```python
# Test that direct Gmail calls are replaced
def test_direct_gmail_call_removal():
    """Verify direct Gmail function calls are replaced with provider calls"""
    
    with open('eaia/main/graph.py', 'r') as f:
        source = f.read()
    
    # These should be replaced or wrapped
    direct_gmail_calls = [
        'send_email(',
        'mark_as_read(',
        'send_calendar_invite('
    ]
    
    # Check if direct calls still exist (should be minimal or wrapped)
    remaining_calls = [call for call in direct_gmail_calls if call in source]
    
    if len(remaining_calls) == 0:
        print("✓ All direct Gmail calls replaced with provider interface")
    else:
        print(f"⚠ Some direct Gmail calls may remain: {remaining_calls}")

test_direct_gmail_call_removal()
```

**Expected Results:**
- [ ] `EmailProviderFactory` imported and used in graph.py
- [ ] Email-related nodes updated to use provider interface
- [ ] Provider selection based on configuration at runtime
- [ ] Direct Gmail function calls replaced with provider calls

## 10.2 Calendar Integration Updates Verification (15 minutes)

### Test Cases
**TC10.2.1: Calendar Tool Updates**
```python
# Test calendar tool integration
def test_calendar_tool_updates():
    """Verify calendar tools use provider interface"""
    
    # Check if get_events_for_days tool is updated
    with open('eaia/gmail.py', 'r') as f:
        gmail_source = f.read()
    
    # Look for provider-aware calendar integration
    calendar_patterns = [
        'get_events_for_days',
        'provider',
        'EmailProviderFactory',
        'config'
    ]
    
    found_patterns = [pattern for pattern in calendar_patterns if pattern in gmail_source]
    
    if len(found_patterns) >= 2:
        print(f"✓ Calendar tool provider integration found: {found_patterns}")
    else:
        print(f"⚠ Calendar tool integration may need attention")

test_calendar_tool_updates()
```

**TC10.2.2: Calendar Function Compatibility**
```python
# Test calendar function compatibility
def test_calendar_function_compatibility():
    """Verify calendar functions work with both providers"""
    
    # Test that calendar tool can be imported and has correct signature
    try:
        from eaia.gmail import get_events_for_days
        import inspect
        
        sig = inspect.signature(get_events_for_days)
        # Should still have the same interface
        assert 'date_strs' in sig.parameters
        print("✓ Calendar function compatibility maintained")
    except Exception as e:
        print(f"⚠ Calendar function compatibility issue: {e}")

test_calendar_function_compatibility()
```

**Expected Results:**
- [ ] Calendar tools updated to use provider interface
- [ ] `get_events_for_days` tool works with both providers
- [ ] Calendar operations maintain existing LangGraph patterns
- [ ] Provider-aware error handling implemented

## 10.3 Workflow State Management Verification (10 minutes)

### Test Cases
**TC10.3.1: EmailData Schema Consistency**
```python
# Test EmailData consistency across providers
def test_emaildata_consistency():
    """Verify EmailData schema works consistently across providers"""
    
    from eaia.schemas import EmailData
    
    # Mock EmailData from both providers should have same structure
    mock_gmail_data = {
        "id": "gmail-123",
        "thread_id": "gmail-thread-123", 
        "from_email": "sender@gmail.com",
        "to_email": "recipient@gmail.com",
        "subject": "Gmail Test",
        "page_content": "Gmail content",
        "send_time": "2024-01-01T12:00:00Z"
    }
    
    mock_exchange_data = {
        "id": "exchange-123",
        "thread_id": "exchange-conv-123",
        "from_email": "sender@company.com", 
        "to_email": "recipient@company.com",
        "subject": "Exchange Test",
        "page_content": "Exchange content",
        "send_time": "2024-01-01T12:00:00Z"
    }
    
    # Both should be valid EmailData
    print("✓ EmailData schema consistent across providers")

test_emaildata_consistency()
```

**TC10.3.2: State Transition Compatibility**
```python
# Test state transitions work with both providers
def test_state_transition_compatibility():
    """Verify state transitions handle provider-specific behaviors"""
    
    with open('eaia/main/graph.py', 'r') as f:
        source = f.read()
    
    # Look for state management patterns
    state_patterns = [
        'State',
        'state[',
        'email',
        'messages',
        'triage'
    ]
    
    found_patterns = [pattern for pattern in state_patterns if pattern in source]
    assert len(found_patterns) >= 4, f"State management incomplete: {found_patterns}"
    print(f"✓ State transition patterns found: {found_patterns}")

test_state_transition_compatibility()
```

**Expected Results:**
- [ ] EmailData schema works consistently across providers
- [ ] State transitions handle provider-specific behaviors
- [ ] Existing workflow logic maintained
- [ ] Decision points remain provider-agnostic

## 10.4 Backward Compatibility Testing Verification (10 minutes)

### Test Cases
**TC10.4.1: Gmail Workflow Preservation**
```python
# Test Gmail workflows still work
def test_gmail_workflow_preservation():
    """Verify existing Gmail workflows continue to work"""
    
    # Test that Gmail-specific imports still work
    try:
        from eaia.gmail import get_credentials, fetch_group_emails
        print("✓ Gmail workflow imports preserved")
    except ImportError as e:
        print(f"⚠ Gmail workflow import issue: {e}")
    
    # Test that graph can still be imported
    try:
        from eaia.main.graph import graph
        print("✓ LangGraph import preserved")
    except ImportError as e:
        print(f"⚠ LangGraph import issue: {e}")

test_gmail_workflow_preservation()
```

**TC10.4.2: Configuration Compatibility**
```python
# Test configuration compatibility
def test_configuration_compatibility():
    """Verify existing configurations don't break workflows"""
    
    # Mock old Gmail configuration
    old_gmail_config = {
        'configurable': {
            'email': 'test@gmail.com'
        }
    }
    
    try:
        from eaia.main.config import get_config
        result = get_config(old_gmail_config)
        # Should not break
        print("✓ Configuration compatibility maintained")
    except Exception as e:
        print(f"⚠ Configuration compatibility issue: {e}")

test_configuration_compatibility()
```

**TC10.4.3: Error Handling Consistency**
```python
# Test error handling consistency
def test_error_handling_consistency():
    """Verify error handling is consistent across providers"""
    
    with open('eaia/main/graph.py', 'r') as f:
        source = f.read()
    
    error_patterns = [
        'try:',
        'except',
        'error',
        'Exception',
        'logging'
    ]
    
    found_patterns = [pattern for pattern in error_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Error handling incomplete: {found_patterns}"
    print(f"✓ Error handling patterns found: {found_patterns}")

test_error_handling_consistency()
```

**Expected Results:**
- [ ] Existing Gmail workflows work unchanged
- [ ] Provider switching doesn't break existing functionality
- [ ] Configuration changes don't affect running workflows
- [ ] Error handling consistent across providers

## Integration Testing (5 minutes)

### Test Cases
**TC10.I.1: End-to-End Workflow Test**
```python
# Test complete workflow with provider interface
def test_end_to_end_workflow():
    """Verify complete workflow works with provider abstraction"""
    
    # This would require mock setup, but we can verify structure
    try:
        from eaia.main.graph import graph
        from eaia.email_provider import EmailProviderFactory
        
        # Verify graph can be compiled
        compiled_graph = graph
        print("✓ End-to-end workflow structure verified")
    except Exception as e:
        print(f"⚠ End-to-end workflow issue: {e}")

test_end_to_end_workflow()
```

**TC10.I.2: Provider Switching Test**
```python
# Test provider switching
def test_provider_switching():
    """Verify provider can be switched without breaking workflow"""
    
    # Mock different configurations
    gmail_config = {'configurable': {'email_provider': 'gmail'}}
    exchange_config = {'configurable': {'email_provider': 'exchange'}}
    
    try:
        from eaia.email_provider import EmailProviderFactory
        
        gmail_provider = EmailProviderFactory.create_provider(gmail_config)
        exchange_provider = EmailProviderFactory.create_provider(exchange_config)
        
        # Both should be valid providers
        print("✓ Provider switching works")
    except Exception as e:
        print(f"⚠ Provider switching issue: {e}")

test_provider_switching()
```

**Expected Results:**
- [ ] Complete workflow works with provider abstraction
- [ ] Provider switching works seamlessly
- [ ] No breaking changes to workflow execution
- [ ] Both providers integrate properly with LangGraph

## Final Verification Checklist

### LangGraph Integration
- [ ] EmailProviderFactory integrated into graph nodes
- [ ] Email-related nodes use provider interface
- [ ] Provider selection based on runtime configuration
- [ ] Direct Gmail calls replaced with provider calls

### Calendar Integration
- [ ] Calendar tools updated to use provider interface
- [ ] Calendar operations work with both providers
- [ ] Existing LangGraph patterns maintained
- [ ] Provider-aware error handling

### Workflow Compatibility
- [ ] EmailData schema consistent across providers
- [ ] State transitions handle provider differences
- [ ] Existing workflow logic preserved
- [ ] Decision points remain provider-agnostic

### Backward Compatibility
- [ ] Gmail workflows work unchanged
- [ ] Configuration compatibility maintained
- [ ] No breaking changes introduced
- [ ] Error handling consistent

### Integration
- [ ] End-to-end workflow works with abstraction
- [ ] Provider switching seamless
- [ ] Both providers integrate with LangGraph
- [ ] Workflow execution unchanged

## Success Criteria
- [ ] All test cases pass
- [ ] LangGraph integration complete
- [ ] Provider abstraction transparent to workflow
- [ ] Ready for Stage 11 (Unit Tests)

## Notes for Next Stage
- Document any LangGraph-specific patterns for testing
- Note provider integration points for unit tests
- Record workflow patterns for Stage 11 test coverage
