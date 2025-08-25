#!/usr/bin/env python3
"""
Test script for the Vercel-compatible Telegram bot.
This simulates how Vercel would call the handler function.
"""

import json
import os
from unittest.mock import Mock

# Set up environment
os.environ['TELEGRAM_BOT_TOKEN'] = '8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84'

# Import the bot module
from api.telegram import handler, send_telegram_message, get_premiumsoft_info

def test_get_request():
    """Test GET request handling."""
    print("Testing GET request...")
    
    # Mock request and response objects
    request = Mock()
    request.method = 'GET'
    request.url = '/api/telegram'
    request.headers = {'host': 'test.vercel.app'}
    
    response = Mock()
    response.status.return_value = response
    
    # Call handler
    handler(request, response)
    
    # Check response
    response.status.assert_called_with(200)
    response.send.assert_called_once()
    
    call_args = response.send.call_args[0][0]
    print(f"GET Response: {call_args}")
    assert "✅ PremiumSoft.uz Info Bot is active on Vercel!" in call_args
    assert "✅ Bot token is configured" in call_args
    print("✅ GET request test passed!")

def test_webhook_setup():
    """Test webhook setup."""
    print("\nTesting webhook setup...")
    
    request = Mock()
    request.method = 'GET'
    request.url = '/api/telegram?setup-webhook'
    request.headers = {'host': 'test.vercel.app'}
    
    response = Mock()
    response.status.return_value = response
    
    handler(request, response)
    
    response.status.assert_called_with(200)
    call_args = response.send.call_args[0][0]
    print(f"Webhook setup response: {call_args}")
    assert "Webhook setup result" in call_args
    print("✅ Webhook setup test passed!")

def test_bot_test():
    """Test bot connectivity test."""
    print("\nTesting bot connectivity...")
    
    request = Mock()
    request.method = 'GET'
    request.url = '/api/telegram?test-bot'
    request.headers = {'host': 'test.vercel.app'}
    
    response = Mock()
    response.status.return_value = response
    
    handler(request, response)
    
    response.status.assert_called_with(200)
    call_args = response.send.call_args[0][0]
    print(f"Bot test response: {call_args}")
    assert "Bot test result" in call_args
    print("✅ Bot test passed!")

def test_post_request():
    """Test POST request (webhook) handling."""
    print("\nTesting POST request (webhook)...")
    
    # Create a mock Telegram update
    telegram_update = {
        "message": {
            "chat": {"id": 12345},
            "text": "/start",
            "from": {"first_name": "TestUser"}
        }
    }
    
    request = Mock()
    request.method = 'POST'
    request.json.return_value = telegram_update
    
    response = Mock()
    response.status.return_value = response
    
    handler(request, response)
    
    response.status.assert_called_with(200)
    response.send.assert_called_with('OK')
    print("✅ POST request test passed!")

def test_info_command():
    """Test /info command."""
    print("\nTesting /info command...")
    
    telegram_update = {
        "message": {
            "chat": {"id": 12345},
            "text": "/info",
            "from": {"first_name": "TestUser"}
        }
    }
    
    request = Mock()
    request.method = 'POST'
    request.json.return_value = telegram_update
    
    response = Mock()
    response.status.return_value = response
    
    handler(request, response)
    
    response.status.assert_called_with(200)
    response.send.assert_called_with('OK')
    print("✅ /info command test passed!")

def test_help_command():
    """Test /help command."""
    print("\nTesting /help command...")
    
    telegram_update = {
        "message": {
            "chat": {"id": 12345},
            "text": "/help",
            "from": {"first_name": "TestUser"}
        }
    }
    
    request = Mock()
    request.method = 'POST'
    request.json.return_value = telegram_update
    
    response = Mock()
    response.status.return_value = response
    
    handler(request, response)
    
    response.status.assert_called_with(200)
    response.send.assert_called_with('OK')
    print("✅ /help command test passed!")

def test_unknown_message():
    """Test unknown message handling."""
    print("\nTesting unknown message...")
    
    telegram_update = {
        "message": {
            "chat": {"id": 12345},
            "text": "Hello bot!",
            "from": {"first_name": "TestUser"}
        }
    }
    
    request = Mock()
    request.method = 'POST'
    request.json.return_value = telegram_update
    
    response = Mock()
    response.status.return_value = response
    
    handler(request, response)
    
    response.status.assert_called_with(200)
    response.send.assert_called_with('OK')
    print("✅ Unknown message test passed!")

def test_premiumsoft_info():
    """Test the info function."""
    print("\nTesting PremiumSoft info function...")
    
    info = get_premiumsoft_info()
    assert "PremiumSoft.uz" in info
    assert "Services" in info
    assert "Technologies" in info
    assert "Contact Information" in info
    print("✅ PremiumSoft info test passed!")

def main():
    """Run all tests."""
    print("🚀 Testing Vercel-compatible Telegram bot...")
    print("=" * 50)
    
    try:
        test_premiumsoft_info()
        test_get_request()
        test_webhook_setup()
        test_bot_test()
        test_post_request()
        test_info_command()
        test_help_command()
        test_unknown_message()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! The bot is ready for Vercel deployment!")
        print("\n📋 Deployment Instructions:")
        print("1. Set environment variable: TELEGRAM_BOT_TOKEN=8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84")
        print("2. Deploy to Vercel")
        print("3. Set webhook: https://your-app.vercel.app/api/telegram?setup-webhook")
        print("4. Test bot: https://your-app.vercel.app/api/telegram?test-bot")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
