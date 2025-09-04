# Verification Plan: Stage 14 - Documentation and Examples

**Stage Reference:** `stage_14.md`  
**Verification Time:** 45-60 minutes  
**Verification Type:** Documentation Quality + Example Validation + User Guide Testing  

## Pre-Verification Setup
- [ ] Stage 13 verification completed successfully
- [ ] Error handling and resilience implemented
- [ ] All core functionality working

## 14.1 Azure AD Setup Documentation Verification (15 minutes)

### Test Cases
**TC14.1.1: Azure AD Setup Guide**
```python
# Test script: verify_documentation.py
def test_azure_ad_setup_guide():
    """Verify Azure AD setup documentation exists and is comprehensive"""
    
    doc_files = [
        Path('docs/azure-ad-setup.md'),
        Path('docs/setup/azure-ad.md'),
        Path('README.md')
    ]
    
    setup_doc = next((f for f in doc_files if f.exists()), None)
    assert setup_doc is not None, f"Azure AD setup documentation missing from: {doc_files}"
    
    with open(setup_doc, 'r') as f:
        content = f.read()
    
    # Check for essential setup steps
    setup_sections = [
        'Azure Portal',
        'App Registration',
        'API Permissions',
        'Client Secret',
        'Tenant ID',
        'Redirect URI'
    ]
    
    found_sections = [section for section in setup_sections if section in content]
    assert len(found_sections) >= 5, f"Missing Azure AD setup sections: {set(setup_sections) - set(found_sections)}"
    print(f"✓ Azure AD setup guide found with sections: {found_sections}")

test_azure_ad_setup_guide()
```

**TC14.1.2: Permission Scopes Documentation**
```python
# Test permission scopes documentation
def test_permission_scopes_documentation():
    """Verify API permission scopes are documented"""
    
    # Check for permission documentation
    doc_files = [
        'docs/azure-ad-setup.md',
        'docs/permissions.md',
        'README.md'
    ]
    
    permissions_documented = False
    for doc_file in doc_files:
        if Path(doc_file).exists():
            with open(doc_file, 'r') as f:
                content = f.read()
            
            # Check for required scopes
            required_scopes = [
                'Mail.ReadWrite',
                'Mail.Send',
                'Calendars.ReadWrite',
                'User.Read'
            ]
            
            found_scopes = [scope for scope in required_scopes if scope in content]
            if len(found_scopes) >= 3:
                permissions_documented = True
                print(f"✓ Permission scopes documented in {doc_file}: {found_scopes}")
                break
    
    assert permissions_documented, "API permission scopes not documented"

test_permission_scopes_documentation()
```

**TC14.1.3: Screenshots and Visual Aids**
```python
# Test for screenshots and visual aids
def test_visual_aids():
    """Verify screenshots and visual aids are included"""
    
    # Check for images directory
    image_dirs = [
        Path('docs/images'),
        Path('docs/screenshots'),
        Path('assets/images')
    ]
    
    image_dir = next((d for d in image_dirs if d.exists()), None)
    
    if image_dir:
        image_files = list(image_dir.glob('*.png')) + list(image_dir.glob('*.jpg'))
        if len(image_files) >= 2:
            print(f"✓ Visual aids found: {len(image_files)} images in {image_dir}")
        else:
            print("⚠ Limited visual aids found")
    else:
        print("⚠ No image directory found - visual aids may be missing")

test_visual_aids()
```

**Expected Results:**
- [ ] Comprehensive Azure AD setup guide with step-by-step instructions
- [ ] API permission scopes clearly documented
- [ ] Screenshots and visual aids for complex setup steps
- [ ] Troubleshooting section for common setup issues

## 14.2 Configuration Documentation Verification (10 minutes)

### Test Cases
**TC14.2.1: Environment Variables Documentation**
```python
# Test environment variables documentation
def test_environment_variables_documentation():
    """Verify environment variables are properly documented"""
    
    # Check .env.example file
    env_example = Path('.env.example')
    assert env_example.exists(), ".env.example file missing"
    
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Check for Exchange environment variables
    exchange_vars = [
        'EXCHANGE_TENANT_ID',
        'EXCHANGE_CLIENT_ID',
        'EXCHANGE_CLIENT_SECRET',
        'EMAIL_PROVIDER'
    ]
    
    found_vars = [var for var in exchange_vars if var in content]
    assert len(found_vars) >= 4, f"Missing environment variables: {set(exchange_vars) - set(found_vars)}"
    
    # Check for comments/descriptions
    comment_count = content.count('#')
    assert comment_count >= 4, "Insufficient documentation comments in .env.example"
    print(f"✓ Environment variables documented with {comment_count} comments")

test_environment_variables_documentation()
```

**TC14.2.2: Configuration Examples**
```python
# Test configuration examples
def test_configuration_examples():
    """Verify configuration examples are provided"""
    
    # Check for configuration examples
    config_docs = [
        Path('docs/configuration.md'),
        Path('docs/config-examples.md'),
        Path('README.md')
    ]
    
    examples_found = False
    for doc_file in config_docs:
        if Path(doc_file).exists():
            with open(doc_file, 'r') as f:
                content = f.read()
            
            # Look for configuration examples
            example_patterns = [
                'email_provider: gmail',
                'email_provider: exchange',
                'exchange_config:',
                'tenant_id:',
                'client_id:'
            ]
            
            found_patterns = [pattern for pattern in example_patterns if pattern in content]
            if len(found_patterns) >= 3:
                examples_found = True
                print(f"✓ Configuration examples found in {doc_file}: {found_patterns}")
                break
    
    assert examples_found, "Configuration examples not found"

test_configuration_examples()
```

**Expected Results:**
- [ ] All environment variables documented in `.env.example`
- [ ] Configuration examples for both Gmail and Exchange
- [ ] Provider switching documentation
- [ ] Configuration validation guidance

## 14.3 API Usage Examples Verification (15 minutes)

### Test Cases
**TC14.3.1: Code Examples Directory**
```python
# Test code examples directory
def test_code_examples_directory():
    """Verify code examples directory exists with relevant examples"""
    
    examples_dirs = [
        Path('examples'),
        Path('docs/examples'),
        Path('samples')
    ]
    
    examples_dir = next((d for d in examples_dirs if d.exists()), None)
    assert examples_dir is not None, f"Examples directory missing from: {examples_dirs}"
    
    # Check for example files
    example_files = list(examples_dir.glob('*.py'))
    assert len(example_files) >= 3, f"Insufficient example files: {len(example_files)}"
    
    print(f"✓ Examples directory found with {len(example_files)} Python files")

test_code_examples_directory()
```

**TC14.3.2: Email Operation Examples**
```python
# Test email operation examples
def test_email_operation_examples():
    """Verify email operation examples exist"""
    
    examples_dir = next((d for d in [Path('examples'), Path('docs/examples'), Path('samples')] if d.exists()), None)
    
    if examples_dir:
        example_files = list(examples_dir.glob('*email*.py')) + list(examples_dir.glob('*send*.py'))
        
        email_examples_found = False
        for example_file in example_files:
            with open(example_file, 'r') as f:
                content = f.read()
            
            # Check for email operation patterns
            email_patterns = [
                'send_email',
                'fetch_emails',
                'mark_as_read',
                'EmailProviderFactory',
                'provider.send_email'
            ]
            
            found_patterns = [pattern for pattern in email_patterns if pattern in content]
            if len(found_patterns) >= 3:
                email_examples_found = True
                print(f"✓ Email operation examples found in {example_file}: {found_patterns}")
                break
        
        assert email_examples_found, "Email operation examples not found"

test_email_operation_examples()
```

**TC14.3.3: Calendar Operation Examples**
```python
# Test calendar operation examples
def test_calendar_operation_examples():
    """Verify calendar operation examples exist"""
    
    examples_dir = next((d for d in [Path('examples'), Path('docs/examples'), Path('samples')] if d.exists()), None)
    
    if examples_dir:
        example_files = list(examples_dir.glob('*calendar*.py')) + list(examples_dir.glob('*invite*.py'))
        
        calendar_examples_found = False
        for example_file in example_files:
            with open(example_file, 'r') as f:
                content = f.read()
            
            # Check for calendar operation patterns
            calendar_patterns = [
                'get_calendar_events',
                'send_calendar_invite',
                'create_meeting',
                'Teams',
                'calendar'
            ]
            
            found_patterns = [pattern for pattern in calendar_patterns if pattern in content]
            if len(found_patterns) >= 2:
                calendar_examples_found = True
                print(f"✓ Calendar operation examples found in {example_file}: {found_patterns}")
                break
        
        assert calendar_examples_found, "Calendar operation examples not found"

test_calendar_operation_examples()
```

**TC14.3.4: Provider Switching Examples**
```python
# Test provider switching examples
def test_provider_switching_examples():
    """Verify provider switching examples exist"""
    
    examples_dir = next((d for d in [Path('examples'), Path('docs/examples'), Path('samples')] if d.exists()), None)
    
    if examples_dir:
        example_files = list(examples_dir.glob('*provider*.py')) + list(examples_dir.glob('*switch*.py'))
        
        switching_examples_found = False
        for example_file in example_files:
            with open(example_file, 'r') as f:
                content = f.read()
            
            # Check for provider switching patterns
            switching_patterns = [
                'EmailProviderFactory',
                'create_provider',
                'gmail',
                'exchange',
                'provider_type'
            ]
            
            found_patterns = [pattern for pattern in switching_patterns if pattern in content]
            if len(found_patterns) >= 3:
                switching_examples_found = True
                print(f"✓ Provider switching examples found in {example_file}: {found_patterns}")
                break
        
        if not switching_examples_found:
            print("⚠ Provider switching examples may be missing")

test_provider_switching_examples()
```

**Expected Results:**
- [ ] Code examples directory with multiple Python files
- [ ] Email operation examples (send, fetch, mark as read)
- [ ] Calendar operation examples (events, invites, Teams meetings)
- [ ] Provider switching examples and patterns

## 14.4 Developer Guide Verification (10 minutes)

### Test Cases
**TC14.4.1: Developer Guide Structure**
```python
# Test developer guide structure
def test_developer_guide_structure():
    """Verify developer guide exists with proper structure"""
    
    guide_files = [
        Path('docs/developer-guide.md'),
        Path('docs/development.md'),
        Path('CONTRIBUTING.md')
    ]
    
    guide_file = next((f for f in guide_files if f.exists()), None)
    assert guide_file is not None, f"Developer guide missing from: {guide_files}"
    
    with open(guide_file, 'r') as f:
        content = f.read()
    
    # Check for essential developer sections
    dev_sections = [
        'Getting Started',
        'Development Setup',
        'Testing',
        'Contributing',
        'Architecture',
        'API Reference'
    ]
    
    found_sections = [section for section in dev_sections if section in content]
    assert len(found_sections) >= 4, f"Missing developer guide sections: {set(dev_sections) - set(found_sections)}"
    print(f"✓ Developer guide found with sections: {found_sections}")

test_developer_guide_structure()
```

**TC14.4.2: Architecture Documentation**
```python
# Test architecture documentation
def test_architecture_documentation():
    """Verify architecture is documented"""
    
    arch_files = [
        Path('docs/architecture.md'),
        Path('docs/developer-guide.md'),
        Path('README.md')
    ]
    
    architecture_documented = False
    for arch_file in arch_files:
        if Path(arch_file).exists():
            with open(arch_file, 'r') as f:
                content = f.read()
            
            # Check for architecture patterns
            arch_patterns = [
                'Provider Interface',
                'EmailProviderFactory',
                'LangGraph',
                'Exchange',
                'Gmail',
                'Architecture'
            ]
            
            found_patterns = [pattern for pattern in arch_patterns if pattern in content]
            if len(found_patterns) >= 4:
                architecture_documented = True
                print(f"✓ Architecture documented in {arch_file}: {found_patterns}")
                break
    
    assert architecture_documented, "Architecture documentation not found"

test_architecture_documentation()
```

**TC14.4.3: Testing Documentation**
```python
# Test testing documentation
def test_testing_documentation():
    """Verify testing procedures are documented"""
    
    test_docs = [
        Path('docs/testing.md'),
        Path('docs/developer-guide.md'),
        Path('CONTRIBUTING.md')
    ]
    
    testing_documented = False
    for test_doc in test_docs:
        if Path(test_doc).exists():
            with open(test_doc, 'r') as f:
                content = f.read()
            
            # Check for testing patterns
            test_patterns = [
                'pytest',
                'unit test',
                'integration test',
                'mock',
                'coverage'
            ]
            
            found_patterns = [pattern for pattern in test_patterns if pattern in content]
            if len(found_patterns) >= 3:
                testing_documented = True
                print(f"✓ Testing documented in {test_doc}: {found_patterns}")
                break
    
    assert testing_documented, "Testing documentation not found"

test_testing_documentation()
```

**Expected Results:**
- [ ] Comprehensive developer guide with proper structure
- [ ] Architecture documentation explaining provider pattern
- [ ] Testing procedures and guidelines documented
- [ ] Contributing guidelines for new developers

## 14.5 README and User Documentation Verification (5 minutes)

### Test Cases
**TC14.5.1: README Completeness**
```python
# Test README completeness
def test_readme_completeness():
    """Verify README is comprehensive and up-to-date"""
    
    readme_file = Path('README.md')
    assert readme_file.exists(), "README.md file missing"
    
    with open(readme_file, 'r') as f:
        content = f.read()
    
    # Check for essential README sections
    readme_sections = [
        'Installation',
        'Configuration',
        'Usage',
        'Exchange Support',
        'Gmail Support',
        'Examples',
        'Contributing'
    ]
    
    found_sections = [section for section in readme_sections if section in content]
    assert len(found_sections) >= 5, f"Missing README sections: {set(readme_sections) - set(found_sections)}"
    print(f"✓ README completeness verified with sections: {found_sections}")

test_readme_completeness()
```

**TC14.5.2: Quick Start Guide**
```python
# Test quick start guide
def test_quick_start_guide():
    """Verify quick start guide exists"""
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for quick start patterns
    quickstart_patterns = [
        'Quick Start',
        'Getting Started',
        'pip install',
        'uv add',
        'python -m',
        'example'
    ]
    
    found_patterns = [pattern for pattern in quickstart_patterns if pattern in content]
    assert len(found_patterns) >= 4, f"Quick start guide incomplete: {found_patterns}"
    print(f"✓ Quick start guide found: {found_patterns}")

test_quick_start_guide()
```

**TC14.5.3: Feature Documentation**
```python
# Test feature documentation
def test_feature_documentation():
    """Verify all features are documented"""
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for feature documentation
    features = [
        'Email sending',
        'Email fetching',
        'Calendar events',
        'Calendar invites',
        'Provider switching',
        'Exchange support',
        'Gmail support'
    ]
    
    documented_features = [feature for feature in features if any(keyword in content.lower() for keyword in feature.lower().split())]
    assert len(documented_features) >= 5, f"Missing feature documentation: {set(features) - set(documented_features)}"
    print(f"✓ Features documented: {documented_features}")

test_feature_documentation()
```

**Expected Results:**
- [ ] Comprehensive README with all essential sections
- [ ] Quick start guide for immediate usage
- [ ] All major features documented
- [ ] Clear installation and configuration instructions

## Documentation Quality Testing (5 minutes)

### Test Cases
**TC14.Q.1: Link Validation**
```python
# Test documentation links
def test_documentation_links():
    """Verify documentation links are valid"""
    
    # Check for common documentation files
    doc_files = [
        'README.md',
        'docs/azure-ad-setup.md',
        'docs/developer-guide.md'
    ]
    
    broken_links = []
    for doc_file in doc_files:
        if Path(doc_file).exists():
            with open(doc_file, 'r') as f:
                content = f.read()
            
            # Look for markdown links
            import re
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            # Check for relative file links
            for link_text, link_url in links:
                if link_url.startswith('./') or link_url.startswith('../'):
                    link_path = Path(doc_file).parent / link_url
                    if not link_path.exists():
                        broken_links.append(f"{doc_file}: {link_url}")
    
    if len(broken_links) == 0:
        print("✓ No broken relative links found")
    else:
        print(f"⚠ Potential broken links: {broken_links}")

test_documentation_links()
```

**TC14.Q.2: Code Block Validation**
```python
# Test code blocks in documentation
def test_code_blocks():
    """Verify code blocks in documentation are valid"""
    
    doc_files = [
        'README.md',
        'docs/developer-guide.md'
    ]
    
    code_blocks_found = 0
    for doc_file in doc_files:
        if Path(doc_file).exists():
            with open(doc_file, 'r') as f:
                content = f.read()
            
            # Count code blocks
            code_blocks_found += content.count('```python')
            code_blocks_found += content.count('```bash')
            code_blocks_found += content.count('```yaml')
    
    assert code_blocks_found >= 5, f"Insufficient code examples: {code_blocks_found}"
    print(f"✓ Code blocks found: {code_blocks_found}")

test_code_blocks()
```

**Expected Results:**
- [ ] No broken links in documentation
- [ ] Sufficient code examples and blocks
- [ ] Consistent formatting and style
- [ ] Up-to-date information

## Final Verification Checklist

### Azure AD Setup
- [ ] Comprehensive setup guide with step-by-step instructions
- [ ] API permission scopes documented
- [ ] Visual aids and screenshots included
- [ ] Troubleshooting section available

### Configuration
- [ ] Environment variables documented
- [ ] Configuration examples provided
- [ ] Provider switching guidance
- [ ] Validation procedures documented

### API Usage Examples
- [ ] Code examples directory with multiple files
- [ ] Email operation examples
- [ ] Calendar operation examples
- [ ] Provider switching examples

### Developer Guide
- [ ] Comprehensive developer guide structure
- [ ] Architecture documentation
- [ ] Testing procedures documented
- [ ] Contributing guidelines available

### User Documentation
- [ ] Complete README with essential sections
- [ ] Quick start guide available
- [ ] All features documented
- [ ] Clear installation instructions

### Documentation Quality
- [ ] No broken links
- [ ] Sufficient code examples
- [ ] Consistent formatting
- [ ] Up-to-date information

## Success Criteria
- [ ] All test cases pass
- [ ] Comprehensive documentation suite complete
- [ ] User and developer guides available
- [ ] Ready for Stage 15 (Performance Optimization)

## Notes for Next Stage
- Document performance benchmarks and optimization targets
- Note any performance-related configuration options
- Record baseline metrics for Stage 15 optimization work
