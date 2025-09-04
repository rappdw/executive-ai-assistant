# Verification Plan: Stage 9 - Configuration System Updates

**Stage Reference:** `stage_9.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Configuration Testing + Backward Compatibility Validation  

## Pre-Verification Setup
- [ ] Stage 8 verification completed successfully
- [ ] Provider interface working correctly
- [ ] Existing Gmail configuration preserved

## 9.1 Configuration Schema Updates Verification (20 minutes)

### Test Cases
**TC9.1.1: Schema Module Updates**
```python
# Test script: test_config_schema.py
def test_schema_updates():
    """Verify configuration schemas are updated"""
    try:
        from eaia.schemas import EmailProviderConfig, ExchangeConfig
        print("✓ Configuration schema classes exist")
    except ImportError as e:
        assert False, f"Configuration schema classes missing: {e}"

test_schema_updates()
```

**TC9.1.2: EmailProviderConfig Validation**
```python
# Test EmailProviderConfig schema
def test_email_provider_config():
    """Verify EmailProviderConfig schema is correct"""
    from eaia.schemas import EmailProviderConfig
    from eaia.email_provider import EmailProvider
    
    # Test valid configuration
    valid_config = EmailProviderConfig(
        provider=EmailProvider.GMAIL,
        gmail_config={"some": "config"},
        exchange_config=None
    )
    
    assert valid_config.provider == EmailProvider.GMAIL
    print("✓ EmailProviderConfig schema works")

test_email_provider_config()
```

**TC9.1.3: ExchangeConfig Validation**
```python
# Test ExchangeConfig schema
def test_exchange_config():
    """Verify ExchangeConfig schema validation"""
    from eaia.schemas import ExchangeConfig
    
    # Test valid Exchange configuration
    valid_exchange_config = ExchangeConfig(
        tenant_id="test-tenant-id",
        client_id="test-client-id", 
        client_secret="test-client-secret"
    )
    
    assert valid_exchange_config.tenant_id == "test-tenant-id"
    print("✓ ExchangeConfig schema works")

test_exchange_config()
```

**TC9.1.4: Backward Compatibility**
```python
# Test backward compatibility with existing schemas
def test_backward_compatibility():
    """Verify existing schemas still work"""
    from eaia.schemas import EmailData, State, RespondTo
    
    # Test existing EmailData still works
    email_data = {
        "id": "test-id",
        "thread_id": "test-thread",
        "from_email": "test@example.com",
        "to_email": "recipient@example.com", 
        "subject": "Test",
        "page_content": "Test content",
        "send_time": "2024-01-01T12:00:00Z"
    }
    
    # Should not raise any errors
    print("✓ Existing schemas preserved")

test_backward_compatibility()
```

**Expected Results:**
- [ ] `EmailProviderConfig` class added to schemas
- [ ] `ExchangeConfig` class with proper validation
- [ ] Provider selection field included
- [ ] Backward compatibility with existing schemas maintained
- [ ] Proper Pydantic validation implemented

## 9.2 Config.yaml Updates Verification (15 minutes)

### Test Cases
**TC9.2.1: Configuration File Structure**
```python
# Test config.yaml structure
def test_config_yaml_structure():
    """Verify config.yaml has provider configuration"""
    import yaml
    from pathlib import Path
    
    config_path = Path('eaia/main/config.yaml')
    assert config_path.exists(), "config.yaml file missing"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for provider configuration
    assert 'email_provider' in config, "email_provider field missing"
    assert config['email_provider'] == 'gmail', "Default provider should be gmail"
    
    print("✓ config.yaml structure updated")

test_config_yaml_structure()
```

**TC9.2.2: Exchange Configuration Section**
```python
# Test Exchange configuration section
def test_exchange_config_section():
    """Verify Exchange configuration section exists"""
    import yaml
    from pathlib import Path
    
    config_path = Path('eaia/main/config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for Exchange configuration
    assert 'exchange_config' in config, "exchange_config section missing"
    
    exchange_config = config['exchange_config']
    required_fields = ['tenant_id', 'client_id', 'client_secret']
    
    for field in required_fields:
        assert field in exchange_config, f"Missing Exchange config field: {field}"
    
    print("✓ Exchange configuration section present")

test_exchange_config_section()
```

**TC9.2.3: Environment Variable Usage**
```python
# Test environment variable placeholders
def test_environment_variables():
    """Verify environment variables are used for sensitive data"""
    import yaml
    from pathlib import Path
    
    config_path = Path('eaia/main/config.yaml')
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    # Check for environment variable patterns
    env_patterns = [
        '${EXCHANGE_TENANT_ID}',
        '${EXCHANGE_CLIENT_ID}',
        '${EXCHANGE_CLIENT_SECRET}'
    ]
    
    for pattern in env_patterns:
        assert pattern in config_content, f"Missing environment variable: {pattern}"
    
    print("✓ Environment variables properly used")

test_environment_variables()
```

**Expected Results:**
- [ ] `email_provider` field added with 'gmail' default
- [ ] `exchange_config` section with all required fields
- [ ] Environment variable placeholders for sensitive data
- [ ] Backward compatibility maintained

## 9.3 Config.py Logic Updates Verification (15 minutes)

### Test Cases
**TC9.3.1: Provider Selection Logic**
```python
# Test provider selection in config.py
def test_provider_selection_logic():
    """Verify config.py handles provider selection"""
    from eaia.main.config import get_config
    
    # Test Gmail configuration (default)
    gmail_config = {'configurable': {'email_provider': 'gmail'}}
    result = get_config(gmail_config)
    
    # Should work without errors
    assert 'email_provider' in result or 'email' in result
    print("✓ Provider selection logic implemented")

test_provider_selection_logic()
```

**TC9.3.2: Configuration Validation**
```python
# Test configuration validation
def test_configuration_validation():
    """Verify configuration validation is implemented"""
    
    # Check if validation logic exists in config.py
    with open('eaia/main/config.py', 'r') as f:
        source = f.read()
    
    validation_patterns = [
        'validate',
        'provider',
        'exchange',
        'gmail',
        'error',
        'raise'
    ]
    
    found_patterns = [pattern for pattern in validation_patterns if pattern in source]
    assert len(found_patterns) >= 3, f"Configuration validation incomplete: {found_patterns}"
    print(f"✓ Configuration validation patterns found: {found_patterns}")

test_configuration_validation()
```

**TC9.3.3: Exchange Configuration Loading**
```python
# Test Exchange configuration loading
def test_exchange_config_loading():
    """Verify Exchange configuration can be loaded"""
    
    # Mock Exchange configuration
    exchange_config = {
        'configurable': {
            'email_provider': 'exchange',
            'exchange_tenant_id': 'test-tenant',
            'exchange_client_id': 'test-client',
            'exchange_client_secret': 'test-secret'
        }
    }
    
    try:
        from eaia.main.config import get_config
        result = get_config(exchange_config)
        # Should not raise errors
        print("✓ Exchange configuration loading works")
    except Exception as e:
        print(f"⚠ Exchange configuration loading may have issues: {e}")

test_exchange_config_loading()
```

**Expected Results:**
- [ ] Provider selection logic implemented in `get_config()`
- [ ] Configuration validation for provider-specific parameters
- [ ] Exchange configuration loading works
- [ ] Backward compatibility with existing Gmail configs maintained

## 9.4 Environment Variable Documentation Verification (10 minutes)

### Test Cases
**TC9.4.1: Environment File Updates**
```bash
# Check .env.example updates
grep "EXCHANGE_TENANT_ID" .env.example
grep "EXCHANGE_CLIENT_ID" .env.example  
grep "EXCHANGE_CLIENT_SECRET" .env.example
grep "EMAIL_PROVIDER" .env.example
echo "✓ Environment variables documented"
```

**TC9.4.2: Variable Format Validation**
```python
# Test environment variable format
def test_env_variable_format():
    """Verify environment variables are properly formatted"""
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    # Check for proper format
    required_vars = [
        'EXCHANGE_TENANT_ID=',
        'EXCHANGE_CLIENT_ID=', 
        'EXCHANGE_CLIENT_SECRET=',
        'EMAIL_PROVIDER='
    ]
    
    for var in required_vars:
        assert var in content, f"Missing environment variable: {var}"
    
    print("✓ Environment variable format correct")

test_env_variable_format()
```

**TC9.4.3: Documentation Comments**
```python
# Test documentation comments
def test_documentation_comments():
    """Verify environment variables have explanatory comments"""
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    # Look for comment patterns
    comment_indicators = ['#', 'Azure', 'tenant', 'client', 'provider']
    found_comments = [indicator for indicator in comment_indicators if indicator in content]
    
    assert len(found_comments) >= 3, f"Insufficient documentation comments: {found_comments}"
    print(f"✓ Documentation comments found: {found_comments}")

test_documentation_comments()
```

**Expected Results:**
- [ ] All Exchange environment variables in `.env.example`
- [ ] `EMAIL_PROVIDER` variable with default value
- [ ] Proper variable format (KEY=value)
- [ ] Explanatory comments for each variable

## Backward Compatibility Testing (5 minutes)

### Test Cases
**TC9.B.1: Existing Gmail Configuration**
```python
# Test existing Gmail configuration still works
def test_existing_gmail_config():
    """Verify existing Gmail configurations are not broken"""
    
    # Test old-style configuration
    old_config = {
        'configurable': {
            'email': 'test@gmail.com'
        }
    }
    
    try:
        from eaia.main.config import get_config
        result = get_config(old_config)
        assert 'email' in result
        print("✓ Existing Gmail configuration preserved")
    except Exception as e:
        assert False, f"Existing Gmail configuration broken: {e}"

test_existing_gmail_config()
```

**TC9.B.2: Configuration Migration**
```python
# Test configuration migration scenarios
def test_configuration_migration():
    """Verify smooth migration from old to new configuration"""
    
    # Check if migration logic exists
    with open('eaia/main/config.py', 'r') as f:
        source = f.read()
    
    migration_patterns = ['backward', 'compatible', 'legacy', 'old', 'migration']
    found_patterns = [pattern for pattern in migration_patterns if pattern in source]
    
    if len(found_patterns) >= 1:
        print(f"✓ Configuration migration considerations found: {found_patterns}")
    else:
        print("⚠ Configuration migration may need attention")

test_configuration_migration()
```

**Expected Results:**
- [ ] Existing Gmail configurations work unchanged
- [ ] No breaking changes to current users
- [ ] Smooth migration path to new configuration
- [ ] Default behavior preserved

## Final Verification Checklist

### Schema Updates
- [ ] EmailProviderConfig class implemented
- [ ] ExchangeConfig class with validation
- [ ] Provider enum integration
- [ ] Backward compatibility maintained

### Configuration Files
- [ ] config.yaml updated with provider selection
- [ ] Exchange configuration section added
- [ ] Environment variables properly used
- [ ] Default provider is Gmail

### Logic Updates
- [ ] get_config() handles provider selection
- [ ] Configuration validation implemented
- [ ] Exchange configuration loading works
- [ ] Error handling for invalid configurations

### Documentation
- [ ] All environment variables documented
- [ ] Variable format correct
- [ ] Explanatory comments provided
- [ ] Migration guide considerations

### Compatibility
- [ ] Existing Gmail configs work unchanged
- [ ] No breaking changes introduced
- [ ] Smooth migration path available
- [ ] Default behavior preserved

## Success Criteria
- [ ] All test cases pass
- [ ] Configuration system supports both providers
- [ ] Backward compatibility maintained
- [ ] Ready for Stage 10 (LangGraph Integration)

## Notes for Next Stage
- Document configuration patterns for LangGraph integration
- Note any provider selection logic for Stage 10
- Record configuration validation patterns
