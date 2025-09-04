# Stage 6: Calendar Events Retrieval

**Estimated Time:** 2-3 hours  
**Prerequisites:** Stage 5 completed  
**Dependencies:** Stage 5  

## Objective
Implement calendar event retrieval from Microsoft Graph API, maintaining compatibility with the existing Gmail calendar interface.

## Tasks

### 6.1 Calendar Events Function Implementation (90 minutes)
- Implement `get_exchange_events_for_days()` function
- Use Microsoft Graph `/me/events` endpoint
- Handle date range filtering for specific days
- Convert Exchange event format to match Gmail output

**Key implementation points:**
```python
def get_exchange_events_for_days(date_strs: list[str], user_email: str):
    # Parse date strings to datetime objects
    # Build Graph API queries for each day
    # Retrieve events from Exchange calendar
    # Format output to match Gmail calendar format
```

### 6.2 Event Format Conversion (60 minutes)
- Create `convert_exchange_event()` function
- Map Exchange event fields to Gmail format
- Handle timezone conversions properly
- Format datetime strings consistently

### 6.3 Date Range Handling (30 minutes)
- Implement proper date parsing for dd-mm-yyyy format
- Handle timezone considerations
- Build appropriate Graph API filter queries
- Support multiple date ranges efficiently

### 6.4 Output Formatting (30 minutes)
- Mirror Gmail's `print_events()` output format
- Handle all-day vs timed events
- Format timezone display consistently
- Ensure readable event summaries

## Acceptance Criteria
- [ ] `get_exchange_events_for_days()` retrieves calendar events
- [ ] Output format matches Gmail calendar tool exactly
- [ ] Date filtering works correctly for multiple days
- [ ] Timezone handling works properly
- [ ] Unit tests for event retrieval and formatting

## Verification Steps
1. Retrieve events for specific dates from Exchange calendar
2. Compare output format with Gmail calendar tool
3. Test with different timezones
4. Verify all-day event handling
5. Test with empty calendar days

## Notes
- Maintain exact output format compatibility with Gmail version
- Pay attention to timezone handling differences between providers
- Consider Exchange-specific event properties
- Ensure proper error handling for calendar access issues

## Next Stage
Stage 7: Calendar Invite Sending
