import unittest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import sys
import io
from http.server import BaseHTTPRequestHandler

# Add the api directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from telegram import Handler, send_telegram_message, get_premiumsoft_info


class TestTelegramBot(unittest.TestCase):
    """Test suite for the Telegram bot functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_bot_token = "test_token_123"
        self.test_chat_id = 12345
        self.test_user_name = "TestUser"
        
    def test_get_premiumsoft_info(self):
        """Test that premiumsoft info is returned correctly."""
        info = get_premiumsoft_info()
        
        # Check that info is not empty
        self.assertIsInstance(info, str)
        self.assertGreater(len(info), 0)
        
        # Check for key content
        self.assertIn("PremiumSoft.uz", info)
        self.assertIn("Services", info)
        self.assertIn("Technologies", info)
        self.assertIn("Contact Information", info)
        
    @patch('telegram.requests.post')
    @patch('telegram.BOT_TOKEN', 'test_token_123')
    def test_send_telegram_message_success(self, mock_post):
        """Test successful message sending."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_post.return_value = mock_response

        result = send_telegram_message(self.test_chat_id, "Test message")

        self.assertTrue(result)
        mock_post.assert_called_once()

        # Check the call arguments
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['chat_id'], self.test_chat_id)
        self.assertEqual(call_args[1]['json']['text'], "Test message")
        
    @patch('telegram.requests.post')
    @patch('telegram.BOT_TOKEN', 'test_token_123')
    def test_send_telegram_message_with_parse_mode(self, mock_post):
        """Test message sending with parse mode."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        result = send_telegram_message(self.test_chat_id, "Test *message*", parse_mode="Markdown")

        self.assertTrue(result)
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['parse_mode'], "Markdown")
        
    @patch('telegram.requests.post')
    @patch('telegram.BOT_TOKEN', 'test_token_123')
    def test_send_telegram_message_api_error(self, mock_post):
        """Test handling of Telegram API errors."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": False, "error_code": 400, "description": "Bad Request"}
        mock_post.return_value = mock_response

        result = send_telegram_message(self.test_chat_id, "Test message")

        self.assertFalse(result)
        
    @patch('telegram.requests.post')
    def test_send_telegram_message_no_token(self, mock_post):
        """Test message sending without bot token."""
        with patch.dict(os.environ, {}, clear=True):
            result = send_telegram_message(self.test_chat_id, "Test message")
            
        self.assertFalse(result)
        mock_post.assert_not_called()
        
    @patch('telegram.requests.post')
    @patch('telegram.BOT_TOKEN', 'test_token_123')
    def test_send_telegram_message_network_error(self, mock_post):
        """Test handling of network errors."""
        mock_post.side_effect = Exception("Network error")

        result = send_telegram_message(self.test_chat_id, "Test message")

        self.assertFalse(result)


class TestTelegramHandler(unittest.TestCase):
    """Test suite for the Telegram webhook handler."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock handler without calling the parent constructor
        self.handler = object.__new__(Handler)
        self.handler.send_response = Mock()
        self.handler.send_header = Mock()
        self.handler.end_headers = Mock()
        self.handler.wfile = Mock()
        self.handler.headers = {}
        self.handler.path = '/'
        
    @patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_123'})
    def test_do_get_basic(self):
        """Test basic GET request handling."""
        self.handler.path = '/'
        
        self.handler.do_GET()
        
        self.handler.send_response.assert_called_with(200)
        self.handler.send_header.assert_called_with('Content-type', 'text/plain')
        self.handler.end_headers.assert_called_once()
        
    @patch.dict(os.environ, {}, clear=True)
    def test_do_get_no_token_warning(self):
        """Test GET request shows warning when no token is configured."""
        self.handler.path = '/'
        
        self.handler.do_GET()
        
        # Check that warning message is written
        write_calls = [call[0][0].decode() for call in self.handler.wfile.write.call_args_list]
        warning_found = any("WARNING: Bot token is not configured!" in call for call in write_calls)
        self.assertTrue(warning_found)
        
    @patch('telegram.requests.post')
    def test_webhook_setup(self, mock_post):
        """Test webhook setup functionality."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_post.return_value = mock_response

        self.handler.path = '/setup-webhook'
        self.handler.headers = {'Host': 'example.com'}

        with patch('telegram.BOT_TOKEN', 'test_token_123'):
            self.handler.do_GET()

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        self.assertIn('setWebhook', call_url)
        # Check that the JSON payload contains the webhook URL
        call_json = mock_post.call_args[1]['json']
        self.assertEqual(call_json['url'], 'https://example.com/api/telegram')
        
    @patch('telegram.send_telegram_message')
    def test_do_post_start_command(self, mock_send):
        """Test handling of /start command."""
        mock_send.return_value = True
        
        # Create test update
        update = {
            "message": {
                "chat": {"id": 12345},
                "text": "/start",
                "from": {"first_name": "TestUser"}
            }
        }
        
        # Mock the request body
        update_json = json.dumps(update)
        self.handler.headers = {'Content-Length': str(len(update_json))}
        self.handler.rfile = io.BytesIO(update_json.encode())
        
        self.handler.do_POST()
        
        # Check that send_telegram_message was called
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        self.assertEqual(call_args[0], 12345)  # chat_id
        self.assertIn("Hello TestUser", call_args[1])  # message text
        
    @patch('telegram.send_telegram_message')
    def test_do_post_info_command(self, mock_send):
        """Test handling of /info command."""
        mock_send.return_value = True
        
        update = {
            "message": {
                "chat": {"id": 12345},
                "text": "/info",
                "from": {"first_name": "TestUser"}
            }
        }
        
        update_json = json.dumps(update)
        self.handler.headers = {'Content-Length': str(len(update_json))}
        self.handler.rfile = io.BytesIO(update_json.encode())
        
        self.handler.do_POST()
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertEqual(call_args[0][0], 12345)  # chat_id
        self.assertIn("PremiumSoft.uz", call_args[0][1])  # message contains company info
        self.assertEqual(call_args[1]['parse_mode'], "Markdown")  # parse_mode is Markdown
        
    @patch('telegram.send_telegram_message')
    def test_do_post_help_command(self, mock_send):
        """Test handling of /help command."""
        mock_send.return_value = True
        
        update = {
            "message": {
                "chat": {"id": 12345},
                "text": "/help",
                "from": {"first_name": "TestUser"}
            }
        }
        
        update_json = json.dumps(update)
        self.handler.headers = {'Content-Length': str(len(update_json))}
        self.handler.rfile = io.BytesIO(update_json.encode())
        
        self.handler.do_POST()
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertEqual(call_args[0][0], 12345)
        self.assertIn("Available commands", call_args[0][1])
        
    @patch('telegram.send_telegram_message')
    def test_do_post_unknown_command(self, mock_send):
        """Test handling of unknown commands."""
        mock_send.return_value = True
        
        update = {
            "message": {
                "chat": {"id": 12345},
                "text": "Hello bot",
                "from": {"first_name": "TestUser"}
            }
        }
        
        update_json = json.dumps(update)
        self.handler.headers = {'Content-Length': str(len(update_json))}
        self.handler.rfile = io.BytesIO(update_json.encode())
        
        self.handler.do_POST()
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertEqual(call_args[0][0], 12345)
        self.assertIn("Hello TestUser", call_args[0][1])
        
    def test_do_post_invalid_json(self):
        """Test handling of invalid JSON in POST request."""
        invalid_json = "invalid json"
        self.handler.headers = {'Content-Length': str(len(invalid_json))}
        self.handler.rfile = io.BytesIO(invalid_json.encode())
        
        # Should not raise exception
        self.handler.do_POST()
        
        # Should still return 200 to Telegram
        self.handler.send_response.assert_called_with(200)


if __name__ == '__main__':
    unittest.main()
