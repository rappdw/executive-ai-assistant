"""
Unit tests for Exchange calendar invite sending functionality.

This module tests the calendar invite creation and sending capabilities
using Microsoft Graph API with proper mocking and error handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
import requests

from eaia.exchange import (
    send_exchange_calendar_invite,
    _send_exchange_calendar_invite_async,
    _validate_calendar_invite_inputs,
    _build_exchange_event_object,
    _format_datetime_for_exchange
)


class TestExchangeCalendarInvites:
    """Test class for Exchange calendar invite functionality."""

    def test_send_calendar_invite_success(self):
        """Test successful calendar invite sending."""
        with patch('asyncio.run') as mock_run:
            mock_run.return_value = True
            
            result = send_exchange_calendar_invite(
                emails=["test@example.com", "user@company.com"],
                title="Team Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )
            
            assert result is True
            mock_run.assert_called_once()

    def test_send_calendar_invite_error_handling(self):
        """Test error handling in calendar invite sending."""
        with patch('asyncio.run') as mock_run:
            mock_run.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                send_exchange_calendar_invite(
                    emails=["test@example.com"],
                    title="Meeting",
                    start_time="2024-07-01T14:00:00",
                    end_time="2024-07-01T15:00:00",
                    user_email="sender@company.com"
                )

    @pytest.mark.asyncio
    async def test_send_calendar_invite_async_success(self):
        """Test successful async calendar invite sending."""
        mock_credentials = {"access_token": "test_token"}
        
        with patch('eaia.exchange.get_exchange_credentials', new_callable=AsyncMock) as mock_creds, \
             patch('requests.post') as mock_post, \
             patch('eaia.exchange._validate_calendar_invite_inputs') as mock_validate, \
             patch('eaia.exchange._build_exchange_event_object') as mock_build:
            
            mock_creds.return_value = mock_credentials
            mock_validate.return_value = None
            mock_build.return_value = {"subject": "Test Meeting"}
            
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 201
            mock_post.return_value = mock_response
            
            result = await _send_exchange_calendar_invite_async(
                emails=["test@example.com"],
                title="Test Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )
            
            assert result is True
            mock_post.assert_called_once()
            
            # Verify API call parameters
            call_args = mock_post.call_args
            assert call_args[1]['json'] == {"subject": "Test Meeting"}
            assert "Bearer test_token" in call_args[1]['headers']['Authorization']

    @pytest.mark.asyncio
    async def test_send_calendar_invite_async_rate_limiting(self):
        """Test rate limiting handling in async calendar invite sending."""
        mock_credentials = {"access_token": "test_token"}
        
        with patch('eaia.exchange.get_exchange_credentials', new_callable=AsyncMock) as mock_creds, \
             patch('requests.post') as mock_post, \
             patch('eaia.exchange._validate_calendar_invite_inputs') as mock_validate, \
             patch('eaia.exchange._build_exchange_event_object') as mock_build, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            mock_creds.return_value = mock_credentials
            mock_validate.return_value = None
            mock_build.return_value = {"subject": "Test Meeting"}
            
            # Mock rate limiting then success
            mock_response_429 = Mock()
            mock_response_429.status_code = 429
            mock_response_429.headers = {'Retry-After': '30'}
            
            mock_response_201 = Mock()
            mock_response_201.status_code = 201
            
            mock_post.side_effect = [mock_response_429, mock_response_201]
            
            result = await _send_exchange_calendar_invite_async(
                emails=["test@example.com"],
                title="Test Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com"
            )
            
            assert result is True
            assert mock_post.call_count == 2
            mock_sleep.assert_called_once_with(30)

    @pytest.mark.asyncio
    async def test_send_calendar_invite_async_api_error(self):
        """Test API error handling in async calendar invite sending."""
        mock_credentials = {"access_token": "test_token"}
        
        with patch('eaia.exchange.get_exchange_credentials', new_callable=AsyncMock) as mock_creds, \
             patch('requests.post') as mock_post, \
             patch('eaia.exchange._validate_calendar_invite_inputs') as mock_validate, \
             patch('eaia.exchange._build_exchange_event_object') as mock_build:
            
            mock_creds.return_value = mock_credentials
            mock_validate.return_value = None
            mock_build.return_value = {"subject": "Test Meeting"}
            
            # Mock API error
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception, match="Failed to create calendar event"):
                await _send_exchange_calendar_invite_async(
                    emails=["test@example.com"],
                    title="Test Meeting",
                    start_time="2024-07-01T14:00:00",
                    end_time="2024-07-01T15:00:00",
                    user_email="sender@company.com"
                )

    @pytest.mark.asyncio
    async def test_send_calendar_invite_async_request_exception_retry(self):
        """Test request exception retry logic in async calendar invite sending."""
        mock_credentials = {"access_token": "test_token"}
        
        with patch('eaia.exchange.get_exchange_credentials', new_callable=AsyncMock) as mock_creds, \
             patch('requests.post') as mock_post, \
             patch('eaia.exchange._validate_calendar_invite_inputs') as mock_validate, \
             patch('eaia.exchange._build_exchange_event_object') as mock_build, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            mock_creds.return_value = mock_credentials
            mock_validate.return_value = None
            mock_build.return_value = {"subject": "Test Meeting"}
            
            # Mock request exception then success
            mock_post.side_effect = [
                requests.exceptions.RequestException("Network error"),
                Mock(status_code=201)
            ]
            
            result = await _send_exchange_calendar_invite_async(
                emails=["test@example.com"],
                title="Test Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com"
            )
            
            assert result is True
            assert mock_post.call_count == 2
            mock_sleep.assert_called_once_with(1)  # 2^0 = 1

    @pytest.mark.asyncio
    async def test_send_calendar_invite_async_auth_failure(self):
        """Test authentication failure handling."""
        with patch('eaia.exchange.get_exchange_credentials', new_callable=AsyncMock) as mock_creds:
            mock_creds.side_effect = ValueError("Authentication failed")
            
            with pytest.raises(ValueError, match="Authentication failed"):
                await _send_exchange_calendar_invite_async(
                    emails=["test@example.com"],
                    title="Test Meeting",
                    start_time="2024-07-01T14:00:00",
                    end_time="2024-07-01T15:00:00",
                    user_email="sender@company.com"
                )

    def test_validate_calendar_invite_inputs_success(self):
        """Test successful input validation."""
        # Should not raise any exception
        _validate_calendar_invite_inputs(
            emails=["test@example.com", "user@company.com"],
            title="Team Meeting",
            start_time="2024-07-01T14:00:00",
            end_time="2024-07-01T15:00:00",
            user_email="sender@company.com",
            timezone="UTC"
        )

    def test_validate_calendar_invite_inputs_invalid_emails(self):
        """Test validation with invalid email addresses."""
        with pytest.raises(ValueError, match="Invalid email address"):
            _validate_calendar_invite_inputs(
                emails=["invalid-email"],
                title="Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )

    def test_validate_calendar_invite_inputs_empty_emails(self):
        """Test validation with empty emails list."""
        with pytest.raises(ValueError, match="Emails must be a non-empty list"):
            _validate_calendar_invite_inputs(
                emails=[],
                title="Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )

    def test_validate_calendar_invite_inputs_invalid_title(self):
        """Test validation with invalid title."""
        with pytest.raises(ValueError, match="Title must be a non-empty string"):
            _validate_calendar_invite_inputs(
                emails=["test@example.com"],
                title="",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )

    def test_validate_calendar_invite_inputs_invalid_user_email(self):
        """Test validation with invalid user email."""
        with pytest.raises(ValueError, match="Invalid user email address"):
            _validate_calendar_invite_inputs(
                emails=["test@example.com"],
                title="Meeting",
                start_time="2024-07-01T14:00:00",
                end_time="2024-07-01T15:00:00",
                user_email="invalid-email",
                timezone="UTC"
            )

    def test_validate_calendar_invite_inputs_invalid_datetime(self):
        """Test validation with invalid datetime format."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            _validate_calendar_invite_inputs(
                emails=["test@example.com"],
                title="Meeting",
                start_time="invalid-datetime",
                end_time="2024-07-01T15:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )

    def test_validate_calendar_invite_inputs_end_before_start(self):
        """Test validation with end time before start time."""
        with pytest.raises(ValueError, match="End time must be after start time"):
            _validate_calendar_invite_inputs(
                emails=["test@example.com"],
                title="Meeting",
                start_time="2024-07-01T15:00:00",
                end_time="2024-07-01T14:00:00",
                user_email="sender@company.com",
                timezone="UTC"
            )

    def test_build_exchange_event_object_success(self):
        """Test successful Exchange event object construction."""
        event_data = _build_exchange_event_object(
            emails=["test@example.com", "user@company.com"],
            title="Team Meeting",
            start_time="2024-07-01T14:00:00",
            end_time="2024-07-01T15:00:00",
            timezone="UTC"
        )
        
        assert event_data["subject"] == "Team Meeting"
        assert len(event_data["attendees"]) == 2
        assert event_data["attendees"][0]["emailAddress"]["address"] == "test@example.com"
        assert event_data["attendees"][0]["type"] == "required"
        assert event_data["isOnlineMeeting"] is True
        assert event_data["onlineMeetingProvider"] == "teamsForBusiness"
        assert event_data["reminderMinutesBeforeStart"] == 15

    def test_build_exchange_event_object_single_attendee(self):
        """Test Exchange event object construction with single attendee."""
        event_data = _build_exchange_event_object(
            emails=["test@example.com"],
            title="One-on-One",
            start_time="2024-07-01T14:00:00",
            end_time="2024-07-01T15:00:00",
            timezone="PST"
        )
        
        assert len(event_data["attendees"]) == 1
        assert event_data["attendees"][0]["emailAddress"]["name"] == "test"

    def test_format_datetime_for_exchange_utc(self):
        """Test datetime formatting for Exchange with UTC timezone."""
        result = _format_datetime_for_exchange("2024-07-01T14:00:00", "UTC")
        
        assert result["dateTime"] == "2024-07-01T14:00:00.0000000"
        assert result["timeZone"] == "UTC"

    def test_format_datetime_for_exchange_pst(self):
        """Test datetime formatting for Exchange with PST timezone."""
        result = _format_datetime_for_exchange("2024-07-01T14:00:00", "PST")
        
        assert result["dateTime"] == "2024-07-01T14:00:00.0000000"
        assert result["timeZone"] == "Pacific Standard Time"

    def test_format_datetime_for_exchange_est(self):
        """Test datetime formatting for Exchange with EST timezone."""
        result = _format_datetime_for_exchange("2024-07-01T14:00:00", "EST")
        
        assert result["dateTime"] == "2024-07-01T14:00:00.0000000"
        assert result["timeZone"] == "Eastern Standard Time"

    def test_format_datetime_for_exchange_custom_timezone(self):
        """Test datetime formatting for Exchange with custom timezone."""
        result = _format_datetime_for_exchange("2024-07-01T14:00:00", "Europe/London")
        
        assert result["dateTime"] == "2024-07-01T14:00:00.0000000"
        assert result["timeZone"] == "Europe/London"

    def test_format_datetime_for_exchange_iso_with_z(self):
        """Test datetime formatting with ISO string containing Z suffix."""
        result = _format_datetime_for_exchange("2024-07-01T14:00:00Z", "UTC")
        
        assert result["dateTime"] == "2024-07-01T14:00:00.0000000"
        assert result["timeZone"] == "UTC"

    def test_calendar_invite_function_signature_compatibility(self):
        """Test that function signature matches Gmail equivalent for compatibility."""
        import inspect
        
        sig = inspect.signature(send_exchange_calendar_invite)
        params = list(sig.parameters.keys())
        
        # Check core parameters are present
        required_params = ['emails', 'title', 'start_time', 'end_time', 'user_email']
        for param in required_params:
            assert param in params, f"Missing required parameter: {param}"
        
        # Check timezone parameter has default
        assert sig.parameters['timezone'].default == "UTC"

    def test_teams_meeting_integration(self):
        """Test Teams meeting integration in event object."""
        event_data = _build_exchange_event_object(
            emails=["test@example.com"],
            title="Teams Meeting",
            start_time="2024-07-01T14:00:00",
            end_time="2024-07-01T15:00:00",
            timezone="UTC"
        )
        
        # Verify Teams meeting is enabled (equivalent to Google Meet)
        assert event_data["isOnlineMeeting"] is True
        assert event_data["onlineMeetingProvider"] == "teamsForBusiness"

    def test_event_properties_configuration(self):
        """Test proper event properties configuration."""
        event_data = _build_exchange_event_object(
            emails=["test@example.com"],
            title="Meeting",
            start_time="2024-07-01T14:00:00",
            end_time="2024-07-01T15:00:00",
            timezone="UTC"
        )
        
        assert event_data["showAs"] == "busy"
        assert event_data["importance"] == "normal"
        assert event_data["sensitivity"] == "normal"
        assert event_data["allowNewTimeProposals"] is True
        assert event_data["reminderMinutesBeforeStart"] == 15
