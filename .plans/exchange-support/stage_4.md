# Stage 4: Email Sending Implementation

**Estimated Time:** 2-3 hours  
**Prerequisites:** Stage 3 completed  
**Dependencies:** Stage 3  

## Objective
Implement email sending functionality using Microsoft Graph API, maintaining compatibility with the existing Gmail interface.

## Tasks

### 4.1 Send Email Function Implementation (90 minutes)
- Implement `send_exchange_email()` function
- Use Microsoft Graph `/me/sendMail` endpoint
- Handle reply threading and message references
- Support additional recipients parameter

**Key implementation points:**
```python
def send_exchange_email(
    message_id: str, 
    response_text: str, 
    user_email: str,
    addn_recipients=None,
    **kwargs
):
    # Get original message for reply context
    # Build reply message with proper threading
    # Send via Graph API /me/sendMail
    # Handle send confirmation
```

### 4.2 Message Composition (60 minutes)
- Create `create_exchange_message()` function
- Handle reply threading (In-Reply-To, References headers)
- Build proper message structure for Graph API
- Support HTML and plain text content

### 4.3 Recipient Management (30 minutes)
- Implement `get_exchange_recipients()` function
- Extract recipients from original message
- Handle CC, BCC, and additional recipients
- Mirror Gmail recipient logic

### 4.4 Error Handling and Validation (30 minutes)
- Validate message content and recipients
- Handle Graph API send failures
- Add retry logic for transient failures
- Log send success/failure appropriately

## Acceptance Criteria
- [ ] `send_exchange_email()` sends replies successfully
- [ ] Reply threading works correctly
- [ ] Additional recipients handled properly
- [ ] Message format compatible with Exchange
- [ ] Error handling for send failures
- [ ] Unit tests for message composition

## Verification Steps
1. Send a reply to an existing Exchange email
2. Verify reply threading appears correctly
3. Test with additional recipients
4. Confirm message formatting in Exchange client
5. Test error handling with invalid recipients

## Notes
- Maintain same function signature as Gmail version
- Ensure reply threading works with Exchange conversation model
- Consider Exchange-specific features like importance and sensitivity
- Add proper logging for send operations

## Next Stage
Stage 5: Mark as Read Implementation
