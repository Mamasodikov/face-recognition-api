import unittest
import json
import os
import sys
import requests
from unittest.mock import Mock, patch, MagicMock
import time

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from telegram import Handler


class TestTelegramBotIntegration(unittest.TestCase):
    """Integration tests for the Telegram bot."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_bot_token = os.environ.get('TEST_TELEGRAM_BOT_TOKEN', 'test_token')
        self.test_chat_id = os.environ.get('TEST_CHAT_ID', '12345')
        
    def test_bot_token_validation(self):
        """Test that bot token validation works correctly."""
        # Test with invalid token
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'invalid_token'}):
            # Create a mock handler without calling the parent constructor
            handler = object.__new__(Handler)
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = Mock()
            handler.headers = {}
            handler.path = '/test-bot'

            # This should handle the invalid token gracefully
            handler.do_GET()

            # Should still return 200
            handler.send_response.assert_called_with(200)
            
    def test_webhook_url_construction(self):
        """Test webhook URL construction logic."""
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {'Host': 'example.vercel.app'}
        handler.path = '/setup-webhook'
        
        with patch('telegram.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response

            with patch('telegram.BOT_TOKEN', 'test_token'):
                handler.do_GET()

            # Check that the webhook URL was constructed correctly
            call_json = mock_post.call_args[1]['json']
            self.assertEqual(call_json['url'], 'https://example.vercel.app/api/telegram')
            
    def test_custom_webhook_url(self):
        """Test custom webhook URL functionality."""
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {'Host': 'example.vercel.app'}
        handler.path = '/setup-webhook=https://custom.domain.com/webhook'
        
        with patch('telegram.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response

            with patch('telegram.BOT_TOKEN', 'test_token'):
                handler.do_GET()

            # Check that the custom webhook URL was used
            call_json = mock_post.call_args[1]['json']
            self.assertEqual(call_json['url'], 'https://custom.domain.com/webhook')
            
    def test_message_processing_flow(self):
        """Test the complete message processing flow."""
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {}
        
        # Test different message types
        test_messages = [
            {
                "update": {
                    "message": {
                        "chat": {"id": 12345},
                        "text": "/start",
                        "from": {"first_name": "TestUser"}
                    }
                },
                "expected_response_contains": "Hello TestUser"
            },
            {
                "update": {
                    "message": {
                        "chat": {"id": 12345},
                        "text": "/info",
                        "from": {"first_name": "TestUser"}
                    }
                },
                "expected_response_contains": "PremiumSoft.uz"
            },
            {
                "update": {
                    "message": {
                        "chat": {"id": 12345},
                        "text": "/help",
                        "from": {"first_name": "TestUser"}
                    }
                },
                "expected_response_contains": "Available commands"
            }
        ]
        
        with patch('telegram.send_telegram_message') as mock_send:
            mock_send.return_value = True
            
            for test_case in test_messages:
                with self.subTest(message=test_case["update"]["message"]["text"]):
                    update_json = json.dumps(test_case["update"])
                    handler.headers = {'Content-Length': str(len(update_json))}
                    
                    # Create a new BytesIO for each test
                    import io
                    handler.rfile = io.BytesIO(update_json.encode())
                    
                    handler.do_POST()
                    
                    # Check that send_telegram_message was called
                    self.assertTrue(mock_send.called)
                    
                    # Check the message content
                    call_args = mock_send.call_args[0]
                    self.assertIn(test_case["expected_response_contains"], call_args[1])
                    
                    # Reset the mock for next iteration
                    mock_send.reset_mock()
                    
    def test_error_recovery(self):
        """Test that the bot recovers gracefully from errors."""
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {}
        
        # Test with malformed JSON
        malformed_json = '{"message": {"chat": {"id": 12345}, "text": "/start"'  # Missing closing braces
        handler.headers = {'Content-Length': str(len(malformed_json))}
        
        import io
        handler.rfile = io.BytesIO(malformed_json.encode())
        
        # Should not raise exception
        try:
            handler.do_POST()
            # Should still return 200 to prevent Telegram retries
            handler.send_response.assert_called_with(200)
        except Exception as e:
            self.fail(f"Handler should not raise exception for malformed JSON: {e}")
            
    def test_missing_message_fields(self):
        """Test handling of updates with missing message fields."""
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {}
        
        # Test with missing chat ID
        update_missing_chat = {
            "message": {
                "text": "/start",
                "from": {"first_name": "TestUser"}
            }
        }
        
        update_json = json.dumps(update_missing_chat)
        handler.headers = {'Content-Length': str(len(update_json))}
        
        import io
        handler.rfile = io.BytesIO(update_json.encode())
        
        with patch('telegram.send_telegram_message') as mock_send:
            handler.do_POST()
            
            # Should handle gracefully and not crash
            handler.send_response.assert_called_with(200)
            
    def test_non_message_updates(self):
        """Test handling of non-message updates (e.g., callback queries)."""
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {}
        
        # Test with callback query instead of message
        update_callback = {
            "callback_query": {
                "id": "123",
                "from": {"id": 12345, "first_name": "TestUser"},
                "data": "some_data"
            }
        }
        
        update_json = json.dumps(update_callback)
        handler.headers = {'Content-Length': str(len(update_json))}
        
        import io
        handler.rfile = io.BytesIO(update_json.encode())
        
        with patch('telegram.send_telegram_message') as mock_send:
            handler.do_POST()
            
            # Should handle gracefully and not send any message
            mock_send.assert_not_called()
            handler.send_response.assert_called_with(200)


class TestBotConfiguration(unittest.TestCase):
    """Test bot configuration and environment setup."""
    
    def test_environment_variable_handling(self):
        """Test that environment variables are handled correctly."""
        # Test with no token
        with patch.dict(os.environ, {}, clear=True):
            from telegram import BOT_TOKEN
            # Re-import to get the updated value
            import importlib
            import telegram
            importlib.reload(telegram)
            self.assertIsNone(telegram.BOT_TOKEN)
            
    def test_vercel_configuration(self):
        """Test that Vercel configuration is correct."""
        # Check that vercel.json exists and has correct routes
        vercel_path = os.path.join(os.path.dirname(__file__), '..', 'vercel.json')
        self.assertTrue(os.path.exists(vercel_path))
        
        with open(vercel_path, 'r') as f:
            vercel_config = json.load(f)
            
        # Check routes
        routes = vercel_config.get('routes', [])
        route_sources = [route['src'] for route in routes]
        
        self.assertIn('/api/telegram', route_sources)
        self.assertIn('/api/telegram/setup-webhook(.*)', route_sources)
        self.assertIn('/api/telegram/test-bot', route_sources)
        
    def test_requirements_file(self):
        """Test that requirements.txt exists and has necessary dependencies."""
        req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        self.assertTrue(os.path.exists(req_path))
        
        with open(req_path, 'r') as f:
            requirements = f.read()
            
        # Check for essential dependencies
        self.assertIn('requests', requirements)


if __name__ == '__main__':
    unittest.main()
