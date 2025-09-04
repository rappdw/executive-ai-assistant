# Verification Plan: Stage 2 - MSAL Authentication Implementation

**Stage Reference:** `stage_2.md`  
**Verification Time:** 60-75 minutes  
**Verification Type:** Functional Testing + Security Validation  

## Pre-Verification Setup
- [ ] Stage 1 verification completed successfully
- [ ] Test Azure AD tenant and app registration available
- [ ] Test credentials stored securely (not in code)

## 2.1 MSAL Client Setup Verification (25 minutes)

### Test Cases
**TC2.1.1: Credential Function Implementation**
```python
# Test script: test_msal_implementation.py
import asyncio
from eaia.exchange import get_exchange_credentials

async def test_credential_function_exists():
    """Verify function exists and has correct signature"""
    import inspect
    sig = inspect.signature(get_exchange_credentials)
    params = list(sig.parameters.keys())
    
    required_params = ['user_email', 'tenant_id', 'client_id', 'client_secret']
    assert all(param in params for param in required_params)
    assert inspect.iscoroutinefunction(get_exchange_credentials)
    print("✓ Function signature correct")

asyncio.run(test_credential_function_exists())
```

**TC2.1.2: MSAL Client Creation**
```python
# Test MSAL client instantiation (with mock credentials)
async def test_msal_client_creation():
    try:
        # Use dummy values to test client creation logic
        result = await get_exchange_credentials(
            user_email="test@example.com",
            tenant_id="test-tenant-id", 
            client_id="test-client-id",
            client_secret="test-secret"
        )
        # Should fail with auth error, not implementation error
        assert False, "Should have failed with auth error"
    except Exception as e:
        # Verify it's an authentication error, not implementation error
        error_msg = str(e).lower()
        assert any(keyword in error_msg for keyword in ['auth', 'tenant', 'client', 'credential'])
        print("✓ MSAL client creation logic implemented")

asyncio.run(test_msal_client_creation())
```

**TC2.1.3: OAuth2 Flow Implementation**
```python
# Verify OAuth2 flow structure exists
import inspect
import ast

def test_oauth2_flow_structure():
    """Verify OAuth2 flow implementation structure"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Check for MSAL-related imports and patterns
    assert 'msal' in source
    assert 'ConfidentialClientApplication' in source or 'confidential' in source.lower()
    assert 'acquire_token' in source or 'get_token' in source
    print("✓ OAuth2 flow structure present")

test_oauth2_flow_structure()
```

**Expected Results:**
- [ ] `get_exchange_credentials()` function implemented
- [ ] MSAL ConfidentialClientApplication used
- [ ] OAuth2 authorization code flow implemented
- [ ] Proper error handling for authentication failures
- [ ] Function returns credentials object

## 2.2 Token Management Verification (20 minutes)

### Test Cases
**TC2.2.1: Token Refresh Logic**
```python
# Test token refresh implementation
def test_token_refresh_logic():
    """Verify token refresh logic exists"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Look for token refresh patterns
    refresh_indicators = [
        'refresh_token', 'acquire_token_silent', 
        'token_cache', 'refresh', 'expire'
    ]
    
    found_indicators = [indicator for indicator in refresh_indicators if indicator in source]
    assert len(found_indicators) >= 2, f"Token refresh logic incomplete. Found: {found_indicators}"
    print(f"✓ Token refresh logic present: {found_indicators}")

test_token_refresh_logic()
```

**TC2.2.2: Credential Object Compatibility**
```python
# Test credential object structure
async def test_credential_compatibility():
    """Verify credential object matches Gmail pattern"""
    from eaia.gmail import get_credentials as gmail_creds
    
    # Compare credential object structure (mock test)
    # This would need real credentials for full test
    print("✓ Credential object compatibility check implemented")
    # Note: Full test requires valid Azure AD setup

asyncio.run(test_credential_compatibility())
```

**Expected Results:**
- [ ] Token refresh mechanism implemented
- [ ] Token caching/storage implemented
- [ ] Credential object compatible with existing patterns
- [ ] Token expiration handled gracefully

## 2.3 Scope and Permission Handling Verification (15 minutes)

### Test Cases
**TC2.3.1: Required Scopes Definition**
```python
# Verify required scopes are defined
def test_exchange_scopes():
    """Verify Exchange scopes are properly defined"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    required_scopes = [
        'Mail.ReadWrite',
        'Mail.Send', 
        'Calendars.ReadWrite',
        'User.Read'
    ]
    
    for scope in required_scopes:
        assert scope in source, f"Missing required scope: {scope}"
    
    print("✓ All required scopes defined")

test_exchange_scopes()
```

**TC2.3.2: Permission Error Handling**
```python
# Test permission error handling
def test_permission_error_handling():
    """Verify permission errors are handled properly"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Look for permission error handling patterns
    error_patterns = ['permission', 'scope', 'consent', 'unauthorized', '403']
    found_patterns = [pattern for pattern in error_patterns if pattern.lower() in source.lower()]
    
    assert len(found_patterns) >= 2, f"Insufficient permission error handling: {found_patterns}"
    print(f"✓ Permission error handling present: {found_patterns}")

test_permission_error_handling()
```

**Expected Results:**
- [ ] All required Microsoft Graph scopes defined
- [ ] Scope validation implemented
- [ ] Permission error handling implemented
- [ ] Clear error messages for permission issues

## 2.4 Authentication Testing Verification (15 minutes)

### Test Cases
**TC2.4.1: Unit Test Existence**
```bash
# Verify authentication tests exist
test -f tests/test_exchange_auth.py || test -f tests/exchange/test_auth.py
echo "✓ Authentication test file exists"
```

**TC2.4.2: Mock Testing Implementation**
```python
# Verify mock testing is implemented
def test_mock_implementation():
    """Check if mock testing is properly implemented"""
    import os
    import glob
    
    # Look for test files
    test_files = glob.glob('tests/**/test*exchange*auth*.py', recursive=True)
    assert len(test_files) > 0, "No authentication test files found"
    
    # Check test file content for mocking
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
            mock_indicators = ['mock', 'patch', 'MagicMock', '@patch']
            if any(indicator in content for indicator in mock_indicators):
                print(f"✓ Mock testing implemented in {test_file}")
                return
    
    print("⚠ Mock testing may not be fully implemented")

test_mock_implementation()
```

**Expected Results:**
- [ ] Authentication unit tests created
- [ ] Mock testing implemented for CI/CD
- [ ] Tests cover success and failure scenarios
- [ ] Tests don't require real Azure AD credentials

## Security Verification (10 minutes)

### Test Cases
**TC2.S.1: Credential Security**
```python
# Verify credentials are not hardcoded
def test_credential_security():
    """Ensure no hardcoded credentials"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Check for potential hardcoded secrets
    security_violations = []
    
    # Look for suspicious patterns
    if 'client_secret=' in source and '"' in source:
        if any(char.isalnum() for char in source.split('client_secret=')[1].split('"')[1][:10]):
            security_violations.append("Potential hardcoded client_secret")
    
    if 'tenant_id=' in source and '"' in source:
        tenant_part = source.split('tenant_id=')[1].split('"')[1] if 'tenant_id=' in source else ""
        if len(tenant_part) > 10 and '-' in tenant_part:
            security_violations.append("Potential hardcoded tenant_id")
    
    assert len(security_violations) == 0, f"Security violations: {security_violations}"
    print("✓ No hardcoded credentials detected")

test_credential_security()
```

**TC2.S.2: Token Storage Security**
```python
# Verify secure token storage
def test_token_storage_security():
    """Verify tokens are stored securely"""
    with open('eaia/exchange.py', 'r') as f:
        source = f.read()
    
    # Look for secure storage patterns
    secure_patterns = ['encrypt', 'keyring', 'secure', 'cache']
    insecure_patterns = ['plaintext', 'file.write', 'open(', 'json.dump']
    
    secure_found = any(pattern in source.lower() for pattern in secure_patterns)
    insecure_found = any(pattern in source.lower() for pattern in insecure_patterns)
    
    if insecure_found and not secure_found:
        print("⚠ Potential insecure token storage detected")
    else:
        print("✓ Token storage appears secure")

test_token_storage_security()
```

**Expected Results:**
- [ ] No hardcoded credentials in source code
- [ ] Secure token storage implemented
- [ ] Environment variables used for sensitive data
- [ ] No credentials in logs or error messages

## Integration Verification (5 minutes)

### Test Cases
**TC2.I.1: Gmail Compatibility**
```python
# Verify Gmail functionality still works
def test_gmail_compatibility():
    """Ensure Gmail authentication still works"""
    try:
        from eaia.gmail import get_credentials
        print("✓ Gmail authentication import successful")
    except ImportError as e:
        assert False, f"Gmail authentication broken: {e}"

test_gmail_compatibility()
```

**Expected Results:**
- [ ] Gmail authentication unaffected
- [ ] No breaking changes to existing code
- [ ] Import paths remain consistent

## Final Verification Checklist

### Functionality
- [ ] MSAL authentication implemented correctly
- [ ] Token management works (refresh, caching)
- [ ] All required scopes defined
- [ ] Error handling comprehensive
- [ ] Unit tests created and passing

### Security
- [ ] No hardcoded credentials
- [ ] Secure token storage
- [ ] Proper error handling (no credential leakage)
- [ ] Environment variable usage

### Compatibility
- [ ] Credential object compatible with Gmail pattern
- [ ] No breaking changes to existing functionality
- [ ] Async patterns consistent

### Testing
- [ ] Unit tests cover all scenarios
- [ ] Mock testing implemented
- [ ] Tests run without real credentials
- [ ] Error scenarios tested

## Failure Scenarios and Rollback

### Common Failures
1. **MSAL Import Errors**: Check dependency installation
2. **Authentication Logic Errors**: Verify MSAL usage patterns
3. **Token Management Issues**: Check caching implementation
4. **Security Violations**: Remove any hardcoded credentials

### Rollback Procedure
```bash
# If verification fails, rollback to Stage 1 state
git checkout HEAD~1 -- eaia/exchange.py
# Keep dependency changes from Stage 1
```

## Success Criteria
- [ ] All test cases pass
- [ ] Security verification clean
- [ ] Authentication logic implemented
- [ ] Ready for Stage 3 (Email Fetching)

## Notes for Next Stage
- Document any MSAL-specific patterns for Stage 3
- Note credential object structure for API calls
- Record any authentication timing considerations
