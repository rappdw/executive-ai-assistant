"""
Unit tests for Exchange email sending functionality.

Tests cover message composition, recipient management, email sending,
error handling, and reply threading using Microsoft Graph API.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from typing import Dict, Any
import asyncio
import requests

from eaia.exchange import (
    send_exchange_email,
    get_exchange_recipients,
    create_exchange_message,
    _get_original_message
)


class TestExchangeEmailSending:
    """Test suite for Exchange email sending functionality."""

    @pytest.fixture
    def mock_credentials(self):
        """Mock Exchange credentials for testing."""
        return {
            "access_token": "mock_access_token_12345",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "scopes": ["https://graph.microsoft.com/Mail.Send"]
        }

    @pytest.fixture
    def mock_original_message(self):
        """Mock original Exchange message for reply testing."""
        return {
            "id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OABGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYbvZDAAA=",
            "conversationId": "AAQkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OAAQAOnRkL7YG0-DgVcSRPqcm2E=",
            "internetMessageId": "<message123@example.com>",
            "subject": "Test Email Subject",
            "from": {
                "emailAddress": {
                    "address": "sender@example.com",
                    "name": "Test Sender"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "recipient@example.com",
                        "name": "Test Recipient"
                    }
                }
            ],
            "ccRecipients": [
                {
                    "emailAddress": {
                        "address": "cc@example.com",
                        "name": "CC Recipient"
                    }
                }
            ],
            "receivedDateTime": "2023-12-01T10:00:00Z",
            "body": {
                "contentType": "text",
                "content": "This is the original message content."
            }
        }

    def test_get_exchange_recipients_basic(self, mock_original_message):
        """Test basic recipient extraction from original message."""
        recipients = get_exchange_recipients(mock_original_message)
        
        # Should have sender as primary recipient
        assert len(recipients["toRecipients"]) == 1
        assert recipients["toRecipients"][0]["emailAddress"]["address"] == "sender@example.com"
        assert recipients["toRecipients"][0]["emailAddress"]["name"] == "Test Sender"
        
        # Should preserve CC recipients
        assert len(recipients["ccRecipients"]) == 1
        assert recipients["ccRecipients"][0]["emailAddress"]["address"] == "cc@example.com"
        
        # Should have empty BCC
        assert len(recipients["bccRecipients"]) == 0

    def test_get_exchange_recipients_with_additional(self, mock_original_message):
        """Test recipient extraction with additional recipients."""
        additional_recipients = ["extra1@example.com", "extra2@example.com"]
        recipients = get_exchange_recipients(mock_original_message, additional_recipients)
        
        # Should have original CC plus additional recipients
        assert len(recipients["ccRecipients"]) == 3
        cc_addresses = [r["emailAddress"]["address"] for r in recipients["ccRecipients"]]
        assert "cc@example.com" in cc_addresses
        assert "extra1@example.com" in cc_addresses
        assert "extra2@example.com" in cc_addresses

    def test_get_exchange_recipients_missing_sender(self):
        """Test recipient extraction when sender is missing."""
        message_without_sender = {
            "id": "test123",
            "ccRecipients": []
        }
        recipients = get_exchange_recipients(message_without_sender)
        
        # Should handle missing sender gracefully
        assert len(recipients["toRecipients"]) == 0
        assert len(recipients["ccRecipients"]) == 0
        assert len(recipients["bccRecipients"]) == 0

    def test_create_exchange_message_basic(self, mock_original_message):
        """Test basic message creation for reply."""
        recipients = {
            "toRecipients": [{"emailAddress": {"address": "sender@example.com", "name": "Test Sender"}}],
            "ccRecipients": [],
            "bccRecipients": []
        }
        
        message = create_exchange_message(
            original_message=mock_original_message,
            response_text="This is my reply.",
            recipients=recipients,
            user_email="user@example.com"
        )
        
        # Check subject has Re: prefix
        assert message["subject"] == "Re: Test Email Subject"
        
        # Check body content
        assert message["body"]["contentType"] == "text"
        assert message["body"]["content"] == "This is my reply."
        
        # Check recipients
        assert message["toRecipients"] == recipients["toRecipients"]
        assert message["ccRecipients"] == recipients["ccRecipients"]
        assert message["bccRecipients"] == recipients["bccRecipients"]

    def test_create_exchange_message_reply_threading(self, mock_original_message):
        """Test that reply threading headers are added correctly."""
        recipients = {"toRecipients": [], "ccRecipients": [], "bccRecipients": []}
        
        message = create_exchange_message(
            original_message=mock_original_message,
            response_text="Reply with threading.",
            recipients=recipients,
            user_email="user@example.com"
        )
        
        # Check threading headers
        assert "internetMessageHeaders" in message
        headers = {h["name"]: h["value"] for h in message["internetMessageHeaders"]}
        assert "In-Reply-To" in headers
        assert "References" in headers
        assert headers["In-Reply-To"] == "<message123@example.com>"
        assert headers["References"] == "<message123@example.com>"

    def test_create_exchange_message_existing_re_subject(self, mock_original_message):
        """Test that Re: is not duplicated in subject."""
        mock_original_message["subject"] = "Re: Original Subject"
        recipients = {"toRecipients": [], "ccRecipients": [], "bccRecipients": []}
        
        message = create_exchange_message(
            original_message=mock_original_message,
            response_text="Reply text.",
            recipients=recipients,
            user_email="user@example.com"
        )
        
        # Should not duplicate Re:
        assert message["subject"] == "Re: Original Subject"

    @patch('requests.get')
    def test_get_original_message_success(self, mock_get, mock_credentials, mock_original_message):
        """Test successful retrieval of original message."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_original_message
        mock_get.return_value = mock_response
        
        result = _get_original_message("test_message_id", mock_credentials)
        
        assert result == mock_original_message
        mock_get.assert_called_once()
        
        # Check request parameters
        call_args = mock_get.call_args
        assert "https://graph.microsoft.com/v1.0/me/messages/test_message_id" in call_args[0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer mock_access_token_12345"

    @patch('requests.get')
    def test_get_original_message_not_found(self, mock_get, mock_credentials):
        """Test handling when original message is not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        result = _get_original_message("nonexistent_id", mock_credentials)
        
        assert result is None

    @patch('requests.get')
    def test_get_original_message_request_exception(self, mock_get, mock_credentials):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        result = _get_original_message("test_id", mock_credentials)
        
        assert result is None

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('eaia.exchange._get_original_message')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_send_exchange_email_success(self, mock_post, mock_get_original, mock_get_creds, 
                                       mock_credentials, mock_original_message):
        """Test successful email sending."""
        # Setup mocks
        mock_get_creds.return_value = mock_credentials
        mock_get_original.return_value = mock_original_message
        
        mock_response = MagicMock()
        mock_response.status_code = 202  # Accepted
        mock_post.return_value = mock_response
        
        # Test the function
        result = await send_exchange_email(
            message_id="test_id",
            response_text="Test reply",
            user_email="user@example.com"
        )
        
        assert result is True
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://graph.microsoft.com/v1.0/me/sendMail" in call_args[0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer mock_access_token_12345"
        
        # Check message structure
        sent_data = call_args[1]["json"]
        assert "message" in sent_data
        message = sent_data["message"]
        assert message["subject"] == "Re: Test Email Subject"
        assert message["body"]["content"] == "Test reply"

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('eaia.exchange._get_original_message')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_send_exchange_email_with_additional_recipients(self, mock_post, mock_get_original, 
                                                          mock_get_creds, mock_credentials, mock_original_message):
        """Test email sending with additional recipients."""
        mock_get_creds.return_value = mock_credentials
        mock_get_original.return_value = mock_original_message
        
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_post.return_value = mock_response
        
        result = await send_exchange_email(
            message_id="test_id",
            response_text="Test reply",
            user_email="user@example.com",
            addn_recipients=["extra@example.com"]
        )
        
        assert result is True
        
        # Check that additional recipient was added to CC
        sent_data = mock_post.call_args[1]["json"]
        cc_recipients = sent_data["message"]["ccRecipients"]
        cc_addresses = [r["emailAddress"]["address"] for r in cc_recipients]
        assert "extra@example.com" in cc_addresses

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('eaia.exchange._get_original_message')
    @pytest.mark.asyncio
    async def test_send_exchange_email_original_message_not_found(self, mock_get_original, mock_get_creds, mock_credentials):
        """Test handling when original message cannot be retrieved."""
        mock_get_creds.return_value = mock_credentials
        mock_get_original.return_value = None
        
        with pytest.raises(ValueError, match="Could not retrieve original message"):
            await send_exchange_email(
                message_id="nonexistent_id",
                response_text="Test reply",
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('eaia.exchange._get_original_message')
    @patch('requests.post')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_send_exchange_email_rate_limiting(self, mock_sleep, mock_post, mock_get_original, 
                                             mock_get_creds, mock_credentials, mock_original_message):
        """Test handling of rate limiting (HTTP 429)."""
        mock_get_creds.return_value = mock_credentials
        mock_get_original.return_value = mock_original_message
        
        # First call returns 429, second call succeeds
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "30"}
        
        success_response = MagicMock()
        success_response.status_code = 202
        
        mock_post.side_effect = [rate_limit_response, success_response]
        
        result = await send_exchange_email(
            message_id="test_id",
            response_text="Test reply",
            user_email="user@example.com"
        )
        
        assert result is True
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once_with(30)

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('eaia.exchange._get_original_message')
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_send_exchange_email_api_error(self, mock_post, mock_get_original, mock_get_creds, 
                                         mock_credentials, mock_original_message):
        """Test handling of API errors."""
        mock_get_creds.return_value = mock_credentials
        mock_get_original.return_value = mock_original_message
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception, match="Failed to send email. Status: 400, Response: Bad Request"):
            await send_exchange_email(
                message_id="test_id",
                response_text="Test reply",
                user_email="user@example.com"
            )

    @patch('eaia.exchange.get_exchange_credentials')
    @patch('eaia.exchange._get_original_message')
    @patch('requests.post')
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_send_exchange_email_request_exception_retry(self, mock_sleep, mock_post, mock_get_original, 
                                                       mock_get_creds, mock_credentials, mock_original_message):
        """Test retry logic for request exceptions."""
        mock_get_creds.return_value = mock_credentials
        mock_get_original.return_value = mock_original_message
        
        # First two calls raise exception, third succeeds
        success_response = MagicMock()
        success_response.status_code = 202
        mock_post.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            requests.exceptions.RequestException("Timeout error"),
            success_response
        ]
        
        result = await send_exchange_email(
            message_id="test_id",
            response_text="Test reply",
            user_email="user@example.com"
        )
        
        assert result is True
        assert mock_post.call_count == 3
        # Should have exponential backoff: 2^0=1, 2^1=2
        assert mock_sleep.call_count == 2

    @patch('eaia.exchange.get_exchange_credentials')
    @pytest.mark.asyncio
    async def test_send_exchange_email_auth_failure(self, mock_get_creds):
        """Test handling of authentication failures."""
        mock_get_creds.side_effect = ValueError("Authentication failed")
        
        with pytest.raises(ValueError, match="Authentication failed"):
            await send_exchange_email(
                message_id="test_id",
                response_text="Test reply",
                user_email="user@example.com"
            )


if __name__ == "__main__":
    pytest.main([__file__])
