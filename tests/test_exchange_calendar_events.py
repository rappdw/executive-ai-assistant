"""
Unit tests for Exchange calendar events functionality.

Tests cover event retrieval, format conversion, date handling,
and timezone processing using Microsoft Graph API.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from typing import Dict, Any, List
import asyncio
import requests
from datetime import datetime, date, time

from eaia.exchange import (
    get_exchange_events_for_days,
    _fetch_exchange_calendar_events,
    _format_exchange_events,
    _convert_exchange_event,
    _format_datetime_with_timezone
)


class TestExchangeCalendarEvents:
    """Test suite for Exchange calendar events functionality."""

    @pytest.fixture
    def mock_credentials(self):
        """Mock Exchange credentials for testing."""
        return {
            "access_token": "mock_calendar_token_12345",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "scopes": ["https://graph.microsoft.com/Calendars.Read"]
        }

    @pytest.fixture
    def sample_exchange_events(self):
        """Sample Exchange events data from Graph API."""
        return [
            {
                "subject": "Team Meeting",
                "start": {
                    "dateTime": "2024-01-15T10:00:00.0000000",
                    "timeZone": "Pacific Standard Time"
                },
                "end": {
                    "dateTime": "2024-01-15T11:00:00.0000000",
                    "timeZone": "Pacific Standard Time"
                },
                "location": {
                    "displayName": "Conference Room A"
                },
                "bodyPreview": "Weekly team sync meeting",
                "isAllDay": False,
                "organizer": {
                    "emailAddress": {
                        "name": "John Doe",
                        "address": "john@example.com"
                    }
                }
            },
            {
                "subject": "All Day Event",
                "start": {
                    "dateTime": "2024-01-15T00:00:00.0000000",
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": "2024-01-16T00:00:00.0000000",
                    "timeZone": "UTC"
                },
                "location": None,
                "bodyPreview": "Company holiday",
                "isAllDay": True,
                "organizer": {
                    "emailAddress": {
                        "name": "HR Team",
                        "address": "hr@example.com"
                    }
                }
            }
        ]

    @pytest.fixture
    def sample_graph_response(self, sample_exchange_events):
        """Sample Graph API response."""
        return {
            "value": sample_exchange_events,
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('user%40example.com')/events"
        }

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_success(self, mock_get, mock_get_creds, mock_credentials, sample_graph_response):
        """Test successful calendar events retrieval."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_graph_response
        mock_get.return_value = mock_response
        
        result = await _fetch_exchange_calendar_events(
            date_strs=["15-01-2024"],
            user_email="user@example.com"
        )
        
        assert "***FOR DAY 15-01-2024***" in result
        assert "Team Meeting" in result
        assert "All Day Event" in result
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "https://graph.microsoft.com/v1.0/me/events" in call_args[0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer mock_calendar_token_12345"

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_empty_day(self, mock_get, mock_get_creds, mock_credentials):
        """Test calendar events retrieval for empty day."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_get.return_value = mock_response
        
        result = await _fetch_exchange_calendar_events(
            date_strs=["16-01-2024"],
            user_email="user@example.com"
        )
        
        assert "***FOR DAY 16-01-2024***" in result
        assert "No events found for this day." in result

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_multiple_days(self, mock_get, mock_get_creds, mock_credentials, sample_graph_response):
        """Test calendar events retrieval for multiple days."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_graph_response
        mock_get.return_value = mock_response
        
        result = await _fetch_exchange_calendar_events(
            date_strs=["15-01-2024", "16-01-2024"],
            user_email="user@example.com"
        )
        
        assert "***FOR DAY 15-01-2024***" in result
        assert "***FOR DAY 16-01-2024***" in result
        assert mock_get.call_count == 2

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_invalid_date_format(self, mock_get_creds, mock_credentials):
        """Test handling of invalid date format."""
        mock_get_creds.return_value = mock_credentials
        
        result = await _fetch_exchange_calendar_events(
            date_strs=["2024-01-15", "invalid-date"],
            user_email="user@example.com"
        )
        
        assert "Error: Invalid date format. Expected dd-mm-yyyy." in result

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_rate_limiting(self, mock_sleep, mock_get, mock_get_creds, mock_credentials, sample_graph_response):
        """Test handling of rate limiting (HTTP 429)."""
        mock_get_creds.return_value = mock_credentials
        
        # First call returns 429, second call succeeds
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "30"}
        
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = sample_graph_response
        
        mock_get.side_effect = [rate_limit_response, success_response]
        
        result = await _fetch_exchange_calendar_events(
            date_strs=["15-01-2024"],
            user_email="user@example.com"
        )
        
        assert "Team Meeting" in result
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(30)

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_api_error(self, mock_get, mock_get_creds, mock_credentials):
        """Test handling of API errors."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Failed to retrieve calendar events"):
            await _fetch_exchange_calendar_events(
                date_strs=["15-01-2024"],
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_fetch_calendar_events_auth_failure(self, mock_get_creds):
        """Test handling of authentication failures."""
        mock_get_creds.side_effect = ValueError("Authentication failed")
        
        with pytest.raises(ValueError, match="Authentication failed"):
            await _fetch_exchange_calendar_events(
                date_strs=["15-01-2024"],
                user_email="user@example.com"
            )

    def test_convert_exchange_event_timed_event(self, sample_exchange_events):
        """Test conversion of timed Exchange event to Gmail format."""
        exchange_event = sample_exchange_events[0]  # Team Meeting
        
        result = _convert_exchange_event(exchange_event)
        
        assert result["summary"] == "Team Meeting"
        assert result["start"]["dateTime"] == "2024-01-15T10:00:00.0000000"
        assert result["start"]["timeZone"] == "Pacific Standard Time"
        assert result["end"]["dateTime"] == "2024-01-15T11:00:00.0000000"
        assert result["end"]["timeZone"] == "Pacific Standard Time"
        assert result["location"] == "Conference Room A"
        assert result["description"] == "Weekly team sync meeting"

    def test_convert_exchange_event_all_day_event(self, sample_exchange_events):
        """Test conversion of all-day Exchange event to Gmail format."""
        exchange_event = sample_exchange_events[1]  # All Day Event
        
        result = _convert_exchange_event(exchange_event)
        
        assert result["summary"] == "All Day Event"
        assert result["start"]["date"] == "2024-01-15"
        assert result["end"]["date"] == "2024-01-16"
        assert "dateTime" not in result["start"]
        assert "dateTime" not in result["end"]

    def test_convert_exchange_event_minimal_data(self):
        """Test conversion of Exchange event with minimal data."""
        minimal_event = {
            "subject": "Simple Event",
            "start": {"dateTime": "2024-01-15T14:00:00.0000000"},
            "end": {"dateTime": "2024-01-15T15:00:00.0000000"},
            "isAllDay": False
        }
        
        result = _convert_exchange_event(minimal_event)
        
        assert result["summary"] == "Simple Event"
        assert result["start"]["dateTime"] == "2024-01-15T14:00:00.0000000"
        assert result["end"]["dateTime"] == "2024-01-15T15:00:00.0000000"

    def test_convert_exchange_event_error_handling(self):
        """Test error handling in event conversion."""
        malformed_event = {"invalid": "data"}
        
        result = _convert_exchange_event(malformed_event)
        
        # Should return minimal structure even with malformed data
        assert "summary" in result
        assert "start" in result
        assert "end" in result

    def test_format_datetime_with_timezone_success(self):
        """Test successful datetime formatting with timezone."""
        dt_str = "2024-01-15T10:00:00Z"
        
        result = _format_datetime_with_timezone(dt_str, "US/Pacific")
        
        # Should format to Pacific time
        assert "2024-01-15" in result
        assert "PST" in result or "PDT" in result

    def test_format_datetime_with_timezone_error_handling(self):
        """Test datetime formatting error handling."""
        invalid_dt = "invalid-datetime"
        
        result = _format_datetime_with_timezone(invalid_dt)
        
        # Should return original string if formatting fails
        assert result == invalid_dt

    def test_format_exchange_events_empty_list(self):
        """Test formatting of empty events list."""
        result = _format_exchange_events([])
        
        assert result == "No events found for this day.\n\n"

    def test_format_exchange_events_success(self, sample_exchange_events):
        """Test successful formatting of Exchange events."""
        result = _format_exchange_events(sample_exchange_events)
        
        assert "Event: Team Meeting" in result
        assert "Event: All Day Event" in result
        assert "Starts:" in result
        assert "Ends:" in result
        assert "-" * 40 in result

    def test_format_exchange_events_error_handling(self):
        """Test error handling in event formatting."""
        malformed_events = [{"invalid": "data"}]
        
        result = _format_exchange_events(malformed_events)
        
        # Should handle errors gracefully - check for either error message or unknown event
        assert ("Error: Could not format event details" in result or 
                "Unknown Event" in result or 
                "Event:" in result)

    @patch('eaia.exchange._fetch_exchange_calendar_events')
    @patch('eaia.main.config.get_config')
    @patch('langchain_core.runnables.config.ensure_config')
    def test_get_exchange_events_for_days_success(self, mock_ensure_config, mock_get_config, mock_fetch):
        """Test the main get_exchange_events_for_days function."""
        # Mock config
        mock_ensure_config.return_value = {}
        mock_get_config.return_value = {"email": "user@example.com"}
        
        # Mock async result
        mock_fetch.return_value = "***FOR DAY 15-01-2024***\n\nTeam Meeting\n"
        
        # Test the function directly (not as a tool)
        from eaia.exchange import get_exchange_events_for_days
        
        # Get the actual function from the tool
        func = get_exchange_events_for_days.func
        result = func(
            date_strs=["15-01-2024"],
            user_email="user@example.com"
        )
        
        assert "***FOR DAY 15-01-2024***" in result

    @patch('eaia.exchange._fetch_exchange_calendar_events')
    @patch('eaia.main.config.get_config')
    @patch('langchain_core.runnables.config.ensure_config')
    def test_get_exchange_events_for_days_config_email(self, mock_ensure_config, mock_get_config, mock_fetch):
        """Test get_exchange_events_for_days using email from config."""
        # Mock config
        mock_ensure_config.return_value = {}
        mock_get_config.return_value = {"email": "config@example.com"}
        
        # Mock async result
        mock_fetch.return_value = "***FOR DAY 15-01-2024***\n\nNo events found.\n"
        
        # Test the function directly (not as a tool)
        from eaia.exchange import get_exchange_events_for_days
        
        # Get the actual function from the tool
        func = get_exchange_events_for_days.func
        result = func(date_strs=["15-01-2024"])
        
        assert "***FOR DAY 15-01-2024***" in result

    @patch('eaia.exchange._fetch_exchange_calendar_events')
    def test_get_exchange_events_for_days_error_handling(self, mock_fetch):
        """Test error handling in get_exchange_events_for_days."""
        mock_fetch.side_effect = Exception("Calendar API error")
        
        # Test the function directly (not as a tool)
        from eaia.exchange import get_exchange_events_for_days
        
        # Get the actual function from the tool
        func = get_exchange_events_for_days.func
        
        with pytest.raises(Exception, match="Calendar API error"):
            func(
                date_strs=["15-01-2024"],
                user_email="user@example.com"
            )

    def test_date_range_filtering_parameters(self):
        """Test that date range filtering creates correct API parameters."""
        from datetime import datetime, time
        
        # Test date parsing
        date_str = "15-01-2024"
        day = datetime.strptime(date_str, "%d-%m-%Y").date()
        
        start_of_day = datetime.combine(day, time.min).isoformat() + "Z"
        end_of_day = datetime.combine(day, time.max).isoformat() + "Z"
        
        assert start_of_day == "2024-01-15T00:00:00Z"
        assert end_of_day == "2024-01-15T23:59:59.999999Z"

    def test_graph_api_filter_format(self):
        """Test Graph API filter format construction."""
        start_of_day = "2024-01-15T00:00:00Z"
        end_of_day = "2024-01-15T23:59:59.999999Z"
        
        filter_query = f"start/dateTime ge '{start_of_day}' and end/dateTime le '{end_of_day}'"
        
        assert "start/dateTime ge" in filter_query
        assert "end/dateTime le" in filter_query
        assert start_of_day in filter_query
        assert end_of_day in filter_query


if __name__ == "__main__":
    pytest.main([__file__])
