"""
Unit tests for Exchange email fetching functionality.
Tests message conversion, body extraction, and API integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
import json

from eaia.exchange import (
    convert_exchange_message_to_email_data,
    extract_exchange_message_body,
    fetch_exchange_emails,
    ExchangeCredentials
)
from eaia.schemas import EmailData


class TestExchangeMessageConversion:
    """Test conversion of Exchange messages to EmailData format."""
    
    def test_convert_basic_message(self):
        """Test conversion of a basic Exchange message."""
        exchange_msg = {
            "id": "test-message-id-123",
            "conversationId": "test-conversation-id-456",
            "subject": "Test Subject",
            "receivedDateTime": "2024-01-15T10:30:00Z",
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
            "body": {
                "contentType": "text",
                "content": "This is a test message body."
            }
        }
        
        result = convert_exchange_message_to_email_data(exchange_msg)
        
        assert result["id"] == "test-message-id-123"
        assert result["thread_id"] == "test-conversation-id-456"
        assert result["subject"] == "Test Subject"
        assert result["from_email"] == "sender@example.com"
        assert result["to_email"] == "recipient@example.com"
        assert result["page_content"] == "This is a test message body."
        assert result["send_time"] == "2024-01-15T10:30:00Z"
    
    def test_convert_message_missing_conversation_id(self):
        """Test conversion when conversationId is missing (fallback to message ID)."""
        exchange_msg = {
            "id": "test-message-id-123",
            "subject": "Test Subject",
            "receivedDateTime": "2024-01-15T10:30:00Z",
            "from": {
                "emailAddress": {
                    "address": "sender@example.com"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "recipient@example.com"
                    }
                }
            ],
            "body": {
                "contentType": "text",
                "content": "Test body"
            }
        }
        
        result = convert_exchange_message_to_email_data(exchange_msg)
        
        assert result["thread_id"] == "test-message-id-123"  # Fallback to message ID
    
    def test_convert_message_missing_required_field(self):
        """Test conversion fails gracefully when required field is missing."""
        exchange_msg = {
            # Missing "id" field
            "subject": "Test Subject"
        }
        
        with pytest.raises(KeyError, match="Invalid Exchange message format"):
            convert_exchange_message_to_email_data(exchange_msg)
    
    def test_convert_message_empty_recipients(self):
        """Test conversion with empty recipient list."""
        exchange_msg = {
            "id": "test-message-id-123",
            "subject": "Test Subject",
            "receivedDateTime": "2024-01-15T10:30:00Z",
            "from": {
                "emailAddress": {
                    "address": "sender@example.com"
                }
            },
            "toRecipients": [],  # Empty recipients
            "body": {
                "contentType": "text",
                "content": "Test body"
            }
        }
        
        result = convert_exchange_message_to_email_data(exchange_msg)
        
        assert result["to_email"] == ""  # Should handle empty recipients gracefully


class TestExchangeBodyExtraction:
    """Test extraction of message body content."""
    
    def test_extract_plain_text_body(self):
        """Test extraction of plain text body."""
        body = {
            "contentType": "text",
            "content": "This is a plain text message."
        }
        
        result = extract_exchange_message_body(body)
        
        assert result == "This is a plain text message."
    
    def test_extract_html_body(self):
        """Test extraction and conversion of HTML body to plain text."""
        body = {
            "contentType": "html",
            "content": "<html><body><p>This is an <strong>HTML</strong> message.</p></body></html>"
        }
        
        result = extract_exchange_message_body(body)
        
        assert result == "This is an HTML message."
    
    def test_extract_html_body_with_entities(self):
        """Test HTML body extraction with HTML entities."""
        body = {
            "contentType": "html",
            "content": "<p>Price: $100 &amp; free shipping &lt;offer&gt;</p>"
        }
        
        result = extract_exchange_message_body(body)
        
        assert result == "Price: $100 & free shipping <offer>"
    
    def test_extract_html_body_with_scripts(self):
        """Test HTML body extraction removes script and style tags."""
        body = {
            "contentType": "html",
            "content": """
            <html>
                <head><style>body { color: red; }</style></head>
                <body>
                    <script>alert('test');</script>
                    <p>Clean content</p>
                </body>
            </html>
            """
        }
        
        result = extract_exchange_message_body(body)
        
        assert "alert" not in result
        assert "color: red" not in result
        assert "Clean content" in result
    
    def test_extract_empty_body(self):
        """Test extraction from empty body."""
        body = {}
        
        result = extract_exchange_message_body(body)
        
        assert result == "No message body available."
    
    def test_extract_body_no_content(self):
        """Test extraction when content field is missing."""
        body = {
            "contentType": "text"
            # Missing "content" field
        }
        
        result = extract_exchange_message_body(body)
        
        assert result == "No message body available."
    
    def test_extract_body_whitespace_cleanup(self):
        """Test whitespace cleanup in body extraction."""
        body = {
            "contentType": "text",
            "content": "  This   has    lots\n\n  of   whitespace  \t\t"
        }
        
        result = extract_exchange_message_body(body)
        
        assert result == "This has lots of whitespace"


class TestExchangeEmailFetching:
    """Test the main email fetching functionality."""
    
    @pytest.mark.asyncio
    @patch('eaia.exchange.get_exchange_auth_from_env')
    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    async def test_fetch_emails_success(self, mock_requests_get, mock_get_creds, mock_get_env):
        """Test successful email fetching."""
        # Mock environment variables
        mock_get_env.return_value = ("tenant-id", "client-id", "client-secret")
        
        # Mock credentials
        mock_credentials = {
            "access_token": "test-token",
            "expires_in": 3600,
            "refresh_token": "refresh-token"
        }
        mock_get_creds.return_value = mock_credentials
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "msg-1",
                    "conversationId": "conv-1",
                    "subject": "Test Email 1",
                    "receivedDateTime": "2024-01-15T10:30:00Z",
                    "from": {"emailAddress": {"address": "sender1@example.com"}},
                    "toRecipients": [{"emailAddress": {"address": "user@example.com"}}],
                    "body": {"contentType": "text", "content": "Test body 1"}
                },
                {
                    "id": "msg-2", 
                    "conversationId": "conv-2",
                    "subject": "Test Email 2",
                    "receivedDateTime": "2024-01-15T11:00:00Z",
                    "from": {"emailAddress": {"address": "sender2@example.com"}},
                    "toRecipients": [{"emailAddress": {"address": "user@example.com"}}],
                    "body": {"contentType": "text", "content": "Test body 2"}
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Test the function
        result = await fetch_exchange_emails("user@example.com", minutes_since=60)
        
        # Verify results
        assert len(result) == 2
        assert result[0]["id"] == "msg-1"
        assert result[0]["subject"] == "Test Email 1"
        assert result[1]["id"] == "msg-2"
        assert result[1]["subject"] == "Test Email 2"
        
        # Verify API was called correctly
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"
    
    @pytest.mark.asyncio
    @patch('eaia.exchange.get_exchange_auth_from_env')
    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    async def test_fetch_emails_with_pagination(self, mock_requests_get, mock_get_creds, mock_get_env):
        """Test email fetching with pagination."""
        # Mock environment and credentials
        mock_get_env.return_value = ("tenant-id", "client-id", "client-secret")
        mock_credentials = {
            "access_token": "test-token",
            "expires_in": 3600,
            "refresh_token": "refresh-token"
        }
        mock_get_creds.return_value = mock_credentials
        
        # Mock paginated responses
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = {
            "value": [
                {
                    "id": "msg-1",
                    "conversationId": "conv-1",
                    "subject": "Page 1 Email",
                    "receivedDateTime": "2024-01-15T10:30:00Z",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "toRecipients": [{"emailAddress": {"address": "user@example.com"}}],
                    "body": {"contentType": "text", "content": "Page 1 body"}
                }
            ],
            "@odata.nextLink": "https://graph.microsoft.com/v1.0/me/messages?$skip=50"
        }
        
        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = {
            "value": [
                {
                    "id": "msg-2",
                    "conversationId": "conv-2", 
                    "subject": "Page 2 Email",
                    "receivedDateTime": "2024-01-15T11:00:00Z",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "toRecipients": [{"emailAddress": {"address": "user@example.com"}}],
                    "body": {"contentType": "text", "content": "Page 2 body"}
                }
            ]
            # No @odata.nextLink - end of pagination
        }
        
        mock_requests_get.side_effect = [page1_response, page2_response]
        
        # Test the function
        result = await fetch_exchange_emails("user@example.com", minutes_since=60)
        
        # Verify results from both pages
        assert len(result) == 2
        assert result[0]["subject"] == "Page 1 Email"
        assert result[1]["subject"] == "Page 2 Email"
        
        # Verify both API calls were made
        assert mock_requests_get.call_count == 2
    
    @pytest.mark.asyncio
    @patch('eaia.exchange.get_exchange_auth_from_env')
    @patch('eaia.exchange.get_exchange_credentials')
    async def test_fetch_emails_auth_failure(self, mock_get_creds, mock_get_env):
        """Test handling of authentication failure."""
        mock_get_env.return_value = ("tenant-id", "client-id", "client-secret")
        mock_get_creds.side_effect = Exception("Authentication failed")
        
        with pytest.raises(ValueError, match="Authentication failed"):
            await fetch_exchange_emails("user@example.com")
    
    @pytest.mark.asyncio
    @patch('eaia.exchange.get_exchange_auth_from_env')
    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    async def test_fetch_emails_api_error(self, mock_requests_get, mock_get_creds, mock_get_env):
        """Test handling of API request errors."""
        # Mock successful auth
        mock_get_env.return_value = ("tenant-id", "client-id", "client-secret")
        mock_credentials = {
            "access_token": "test-token",
            "expires_in": 3600,
            "refresh_token": "refresh-token"
        }
        mock_get_creds.return_value = mock_credentials
        
        # Mock API failure
        mock_requests_get.side_effect = Exception("API request failed")
        
        with pytest.raises(Exception, match="API request failed"):
            await fetch_exchange_emails("user@example.com")
    
    @pytest.mark.asyncio
    @patch('eaia.exchange.get_exchange_auth_from_env')
    @patch('eaia.exchange.get_exchange_credentials')
    @patch('requests.get')
    @patch('asyncio.sleep')
    async def test_fetch_emails_rate_limiting(self, mock_sleep, mock_requests_get, mock_get_creds, mock_get_env):
        """Test handling of rate limiting (429 response)."""
        # Mock successful auth
        mock_get_env.return_value = ("tenant-id", "client-id", "client-secret")
        mock_credentials = {
            "access_token": "test-token",
            "expires_in": 3600,
            "refresh_token": "refresh-token"
        }
        mock_get_creds.return_value = mock_credentials
        
        # Mock rate limited response, then success
        rate_limited_response = Mock()
        rate_limited_response.status_code = 429
        rate_limited_response.headers = {"Retry-After": "30"}
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"value": []}
        
        mock_requests_get.side_effect = [rate_limited_response, success_response]
        
        # Test the function
        result = await fetch_exchange_emails("user@example.com")
        
        # Verify sleep was called with retry-after value
        mock_sleep.assert_called_once_with(30)
        
        # Verify both requests were made
        assert mock_requests_get.call_count == 2
        
        # Should return empty list
        assert len(result) == 0
