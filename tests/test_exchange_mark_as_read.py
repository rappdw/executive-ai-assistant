"""
Unit tests for Exchange mark as read functionality.

Tests cover single message marking, batch operations, error handling,
and validation using Microsoft Graph API.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from typing import Dict, Any, List
import asyncio
import requests

from eaia.exchange import (
    mark_exchange_as_read,
    mark_exchange_messages_as_read_batch
)


class TestExchangeMarkAsRead:
    """Test suite for Exchange mark as read functionality."""

    @pytest.fixture
    def mock_credentials(self):
        """Mock Exchange credentials for testing."""
        return {
            "access_token": "mock_access_token_12345",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "scopes": ["https://graph.microsoft.com/Mail.ReadWrite"]
        }

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.patch')
    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, mock_patch, mock_get_creds, mock_credentials):
        """Test successful marking of message as read."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = await mark_exchange_as_read(
            message_id="test_message_id",
            user_email="user@example.com"
        )
        
        assert result is True
        
        # Verify API call
        mock_patch.assert_called_once()
        call_args = mock_patch.call_args
        assert "https://graph.microsoft.com/v1.0/me/messages/test_message_id" in call_args[0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer mock_access_token_12345"
        assert call_args[1]["json"] == {"isRead": True}

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.patch')
    @pytest.mark.asyncio
    async def test_mark_as_read_message_not_found(self, mock_patch, mock_get_creds, mock_credentials):
        """Test handling when message is not found."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_patch.return_value = mock_response
        
        with pytest.raises(ValueError, match="Message with ID test_message_id not found"):
            await mark_exchange_as_read(
                message_id="test_message_id",
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_mark_as_read_invalid_message_id(self, mock_get_creds, mock_credentials):
        """Test validation of invalid message ID."""
        mock_get_creds.return_value = mock_credentials
        
        # Test empty message ID
        with pytest.raises(ValueError, match="Invalid message ID provided"):
            await mark_exchange_as_read(
                message_id="",
                user_email="user@example.com"
            )
        
        # Test None message ID
        with pytest.raises(ValueError, match="Invalid message ID provided"):
            await mark_exchange_as_read(
                message_id=None,
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.patch')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_mark_as_read_rate_limiting(self, mock_sleep, mock_patch, mock_get_creds, mock_credentials):
        """Test handling of rate limiting (HTTP 429)."""
        mock_get_creds.return_value = mock_credentials
        
        # First call returns 429, second call succeeds
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "30"}
        
        success_response = MagicMock()
        success_response.status_code = 200
        
        mock_patch.side_effect = [rate_limit_response, success_response]
        
        result = await mark_exchange_as_read(
            message_id="test_message_id",
            user_email="user@example.com"
        )
        
        assert result is True
        assert mock_patch.call_count == 2
        mock_sleep.assert_called_once_with(30)

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.patch')
    @pytest.mark.asyncio
    async def test_mark_as_read_api_error(self, mock_patch, mock_get_creds, mock_credentials):
        """Test handling of API errors."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_patch.return_value = mock_response
        
        with pytest.raises(Exception, match="Failed to mark message as read. Status: 500"):
            await mark_exchange_as_read(
                message_id="test_message_id",
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.patch')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_mark_as_read_request_exception_retry(self, mock_sleep, mock_patch, mock_get_creds, mock_credentials):
        """Test retry logic for request exceptions."""
        mock_get_creds.return_value = mock_credentials
        
        # First two calls raise exception, third succeeds
        success_response = MagicMock()
        success_response.status_code = 200
        mock_patch.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            requests.exceptions.RequestException("Timeout error"),
            success_response
        ]
        
        result = await mark_exchange_as_read(
            message_id="test_message_id",
            user_email="user@example.com"
        )
        
        assert result is True
        assert mock_patch.call_count == 3
        # Should have exponential backoff: 2^0=1, 2^1=2
        assert mock_sleep.call_count == 2

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_mark_as_read_auth_failure(self, mock_get_creds):
        """Test handling of authentication failures."""
        mock_get_creds.side_effect = ValueError("Authentication failed")
        
        with pytest.raises(ValueError, match="Authentication failed"):
            await mark_exchange_as_read(
                message_id="test_message_id",
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_success(self, mock_post, mock_get_creds, mock_credentials):
        """Test successful batch marking of messages as read."""
        mock_get_creds.return_value = mock_credentials
        
        # Mock batch response
        batch_response = {
            "responses": [
                {"id": "0", "status": 200},
                {"id": "1", "status": 200},
                {"id": "2", "status": 404}
            ]
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = batch_response
        mock_post.return_value = mock_response
        
        message_ids = ["msg1", "msg2", "msg3"]
        result = await mark_exchange_messages_as_read_batch(
            message_ids=message_ids,
            user_email="user@example.com"
        )
        
        expected_result = {
            "msg1": True,
            "msg2": True,
            "msg3": False  # 404 status
        }
        assert result == expected_result
        
        # Verify batch API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://graph.microsoft.com/v1.0/$batch" in call_args[0]
        
        # Check batch payload structure
        batch_payload = call_args[1]["json"]
        assert "requests" in batch_payload
        assert len(batch_payload["requests"]) == 3
        
        # Verify individual requests in batch
        for i, request in enumerate(batch_payload["requests"]):
            assert request["method"] == "PATCH"
            assert request["url"] == f"/me/messages/{message_ids[i]}"
            assert request["body"] == {"isRead": True}

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_empty_list(self, mock_get_creds, mock_credentials):
        """Test batch operation with empty message list."""
        mock_get_creds.return_value = mock_credentials
        
        result = await mark_exchange_messages_as_read_batch(
            message_ids=[],
            user_email="user@example.com"
        )
        
        assert result == {}

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_invalid_message_ids(self, mock_post, mock_get_creds, mock_credentials):
        """Test batch operation with invalid message IDs."""
        mock_get_creds.return_value = mock_credentials
        
        # Mock batch response for valid messages only
        batch_response = {
            "responses": [
                {"id": "0", "status": 200}  # Only one valid message
            ]
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = batch_response
        mock_post.return_value = mock_response
        
        # Mix of valid and invalid message IDs
        message_ids = ["valid_msg", "", None, "another_valid_msg"]
        result = await mark_exchange_messages_as_read_batch(
            message_ids=message_ids,
            user_email="user@example.com"
        )
        
        # Should only process valid message IDs
        assert "valid_msg" in result
        assert result["valid_msg"] is True

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.post')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_rate_limiting(self, mock_sleep, mock_post, mock_get_creds, mock_credentials):
        """Test batch operation rate limiting."""
        mock_get_creds.return_value = mock_credentials
        
        # First call returns 429, second call succeeds
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "45"}
        
        batch_response = {"responses": [{"id": "0", "status": 200}]}
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = batch_response
        
        mock_post.side_effect = [rate_limit_response, success_response]
        
        result = await mark_exchange_messages_as_read_batch(
            message_ids=["test_msg"],
            user_email="user@example.com"
        )
        
        assert result == {"test_msg": True}
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once_with(45)

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_api_error(self, mock_post, mock_get_creds, mock_credentials):
        """Test batch operation API errors."""
        mock_get_creds.return_value = mock_credentials
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception, match="Batch operation failed. Status: 500"):
            await mark_exchange_messages_as_read_batch(
                message_ids=["test_msg"],
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.post')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_request_exception_retry(self, mock_sleep, mock_post, mock_get_creds, mock_credentials):
        """Test batch operation retry logic for request exceptions."""
        mock_get_creds.return_value = mock_credentials
        
        # First two calls raise exception, third succeeds
        batch_response = {"responses": [{"id": "0", "status": 200}]}
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = batch_response
        
        mock_post.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            requests.exceptions.RequestException("Timeout error"),
            success_response
        ]
        
        result = await mark_exchange_messages_as_read_batch(
            message_ids=["test_msg"],
            user_email="user@example.com"
        )
        
        assert result == {"test_msg": True}
        assert mock_post.call_count == 3
        # Should have exponential backoff: 2^0=1, 2^1=2
        assert mock_sleep.call_count == 2

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_auth_failure(self, mock_get_creds):
        """Test batch operation authentication failures."""
        mock_get_creds.side_effect = ValueError("Authentication failed")
        
        with pytest.raises(ValueError, match="Authentication failed"):
            await mark_exchange_messages_as_read_batch(
                message_ids=["test_msg"],
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_batch_mark_as_read_partial_success(self, mock_post, mock_get_creds, mock_credentials):
        """Test batch operation with partial success scenarios."""
        mock_get_creds.return_value = mock_credentials
        
        # Mock batch response with mixed results
        batch_response = {
            "responses": [
                {"id": "0", "status": 200},  # Success
                {"id": "1", "status": 404},  # Not found
                {"id": "2", "status": 403},  # Forbidden
                {"id": "3", "status": 200}   # Success
            ]
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = batch_response
        mock_post.return_value = mock_response
        
        message_ids = ["msg1", "msg2", "msg3", "msg4"]
        result = await mark_exchange_messages_as_read_batch(
            message_ids=message_ids,
            user_email="user@example.com"
        )
        
        expected_result = {
            "msg1": True,   # 200 status
            "msg2": False,  # 404 status
            "msg3": False,  # 403 status
            "msg4": True    # 200 status
        }
        assert result == expected_result


if __name__ == "__main__":
    pytest.main([__file__])
