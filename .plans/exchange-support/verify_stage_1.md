# Verification Plan: Stage 1 - Project Dependencies and Basic Structure

**Stage Reference:** `stage_1.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Static Analysis + Build Verification  

## Pre-Verification Setup
- [ ] Ensure clean git working directory
- [ ] Document current dependency versions for rollback
- [ ] Verify existing Gmail functionality works before changes

## 1.1 Dependencies Verification (15 minutes)

### Test Cases
**TC1.1.1: Dependency Installation**
```bash
# Verify dependencies are added to pyproject.toml
grep -E "msal>=1\.24\.0" pyproject.toml
grep -E "msgraph-core>=0\.2\.2" pyproject.toml
grep -E "requests>=2\.31\.0" pyproject.toml

# Install and verify no conflicts
uv install
uv lock --check
```

**TC1.1.2: Import Verification**
```python
# Test script: test_imports.py
try:
    import msal
    import msgraph.core
    import requests
    print("✓ All Exchange dependencies imported successfully")
    print(f"MSAL version: {msal.__version__}")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    exit(1)
```

**Expected Results:**
- [ ] All dependencies present in pyproject.toml with correct versions
- [ ] `uv install` completes without conflicts
- [ ] All imports succeed without errors
- [ ] Version constraints satisfied

## 1.2 Exchange Module Structure Verification (15 minutes)

### Test Cases
**TC1.2.1: Module File Creation**
```bash
# Verify file exists and has correct structure
test -f eaia/exchange.py
python -c "import eaia.exchange; print('✓ Module imports successfully')"
```

**TC1.2.2: Function Signature Verification**
```python
# Test script: verify_signatures.py
import inspect
from eaia.exchange import (
    get_exchange_credentials,
    fetch_exchange_emails,
    send_exchange_email,
    mark_exchange_as_read,
    get_exchange_events_for_days,
    send_exchange_calendar_invite
)

# Verify async functions
assert inspect.iscoroutinefunction(get_exchange_credentials)
assert inspect.iscoroutinefunction(fetch_exchange_emails)

# Verify function signatures match specification
sig = inspect.signature(get_exchange_credentials)
expected_params = ['user_email', 'tenant_id', 'client_id', 'client_secret']
actual_params = list(sig.parameters.keys())
assert all(param in actual_params for param in expected_params)

print("✓ All function signatures verified")
```

**Expected Results:**
- [ ] `eaia/exchange.py` file exists
- [ ] All required functions defined with correct signatures
- [ ] Async functions properly marked as async
- [ ] Module imports without syntax errors
- [ ] All functions have docstrings

## 1.3 Environment Configuration Verification (10 minutes)

### Test Cases
**TC1.3.1: Environment Variables Documentation**
```bash
# Verify .env.example contains Exchange variables
grep "EXCHANGE_TENANT_ID" .env.example
grep "EXCHANGE_CLIENT_ID" .env.example
grep "EXCHANGE_CLIENT_SECRET" .env.example
grep "EMAIL_PROVIDER" .env.example
```

**TC1.3.2: Default Configuration**
```python
# Verify EMAIL_PROVIDER defaults to gmail for backward compatibility
import os
default_provider = os.getenv('EMAIL_PROVIDER', 'gmail')
assert default_provider == 'gmail'
print("✓ Default provider is gmail")
```

**Expected Results:**
- [ ] All Exchange environment variables documented in `.env.example`
- [ ] Default EMAIL_PROVIDER is 'gmail'
- [ ] Environment variable format is correct
- [ ] Comments explain each variable's purpose

## 1.4 Documentation Verification (15 minutes)

### Test Cases
**TC1.4.1: Setup Documentation Exists**
```bash
# Verify documentation files exist
test -f docs/exchange-setup.md || test -f docs/exchange/azure-ad-setup.md
```

**TC1.4.2: Documentation Content Verification**
- [ ] Azure AD app registration steps documented
- [ ] Required permissions listed (Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, User.Read)
- [ ] Troubleshooting section present
- [ ] Links to Microsoft documentation included

**Expected Results:**
- [ ] Setup documentation file exists
- [ ] All required permissions documented
- [ ] Troubleshooting guide covers common issues
- [ ] Documentation is clear and actionable

## Regression Testing (10 minutes)

### Test Cases
**TC1.R.1: Gmail Functionality Preserved**
```python
# Verify existing Gmail imports still work
from eaia.gmail import get_credentials, fetch_group_emails, send_email
print("✓ Gmail imports successful")

# Run existing Gmail tests if available
pytest tests/ -k gmail -v
```

**TC1.R.2: No Breaking Changes**
```bash
# Verify existing configuration still works
python -c "from eaia.main.config import get_config; print('✓ Config loading works')"
```

**Expected Results:**
- [ ] All existing Gmail functionality works unchanged
- [ ] No import errors in existing code
- [ ] Existing tests pass
- [ ] Configuration loading works

## Final Verification Checklist

### Code Quality
- [ ] All functions have type hints
- [ ] Docstrings follow project conventions
- [ ] Code passes linting (ruff, flake8)
- [ ] No security issues in dependency versions

### Functionality
- [ ] All stub functions defined and importable
- [ ] Function signatures match specification exactly
- [ ] Async/sync patterns correct
- [ ] Error handling structure in place

### Documentation
- [ ] Setup guide complete and accurate
- [ ] Environment variables documented
- [ ] Troubleshooting section helpful
- [ ] Code examples provided

### Integration
- [ ] No conflicts with existing dependencies
- [ ] Gmail functionality unaffected
- [ ] Module structure follows project conventions
- [ ] Import paths consistent

## Failure Scenarios and Rollback

### Common Failures
1. **Dependency Conflicts**: Check `uv.lock` for version conflicts
2. **Import Errors**: Verify Python path and module structure
3. **Missing Documentation**: Ensure all required files created
4. **Regression Issues**: Rollback changes and investigate

### Rollback Procedure
```bash
# If verification fails, rollback changes
git checkout -- pyproject.toml uv.lock
git clean -fd eaia/exchange.py docs/exchange*
uv install  # Restore original dependencies
```

## Success Criteria
- [ ] All test cases pass
- [ ] No regressions in existing functionality
- [ ] Documentation complete and accurate
- [ ] Ready for Stage 2 implementation

## Notes for Next Stage
- Document any dependency version issues for Stage 2
- Note any deviations from planned structure
- Record any additional setup requirements discovered
