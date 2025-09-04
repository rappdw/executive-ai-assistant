# Stage 10: LangGraph Integration Updates

**Estimated Time:** 2-3 hours  
**Prerequisites:** Stage 9 completed  
**Dependencies:** Stage 9  

## Objective
Update LangGraph workflow integration to use the provider-agnostic email interface, enabling seamless operation with both Gmail and Exchange.

## Tasks

### 10.1 Graph Node Updates (90 minutes)
- Update `eaia/main/graph.py` to use `EmailProviderFactory`
- Modify email-related nodes to work with provider interface
- Update `send_email_node()`, `mark_as_read_node()`, `send_cal_invite_node()`
- Ensure provider selection happens at runtime based on configuration

**Key changes:**
```python
def send_email_node(state, config):
    provider = EmailProviderFactory.create_provider(config)
    # Use provider.send_email() instead of direct Gmail calls
```

### 10.2 Calendar Integration Updates (45 minutes)
- Update calendar-related functions to use provider interface
- Modify `get_events_for_days` tool to work with both providers
- Ensure calendar operations maintain existing LangGraph patterns
- Add provider-aware error handling

### 10.3 Workflow State Management (30 minutes)
- Ensure `EmailData` schema works consistently across providers
- Update state transitions to handle provider-specific behaviors
- Maintain existing workflow logic and decision points
- Add logging for provider operations

### 10.4 Backward Compatibility Testing (15 minutes)
- Verify existing Gmail workflows continue to work
- Test provider switching doesn't break existing functionality
- Ensure configuration changes don't affect running workflows
- Validate error handling across providers

## Acceptance Criteria
- [ ] LangGraph nodes use provider interface instead of direct Gmail calls
- [ ] Provider selection works based on configuration
- [ ] Existing Gmail workflows continue to work unchanged
- [ ] Exchange workflows work through same LangGraph nodes
- [ ] Error handling consistent across providers
- [ ] Integration tests pass for both providers

## Verification Steps
1. Run existing Gmail workflows through updated LangGraph
2. Test Exchange workflows through same LangGraph nodes
3. Verify provider switching works at runtime
4. Test error scenarios with both providers
5. Run full integration test suite

## Notes
- Maintain exact same workflow behavior regardless of provider
- Ensure provider selection is transparent to workflow logic
- Add comprehensive logging for debugging provider issues
- Consider provider-specific optimizations in future iterations

## Next Stage
Stage 11: Unit Test Implementation
