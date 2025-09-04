# Stage 9: Configuration System Updates

**Estimated Time:** 2-3 hours  
**Prerequisites:** Stage 8 completed  
**Dependencies:** Stage 8  

## Objective
Update the configuration system to support email provider selection and Exchange-specific configuration parameters.

## Tasks

### 9.1 Configuration Schema Updates (60 minutes)
- Update `eaia/schemas.py` with provider configuration models
- Add `EmailProviderConfig` class with validation
- Extend existing configuration to include provider selection
- Ensure backward compatibility with existing Gmail configs

**Key schema additions:**
```python
class EmailProviderConfig(BaseModel):
    provider: EmailProvider
    gmail_config: Optional[dict] = None
    exchange_config: Optional[ExchangeConfig] = None

class ExchangeConfig(BaseModel):
    tenant_id: str
    client_id: str
    client_secret: str
```

### 9.2 Config.yaml Updates (45 minutes)
- Update `eaia/main/config.yaml` with provider selection
- Add Exchange configuration section
- Maintain Gmail as default for backward compatibility
- Add configuration validation

**Configuration structure:**
```yaml
email_provider: "gmail"  # Default to gmail
exchange_config:
  tenant_id: "${EXCHANGE_TENANT_ID}"
  client_id: "${EXCHANGE_CLIENT_ID}"
  client_secret: "${EXCHANGE_CLIENT_SECRET}"
```

### 9.3 Config.py Logic Updates (45 minutes)
- Update `eaia/main/config.py` to handle provider selection
- Add validation for provider-specific configuration
- Implement configuration loading with provider support
- Add error handling for missing configuration

### 9.4 Environment Variable Documentation (30 minutes)
- Update `.env.example` with Exchange variables
- Document all required environment variables
- Add configuration examples for both providers
- Create migration guide for existing installations

## Acceptance Criteria
- [ ] Configuration system supports provider selection
- [ ] Exchange configuration parameters properly validated
- [ ] Backward compatibility maintained for existing Gmail configs
- [ ] Environment variables documented
- [ ] Configuration validation works correctly
- [ ] Unit tests for configuration loading

## Verification Steps
1. Test configuration loading with Gmail provider
2. Test configuration loading with Exchange provider
3. Verify validation catches missing Exchange parameters
4. Test backward compatibility with existing configs
5. Run configuration unit tests

## Notes
- Maintain strict backward compatibility
- Add comprehensive validation for Exchange parameters
- Consider configuration migration scenarios
- Ensure secure handling of client secrets

## Next Stage
Stage 10: LangGraph Integration Updates
