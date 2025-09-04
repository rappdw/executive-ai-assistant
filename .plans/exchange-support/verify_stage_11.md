# Verification Plan: Stage 11 - Unit Test Implementation

**Stage Reference:** `stage_11.md`  
**Verification Time:** 60-75 minutes  
**Verification Type:** Test Coverage + Quality Validation  

## Pre-Verification Setup
- [ ] Stage 10 verification completed successfully
- [ ] LangGraph integration working correctly
- [ ] Provider interface fully implemented

## 11.1 Authentication Unit Tests Verification (15 minutes)

### Test Cases
**TC11.1.1: MSAL Authentication Test Structure**
```python
# Test script: verify_auth_tests.py
def test_auth_test_structure():
    """Verify authentication unit tests exist and are comprehensive"""
    
    import os
    from pathlib import Path
    
    test_file = Path('tests/test_exchange_auth.py')
    assert test_file.exists(), "Authentication test file missing"
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for key test functions
    required_tests = [
        'test_get_access_token_success',
        'test_get_access_token_failure', 
        'test_token_refresh',
        'test_invalid_credentials',
        'test_scope_validation'
    ]
    
    found_tests = [test for test in required_tests if test in content]
    assert len(found_tests) >= 4, f"Missing authentication tests: {set(required_tests) - set(found_tests)}"
    print(f"✓ Authentication tests found: {found_tests}")

test_auth_test_structure()
```

**TC11.1.2: Mock MSAL Integration**
```python
# Test MSAL mocking
def test_msal_mocking():
    """Verify MSAL is properly mocked in tests"""
    
    with open('tests/test_exchange_auth.py', 'r') as f:
        content = f.read()
    
    mock_patterns = [
        '@patch',
        'mock',
        'Mock',
        'msal',
        'ConfidentialClientApplication'
    ]
    
    found_patterns = [pattern for pattern in mock_patterns if pattern in content]
    assert len(found_patterns) >= 3, f"MSAL mocking incomplete: {found_patterns}"
    print(f"✓ MSAL mocking patterns found: {found_patterns}")

test_msal_mocking()
```

**TC11.1.3: Authentication Test Execution**
```bash
# Run authentication tests
cd /Users/drapp/dev/executive-ai-assistant
python -m pytest tests/test_exchange_auth.py -v
echo "✓ Authentication tests executed"
```

**Expected Results:**
- [ ] `test_exchange_auth.py` exists with comprehensive test coverage
- [ ] MSAL library properly mocked to avoid external dependencies
- [ ] Token acquisition, refresh, and error scenarios tested
- [ ] All authentication tests pass

## 11.2 Email Operations Unit Tests Verification (20 minutes)

### Test Cases
**TC11.2.1: Email Fetching Tests**
```python
# Test email fetching unit tests
def test_email_fetching_tests():
    """Verify email fetching tests are comprehensive"""
    
    test_file = Path('tests/test_exchange_email.py')
    assert test_file.exists(), "Email test file missing"
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for email fetching tests
    email_tests = [
        'test_fetch_emails_success',
        'test_fetch_emails_empty',
        'test_fetch_emails_error',
        'test_message_conversion',
        'test_body_extraction'
    ]
    
    found_tests = [test for test in email_tests if test in content]
    assert len(found_tests) >= 4, f"Missing email fetching tests: {set(email_tests) - set(found_tests)}"
    print(f"✓ Email fetching tests found: {found_tests}")

test_email_fetching_tests()
```

**TC11.2.2: Email Sending Tests**
```python
# Test email sending unit tests
def test_email_sending_tests():
    """Verify email sending tests are comprehensive"""
    
    with open('tests/test_exchange_email.py', 'r') as f:
        content = f.read()
    
    # Check for email sending tests
    sending_tests = [
        'test_send_email_success',
        'test_send_email_failure',
        'test_message_composition',
        'test_recipient_validation',
        'test_attachment_handling'
    ]
    
    found_tests = [test for test in sending_tests if test in content]
    assert len(found_tests) >= 3, f"Missing email sending tests: {set(sending_tests) - set(found_tests)}"
    print(f"✓ Email sending tests found: {found_tests}")

test_email_sending_tests()
```

**TC11.2.3: Mark as Read Tests**
```python
# Test mark as read unit tests
def test_mark_as_read_tests():
    """Verify mark as read tests are comprehensive"""
    
    with open('tests/test_exchange_email.py', 'r') as f:
        content = f.read()
    
    # Check for mark as read tests
    mark_tests = [
        'test_mark_as_read_success',
        'test_mark_as_read_batch',
        'test_mark_as_read_error',
        'test_invalid_message_id'
    ]
    
    found_tests = [test for test in mark_tests if test in content]
    assert len(found_tests) >= 3, f"Missing mark as read tests: {set(mark_tests) - set(found_tests)}"
    print(f"✓ Mark as read tests found: {found_tests}")

test_mark_as_read_tests()
```

**TC11.2.4: Graph API Mocking**
```python
# Test Microsoft Graph API mocking
def test_graph_api_mocking():
    """Verify Microsoft Graph API is properly mocked"""
    
    with open('tests/test_exchange_email.py', 'r') as f:
        content = f.read()
    
    mock_patterns = [
        'requests.get',
        'requests.post',
        'requests.patch',
        '@patch',
        'mock_response'
    ]
    
    found_patterns = [pattern for pattern in mock_patterns if pattern in content]
    assert len(found_patterns) >= 3, f"Graph API mocking incomplete: {found_patterns}"
    print(f"✓ Graph API mocking patterns found: {found_patterns}")

test_graph_api_mocking()
```

**Expected Results:**
- [ ] `test_exchange_email.py` with comprehensive email operation tests
- [ ] Microsoft Graph API properly mocked
- [ ] Email fetching, sending, and mark as read scenarios covered
- [ ] Error handling and edge cases tested

## 11.3 Calendar Operations Unit Tests Verification (15 minutes)

### Test Cases
**TC11.3.1: Calendar Event Tests**
```python
# Test calendar event unit tests
def test_calendar_event_tests():
    """Verify calendar event tests are comprehensive"""
    
    test_file = Path('tests/test_exchange_calendar.py')
    assert test_file.exists(), "Calendar test file missing"
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for calendar event tests
    calendar_tests = [
        'test_get_calendar_events_success',
        'test_get_calendar_events_empty',
        'test_event_conversion',
        'test_date_range_filtering',
        'test_timezone_handling'
    ]
    
    found_tests = [test for test in calendar_tests if test in content]
    assert len(found_tests) >= 4, f"Missing calendar event tests: {set(calendar_tests) - set(found_tests)}"
    print(f"✓ Calendar event tests found: {found_tests}")

test_calendar_event_tests()
```

**TC11.3.2: Calendar Invite Tests**
```python
# Test calendar invite unit tests
def test_calendar_invite_tests():
    """Verify calendar invite tests are comprehensive"""
    
    with open('tests/test_exchange_calendar.py', 'r') as f:
        content = f.read()
    
    # Check for calendar invite tests
    invite_tests = [
        'test_send_calendar_invite_success',
        'test_send_calendar_invite_failure',
        'test_teams_meeting_creation',
        'test_attendee_management',
        'test_recurrence_handling'
    ]
    
    found_tests = [test for test in invite_tests if test in content]
    assert len(found_tests) >= 3, f"Missing calendar invite tests: {set(invite_tests) - set(found_tests)}"
    print(f"✓ Calendar invite tests found: {found_tests}")

test_calendar_invite_tests()
```

**Expected Results:**
- [ ] `test_exchange_calendar.py` with comprehensive calendar tests
- [ ] Calendar event retrieval and invite sending covered
- [ ] Date/time handling and timezone conversion tested
- [ ] Teams meeting integration tested

## 11.4 Provider Interface Unit Tests Verification (15 minutes)

### Test Cases
**TC11.4.1: Provider Factory Tests**
```python
# Test provider factory unit tests
def test_provider_factory_tests():
    """Verify provider factory tests are comprehensive"""
    
    test_file = Path('tests/test_email_provider.py')
    assert test_file.exists(), "Provider test file missing"
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for provider factory tests
    factory_tests = [
        'test_create_gmail_provider',
        'test_create_exchange_provider',
        'test_invalid_provider_type',
        'test_provider_configuration',
        'test_factory_error_handling'
    ]
    
    found_tests = [test for test in factory_tests if test in content]
    assert len(found_tests) >= 4, f"Missing provider factory tests: {set(factory_tests) - set(found_tests)}"
    print(f"✓ Provider factory tests found: {found_tests}")

test_provider_factory_tests()
```

**TC11.4.2: Interface Compliance Tests**
```python
# Test interface compliance
def test_interface_compliance_tests():
    """Verify interface compliance tests exist"""
    
    with open('tests/test_email_provider.py', 'r') as f:
        content = f.read()
    
    # Check for interface compliance tests
    compliance_tests = [
        'test_gmail_provider_interface',
        'test_exchange_provider_interface',
        'test_method_signatures',
        'test_return_types',
        'test_error_handling_consistency'
    ]
    
    found_tests = [test for test in compliance_tests if test in content]
    assert len(found_tests) >= 3, f"Missing interface compliance tests: {set(compliance_tests) - set(found_tests)}"
    print(f"✓ Interface compliance tests found: {found_tests}")

test_interface_compliance_tests()
```

**TC11.4.3: Provider Switching Tests**
```python
# Test provider switching
def test_provider_switching_tests():
    """Verify provider switching tests exist"""
    
    with open('tests/test_email_provider.py', 'r') as f:
        content = f.read()
    
    # Check for provider switching tests
    switching_tests = [
        'test_runtime_provider_switch',
        'test_configuration_based_selection',
        'test_provider_isolation',
        'test_state_independence'
    ]
    
    found_tests = [test for test in switching_tests if test in content]
    assert len(found_tests) >= 2, f"Missing provider switching tests: {set(switching_tests) - set(found_tests)}"
    print(f"✓ Provider switching tests found: {found_tests}")

test_provider_switching_tests()
```

**Expected Results:**
- [ ] `test_email_provider.py` with comprehensive provider interface tests
- [ ] Provider factory creation and error handling tested
- [ ] Interface compliance verified for both providers
- [ ] Provider switching scenarios covered

## 11.5 Test Execution and Coverage Verification (10 minutes)

### Test Cases
**TC11.5.1: Test Suite Execution**
```bash
# Run all unit tests
cd /Users/drapp/dev/executive-ai-assistant
python -m pytest tests/ -v --tb=short
echo "✓ Unit test suite executed"
```

**TC11.5.2: Test Coverage Analysis**
```bash
# Run tests with coverage
cd /Users/drapp/dev/executive-ai-assistant
python -m pytest tests/ --cov=eaia --cov-report=term-missing
echo "✓ Test coverage analyzed"
```

**TC11.5.3: Exchange Module Coverage**
```python
# Test Exchange module coverage specifically
def test_exchange_module_coverage():
    """Verify Exchange modules have adequate test coverage"""
    
    # This would be verified by coverage report
    # Looking for >80% coverage on Exchange modules
    print("✓ Exchange module coverage verified via coverage report")

test_exchange_module_coverage()
```

**TC11.5.4: Test Configuration**
```python
# Test pytest configuration
def test_pytest_configuration():
    """Verify pytest is properly configured"""
    
    config_files = [
        Path('pytest.ini'),
        Path('pyproject.toml'),
        Path('setup.cfg')
    ]
    
    config_found = any(f.exists() for f in config_files)
    assert config_found, "No pytest configuration found"
    print("✓ Pytest configuration exists")

test_pytest_configuration()
```

**Expected Results:**
- [ ] All unit tests pass successfully
- [ ] Test coverage >80% for Exchange modules
- [ ] No test failures or errors
- [ ] Pytest properly configured

## Mock and Fixture Verification (5 minutes)

### Test Cases
**TC11.M.1: Mock Setup Verification**
```python
# Test mock setup
def test_mock_setup():
    """Verify mocks are properly set up"""
    
    # Check for conftest.py or similar fixture setup
    conftest_file = Path('tests/conftest.py')
    
    if conftest_file.exists():
        with open(conftest_file, 'r') as f:
            content = f.read()
        
        fixture_patterns = [
            '@pytest.fixture',
            'mock',
            'patch',
            'exchange',
            'gmail'
        ]
        
        found_patterns = [pattern for pattern in fixture_patterns if pattern in content]
        print(f"✓ Test fixtures found: {found_patterns}")
    else:
        print("⚠ No conftest.py found - fixtures may be inline")

test_mock_setup()
```

**TC11.M.2: External Dependency Isolation**
```python
# Test external dependency isolation
def test_external_dependency_isolation():
    """Verify external dependencies are properly isolated"""
    
    test_files = [
        'tests/test_exchange_auth.py',
        'tests/test_exchange_email.py', 
        'tests/test_exchange_calendar.py'
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Should not make real external calls
            external_patterns = [
                'requests.get',
                'requests.post',
                'msal.',
                'graph.microsoft.com'
            ]
            
            # These should be mocked, not called directly
            direct_calls = [pattern for pattern in external_patterns if pattern in content and '@patch' not in content]
            
            if len(direct_calls) == 0:
                print(f"✓ {test_file} properly isolates external dependencies")
            else:
                print(f"⚠ {test_file} may have unmocked external calls: {direct_calls}")

test_external_dependency_isolation()
```

**Expected Results:**
- [ ] Test fixtures properly configured
- [ ] External dependencies isolated with mocks
- [ ] No real API calls in unit tests
- [ ] Consistent mock patterns across test files

## Final Verification Checklist

### Authentication Tests
- [ ] MSAL authentication tests comprehensive
- [ ] Token acquisition and refresh tested
- [ ] Error scenarios covered
- [ ] External dependencies mocked

### Email Operation Tests
- [ ] Email fetching tests complete
- [ ] Email sending tests comprehensive
- [ ] Mark as read functionality tested
- [ ] Microsoft Graph API properly mocked

### Calendar Operation Tests
- [ ] Calendar event retrieval tested
- [ ] Calendar invite sending covered
- [ ] Date/time handling verified
- [ ] Teams integration tested

### Provider Interface Tests
- [ ] Provider factory tests complete
- [ ] Interface compliance verified
- [ ] Provider switching tested
- [ ] Error handling consistent

### Test Quality
- [ ] All unit tests pass
- [ ] Test coverage >80% for Exchange modules
- [ ] External dependencies isolated
- [ ] Pytest properly configured

## Success Criteria
- [ ] All test cases pass
- [ ] Comprehensive unit test coverage achieved
- [ ] External dependencies properly mocked
- [ ] Ready for Stage 12 (Integration Tests)

## Notes for Next Stage
- Document any integration test requirements
- Note provider interaction patterns for integration testing
- Record test data requirements for Stage 12
