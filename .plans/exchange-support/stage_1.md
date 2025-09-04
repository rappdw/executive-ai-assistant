# Stage 1: Project Dependencies and Basic Structure

**Estimated Time:** 2-3 hours  
**Prerequisites:** None  
**Dependencies:** None  

## Objective
Set up the foundational dependencies and basic project structure for Exchange support.

## Tasks

### 1.1 Update Dependencies (30 minutes)
- Add Microsoft Graph API dependencies to `pyproject.toml`
- Ensure compatibility with existing dependencies
- Update lock file

**Dependencies to add:**
```toml
"msal>=1.24.0",           # Microsoft Authentication Library
"msgraph-core>=0.2.2",   # Microsoft Graph Core SDK
"requests>=2.31.0",      # HTTP requests (likely already present)
```

### 1.2 Create Exchange Module Skeleton (45 minutes)
- Create `eaia/exchange.py` with basic structure
- Define function signatures matching Gmail interface
- Add proper imports and basic error handling structure
- Include comprehensive docstrings

**Key functions to define:**
```python
async def get_exchange_credentials(user_email: str, tenant_id: str, client_id: str, client_secret: str)
async def fetch_exchange_emails(user_email: str, minutes_since: int = 30)
def send_exchange_email(message_id: str, response_text: str, user_email: str, **kwargs)
def mark_exchange_as_read(message_id: str, user_email: str)
def get_exchange_events_for_days(date_strs: list[str], user_email: str)
def send_exchange_calendar_invite(emails: list, title: str, start_time: str, end_time: str, user_email: str)
```

### 1.3 Environment Configuration (30 minutes)
- Update `.env.example` with Exchange environment variables
- Document required Azure AD app registration parameters

**Environment variables to add:**
```bash
EXCHANGE_TENANT_ID=your-tenant-id
EXCHANGE_CLIENT_ID=your-client-id
EXCHANGE_CLIENT_SECRET=your-client-secret
EMAIL_PROVIDER=gmail  # Default to gmail for backward compatibility
```

### 1.4 Basic Documentation (45 minutes)
- Create `docs/exchange-setup.md` with Azure AD app registration guide
- Document required permissions and scopes
- Add troubleshooting section for common setup issues

## Acceptance Criteria
- [ ] Dependencies added to `pyproject.toml` and installed successfully
- [ ] `eaia/exchange.py` exists with all required function signatures
- [ ] Environment variables documented in `.env.example`
- [ ] Basic setup documentation created
- [ ] All existing tests still pass
- [ ] No breaking changes to existing Gmail functionality

## Verification Steps
1. Run `uv install` to verify dependencies install correctly
2. Import the new exchange module: `from eaia.exchange import get_exchange_credentials`
3. Verify existing Gmail functionality still works
4. Check that all function signatures match the specification

## Notes
- Keep all functions as stubs initially - implementation comes in later stages
- Focus on maintaining interface compatibility with Gmail module
- Ensure proper async/await patterns where needed
- Add comprehensive type hints for all function parameters

## Next Stage
Stage 2: MSAL Authentication Implementation
