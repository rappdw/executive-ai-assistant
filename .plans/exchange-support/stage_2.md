# Stage 2: MSAL Authentication Implementation

**Estimated Time:** 3-4 hours  
**Prerequisites:** Stage 1 completed  
**Dependencies:** Stage 1  

## Objective
Implement Microsoft Authentication Library (MSAL) integration for Exchange authentication, mirroring the Gmail authentication pattern.

## Tasks

### 2.1 MSAL Client Setup (90 minutes)
- Implement `get_exchange_credentials()` function using MSAL
- Handle confidential client application setup
- Implement OAuth2 flow with proper error handling
- Add token caching mechanism

**Key implementation points:**
```python
async def get_exchange_credentials(user_email: str, tenant_id: str, client_id: str, client_secret: str):
    # Create MSAL confidential client
    # Handle OAuth2 authorization code flow
    # Return credentials object compatible with existing interface
    # Implement proper error handling for auth failures
```

### 2.2 Token Management (60 minutes)
- Implement token refresh logic
- Add secure token storage/caching
- Handle token expiration gracefully
- Mirror Gmail's credential management pattern

### 2.3 Scope and Permission Handling (45 minutes)
- Define required Microsoft Graph scopes
- Implement scope validation
- Add permission error handling
- Document required Azure AD permissions

**Required scopes:**
```python
_EXCHANGE_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send", 
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/User.Read"
]
```

### 2.4 Authentication Testing (45 minutes)
- Create basic authentication test
- Test token acquisition and refresh
- Verify credential object compatibility
- Add mock testing for CI/CD

## Acceptance Criteria
- [ ] `get_exchange_credentials()` successfully authenticates with Azure AD
- [ ] Token refresh works automatically
- [ ] Proper error handling for authentication failures
- [ ] Credentials object compatible with existing patterns
- [ ] Unit tests for authentication flow
- [ ] Documentation for Azure AD app setup requirements

## Verification Steps
1. Test authentication with valid Azure AD credentials
2. Verify token refresh mechanism works
3. Test error handling with invalid credentials
4. Confirm credential object structure matches Gmail pattern
5. Run authentication unit tests

## Notes
- Follow the same async pattern as Gmail authentication
- Ensure credential objects are interchangeable between providers
- Add comprehensive logging for debugging authentication issues
- Consider multi-tenant scenarios in the design

## Next Stage
Stage 3: Email Fetching Implementation
