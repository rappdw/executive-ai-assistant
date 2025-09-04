# Verification Plan: Stage 8 - Email Provider Interface Design

**Stage Reference:** `stage_8.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Architecture Validation + Interface Compliance Testing  

## Pre-Verification Setup
- [ ] Stage 7 verification completed successfully
- [ ] All Exchange functions from Stages 2-7 implemented
- [ ] Gmail functionality preserved and working

## 8.1 Abstract Base Interface Design Verification (20 minutes)

### Test Cases
**TC8.1.1: Interface Module Creation**
```python
# Test script: test_email_provider_interface.py
def test_interface_module_exists():
    """Verify email provider interface module exists"""
    try:
        from eaia.email_provider import EmailInterface, EmailProvider, EmailProviderFactory
        print("✓ Email provider interface module exists")
    except ImportError as e:
        assert False, f"Email provider interface module missing: {e}"

test_interface_module_exists()
```

**TC8.1.2: EmailProvider Enum Verification**
```python
# Test EmailProvider enum
def test_email_provider_enum():
    """Verify EmailProvider enum is properly defined"""
    from eaia.email_provider import EmailProvider
    
    # Check enum values
    assert hasattr(EmailProvider, 'GMAIL')
    assert hasattr(EmailProvider, 'EXCHANGE')
    assert EmailProvider.GMAIL.value == "gmail"
    assert EmailProvider.EXCHANGE.value == "exchange"
    
    print("✓ EmailProvider enum correctly defined")

test_email_provider_enum()
```

**TC8.1.3: Abstract Interface Definition**
```python
# Test abstract interface
def test_abstract_interface():
    """Verify EmailInterface abstract base class is properly defined"""
    from eaia.email_provider import EmailInterface
    import inspect
    
    # Check it's abstract
    assert inspect.isabstract(EmailInterface)
    
    # Check required methods exist
    required_methods = [
        'fetch_emails',
        'send_email', 
        'mark_as_read',
        'get_events_for_days',
        'send_calendar_invite'
    ]
    
    interface_methods = [method for method in dir(EmailInterface) if not method.startswith('_')]
    
    for method in required_methods:
        assert method in interface_methods, f"Missing required method: {method}"
    
    print("✓ EmailInterface abstract base class correctly defined")

test_abstract_interface()
```

**TC8.1.4: Method Signatures Verification**
```python
# Test method signatures
def test_interface_method_signatures():
    """Verify abstract method signatures are correct"""
    from eaia.email_provider import EmailInterface
    import inspect
    
    # Check fetch_emails signature
    fetch_sig = inspect.signature(EmailInterface.fetch_emails)
    fetch_params = list(fetch_sig.parameters.keys())
    expected_fetch = ['self', 'user_email', 'minutes_since']
    assert all(param in fetch_params for param in expected_fetch)
    
    # Check send_email signature
    send_sig = inspect.signature(EmailInterface.send_email)
    send_params = list(send_sig.parameters.keys())
    expected_send = ['self', 'email_id', 'response_text', 'user_email']
    assert all(param in expected_send for param in send_params[:4])
    
    print("✓ Interface method signatures correct")

test_interface_method_signatures()
```

**Expected Results:**
- [ ] `eaia/email_provider.py` module created
- [ ] `EmailInterface` abstract base class defined
- [ ] `EmailProvider` enum with GMAIL and EXCHANGE values
- [ ] All required abstract methods defined with correct signatures
- [ ] Proper use of ABC and abstractmethod decorators

## 8.2 Gmail Provider Implementation Verification (15 minutes)

### Test Cases
**TC8.2.1: Gmail Provider Class**
```python
# Test Gmail provider implementation
def test_gmail_provider_class():
    """Verify GmailProvider implements EmailInterface"""
    from eaia.email_provider import EmailInterface, GmailProvider
    
    # Check inheritance
    assert issubclass(GmailProvider, EmailInterface)
    
    # Check it's not abstract
    import inspect
    assert not inspect.isabstract(GmailProvider)
    
    print("✓ GmailProvider class correctly implements EmailInterface")

test_gmail_provider_class()
```

**TC8.2.2: Gmail Method Implementation**
```python
# Test Gmail methods are implemented
def test_gmail_method_implementation():
    """Verify all Gmail methods are implemented"""
    from eaia.email_provider import GmailProvider
    
    provider = GmailProvider()
    
    # Check all required methods exist and are callable
    required_methods = [
        'fetch_emails',
        'send_email',
        'mark_as_read', 
        'get_events_for_days',
        'send_calendar_invite'
    ]
    
    for method in required_methods:
        assert hasattr(provider, method), f"Missing method: {method}"
        assert callable(getattr(provider, method)), f"Method not callable: {method}"
    
    print("✓ All Gmail provider methods implemented")

test_gmail_method_implementation()
```

**TC8.2.3: Gmail Function Wrapping**
```python
# Test Gmail functions are properly wrapped
def test_gmail_function_wrapping():
    """Verify Gmail functions are wrapped without breaking functionality"""
    
    # Check that original Gmail functions still exist
    from eaia import gmail
    
    gmail_functions = [
        'fetch_group_emails',
        'send_email',
        'mark_as_read',
        'get_events_for_days', 
        'send_calendar_invite'
    ]
    
    for func_name in gmail_functions:
        assert hasattr(gmail, func_name), f"Original Gmail function missing: {func_name}"
    
    print("✓ Original Gmail functions preserved")

test_gmail_function_wrapping()
```

**Expected Results:**
- [ ] `GmailProvider` class implements `EmailInterface`
- [ ] All abstract methods implemented
- [ ] Gmail functions wrapped without breaking changes
- [ ] No regressions in existing Gmail functionality

## 8.3 Exchange Provider Implementation Verification (15 minutes)

### Test Cases
**TC8.3.1: Exchange Provider Class**
```python
# Test Exchange provider implementation
def test_exchange_provider_class():
    """Verify ExchangeProvider implements EmailInterface"""
    from eaia.email_provider import EmailInterface, ExchangeProvider
    
    # Check inheritance
    assert issubclass(ExchangeProvider, EmailInterface)
    
    # Check it's not abstract
    import inspect
    assert not inspect.isabstract(ExchangeProvider)
    
    print("✓ ExchangeProvider class correctly implements EmailInterface")

test_exchange_provider_class()
```

**TC8.3.2: Exchange Method Implementation**
```python
# Test Exchange methods are implemented
def test_exchange_method_implementation():
    """Verify all Exchange methods are implemented"""
    from eaia.email_provider import ExchangeProvider
    
    provider = ExchangeProvider()
    
    # Check all required methods exist and are callable
    required_methods = [
        'fetch_emails',
        'send_email',
        'mark_as_read',
        'get_events_for_days', 
        'send_calendar_invite'
    ]
    
    for method in required_methods:
        assert hasattr(provider, method), f"Missing method: {method}"
        assert callable(getattr(provider, method)), f"Method not callable: {method}"
    
    print("✓ All Exchange provider methods implemented")

test_exchange_method_implementation()
```

**TC8.3.3: Exchange Function Integration**
```python
# Test Exchange functions are properly integrated
def test_exchange_function_integration():
    """Verify Exchange functions are integrated into provider"""
    
    # Check that Exchange functions exist
    from eaia import exchange
    
    exchange_functions = [
        'fetch_exchange_emails',
        'send_exchange_email', 
        'mark_exchange_as_read',
        'get_exchange_events_for_days',
        'send_exchange_calendar_invite'
    ]
    
    for func_name in exchange_functions:
        assert hasattr(exchange, func_name), f"Exchange function missing: {func_name}"
    
    print("✓ Exchange functions properly integrated")

test_exchange_function_integration()
```

**Expected Results:**
- [ ] `ExchangeProvider` class implements `EmailInterface`
- [ ] All abstract methods implemented
- [ ] Exchange functions from Stages 2-7 wrapped properly
- [ ] Provider-specific configuration handled

## 8.4 Provider Factory Pattern Verification (10 minutes)

### Test Cases
**TC8.4.1: Factory Class Implementation**
```python
# Test provider factory
def test_provider_factory():
    """Verify EmailProviderFactory is implemented"""
    from eaia.email_provider import EmailProviderFactory
    
    # Check factory methods exist
    assert hasattr(EmailProviderFactory, 'create_provider')
    assert callable(EmailProviderFactory.create_provider)
    
    print("✓ EmailProviderFactory implemented")

test_provider_factory()
```

**TC8.4.2: Provider Instantiation**
```python
# Test provider creation
def test_provider_instantiation():
    """Verify factory can create both provider types"""
    from eaia.email_provider import EmailProviderFactory, EmailProvider, GmailProvider, ExchangeProvider
    
    # Mock configuration for testing
    gmail_config = {'configurable': {'email_provider': 'gmail'}}
    exchange_config = {'configurable': {'email_provider': 'exchange'}}
    
    # Test Gmail provider creation
    gmail_provider = EmailProviderFactory.create_provider(gmail_config)
    assert isinstance(gmail_provider, GmailProvider)
    
    # Test Exchange provider creation  
    exchange_provider = EmailProviderFactory.create_provider(exchange_config)
    assert isinstance(exchange_provider, ExchangeProvider)
    
    print("✓ Provider factory creates correct provider types")

test_provider_instantiation()
```

**TC8.4.3: Configuration Validation**
```python
# Test configuration validation
def test_configuration_validation():
    """Verify factory validates provider configuration"""
    from eaia.email_provider import EmailProviderFactory
    
    # Test invalid configuration
    invalid_config = {'configurable': {'email_provider': 'invalid'}}
    
    try:
        EmailProviderFactory.create_provider(invalid_config)
        assert False, "Should have raised error for invalid provider"
    except (ValueError, KeyError) as e:
        print("✓ Configuration validation works")

test_configuration_validation()
```

**Expected Results:**
- [ ] `EmailProviderFactory` class implemented
- [ ] Provider instantiation based on configuration works
- [ ] Configuration validation implemented
- [ ] Provider switching logic handles both types

## Interface Compliance Testing (5 minutes)

### Test Cases
**TC8.C.1: Interface Compliance**
```python
# Test interface compliance
def test_interface_compliance():
    """Verify both providers fully comply with interface"""
    from eaia.email_provider import EmailInterface, GmailProvider, ExchangeProvider
    import inspect
    
    # Get interface methods
    interface_methods = [method for method in dir(EmailInterface) 
                        if not method.startswith('_') and callable(getattr(EmailInterface, method))]
    
    # Test Gmail provider compliance
    gmail_provider = GmailProvider()
    for method in interface_methods:
        assert hasattr(gmail_provider, method), f"Gmail missing method: {method}"
        
    # Test Exchange provider compliance  
    exchange_provider = ExchangeProvider()
    for method in interface_methods:
        assert hasattr(exchange_provider, method), f"Exchange missing method: {method}"
    
    print("✓ Both providers comply with interface")

test_interface_compliance()
```

**Expected Results:**
- [ ] Both providers implement all interface methods
- [ ] Method signatures match interface definition
- [ ] No missing or extra methods
- [ ] Interface contract fully satisfied

## Final Verification Checklist

### Interface Design
- [ ] Abstract base class properly defined
- [ ] All required methods declared as abstract
- [ ] Method signatures correct and consistent
- [ ] EmailProvider enum properly defined

### Gmail Provider
- [ ] Implements EmailInterface completely
- [ ] Wraps existing Gmail functions correctly
- [ ] No breaking changes to Gmail functionality
- [ ] Error handling consistent with interface

### Exchange Provider  
- [ ] Implements EmailInterface completely
- [ ] Integrates Exchange functions from previous stages
- [ ] Provider-specific configuration handled
- [ ] Error handling consistent with interface

### Factory Pattern
- [ ] EmailProviderFactory creates correct providers
- [ ] Configuration-based provider selection works
- [ ] Validation for provider-specific requirements
- [ ] Provider switching logic implemented

### Compatibility
- [ ] Both providers interchangeable through interface
- [ ] Consistent error handling patterns
- [ ] Same method signatures and return types
- [ ] No provider-specific leakage in interface

## Success Criteria
- [ ] All test cases pass
- [ ] Interface abstraction complete
- [ ] Both providers fully compliant
- [ ] Ready for Stage 9 (Configuration Updates)

## Notes for Next Stage
- Document provider selection patterns for configuration
- Note any interface design decisions for Stage 9
- Record factory patterns for LangGraph integration
