# Stage 3: Email Fetching Implementation

**Estimated Time:** 3-4 hours  
**Prerequisites:** Stage 2 completed  
**Dependencies:** Stage 2  

## Objective
Implement email fetching from Microsoft Graph API, converting Exchange message format to match the existing `EmailData` schema.

## Tasks

### 3.1 Microsoft Graph Email API Integration (90 minutes)
- Implement `fetch_exchange_emails()` function
- Use Microsoft Graph `/me/messages` endpoint
- Handle pagination for large result sets
- Implement time-based filtering (minutes_since parameter)

**Key implementation points:**
```python
async def fetch_exchange_emails(user_email: str, minutes_since: int = 30) -> Iterable[EmailData]:
    # Build Graph API client with credentials
    # Construct query with time filter
    # Handle pagination through all results
    # Convert each message to EmailData format
```

### 3.2 Message Format Conversion (75 minutes)
- Create `convert_exchange_message_to_email_data()` function
- Map Exchange message fields to EmailData schema
- Handle different message body formats (HTML/plain text)
- Extract thread/conversation information

**Conversion mapping:**
```python
def convert_exchange_message_to_email_data(exchange_msg: dict) -> EmailData:
    return {
        "id": exchange_msg["id"],
        "thread_id": exchange_msg["conversationId"], 
        "from_email": exchange_msg["from"]["emailAddress"]["address"],
        "to_email": exchange_msg["toRecipients"][0]["emailAddress"]["address"],
        "subject": exchange_msg["subject"],
        "page_content": extract_body_content(exchange_msg["body"]),
        "send_time": exchange_msg["receivedDateTime"],
    }
```

### 3.3 Body Content Extraction (45 minutes)
- Implement `extract_exchange_message_body()` function
- Handle HTML and plain text body formats
- Mirror Gmail's `extract_message_part()` functionality
- Ensure consistent text output format

### 3.4 Error Handling and Edge Cases (30 minutes)
- Handle missing or malformed message fields
- Add retry logic for API failures
- Handle rate limiting from Microsoft Graph
- Log appropriate error messages

## Acceptance Criteria
- [ ] `fetch_exchange_emails()` retrieves messages from Exchange
- [ ] Messages converted to `EmailData` format correctly
- [ ] Time filtering works (minutes_since parameter)
- [ ] Pagination handles large mailboxes
- [ ] Body content extraction works for HTML and plain text
- [ ] Proper error handling for API failures
- [ ] Unit tests for message conversion

## Verification Steps
1. Test fetching emails from a real Exchange mailbox
2. Verify EmailData objects match expected schema
3. Test time filtering with different minutes_since values
4. Confirm body content extraction preserves formatting
5. Test error handling with invalid credentials
6. Run conversion unit tests

## Notes
- Maintain the same async iterator pattern as Gmail
- Ensure thread_id mapping works correctly for conversation threading
- Consider Exchange-specific features like importance levels
- Add comprehensive logging for debugging message parsing

## Next Stage
Stage 4: Email Sending Implementation
