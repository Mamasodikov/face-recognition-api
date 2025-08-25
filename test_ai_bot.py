#!/usr/bin/env python3
"""
Test the AI-enhanced Telegram bot functionality.
"""

import os
import sys
import json
from unittest.mock import Mock

# Set up environment
os.environ['TELEGRAM_BOT_TOKEN'] = '8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84'
# Note: GROQ_API_KEY is not set, so AI will be disabled for this test

sys.path.append('.')

def test_ai_imports():
    """Test that AI imports work correctly."""
    print("🔍 Testing AI imports...")
    try:
        from api.telegram import AI_AVAILABLE, groq_client, get_ai_response
        print(f"AI Available: {AI_AVAILABLE}")
        print(f"Groq Client: {groq_client}")
        print("✅ AI imports successful")
        return True
    except Exception as e:
        print(f"❌ AI import error: {e}")
        return False

def test_enhanced_commands():
    """Test the enhanced bot commands."""
    print("\n🔍 Testing enhanced commands...")
    try:
        from api.telegram import Handler, handle_message
        
        # Test /start command
        message = {
            "chat": {"id": 12345},
            "text": "/start",
            "from": {"first_name": "TestUser"}
        }
        
        print("Testing /start command...")
        handle_message(message)
        
        # Test /ai command
        message["text"] = "/ai"
        print("Testing /ai command...")
        handle_message(message)
        
        # Test /help command
        message["text"] = "/help"
        print("Testing /help command...")
        handle_message(message)
        
        print("✅ Enhanced commands working")
        return True
    except Exception as e:
        print(f"❌ Enhanced commands error: {e}")
        return False

def test_ai_response_without_key():
    """Test AI response when no API key is set."""
    print("\n🔍 Testing AI response without API key...")
    try:
        from api.telegram import get_ai_response
        
        response = get_ai_response("Tell me about your services", "TestUser")
        print(f"AI Response: {response}")
        
        # Should return a fallback message
        if "AI features are currently unavailable" in response:
            print("✅ Correct fallback response when AI unavailable")
            return True
        else:
            print("❌ Unexpected response when AI unavailable")
            return False
            
    except Exception as e:
        print(f"❌ AI response test error: {e}")
        return False

def test_knowledge_base():
    """Test the company knowledge base."""
    print("\n🔍 Testing knowledge base...")
    try:
        from api.telegram import get_company_knowledge_base, get_premiumsoft_info
        
        kb = get_company_knowledge_base()
        info = get_premiumsoft_info()
        
        # Check knowledge base content
        if "Muhammad Aziz Mamasodikov" in kb and "PremiumSoft.uz" in kb:
            print("✅ Knowledge base contains team member info")
        else:
            print("❌ Knowledge base missing team info")
            return False
        
        # Check enhanced info
        if "Muhammad Aziz Mamasodikov" in info:
            print("✅ Enhanced company info includes team members")
        else:
            print("❌ Enhanced company info missing team members")
            return False
        
        print("✅ Knowledge base working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Knowledge base test error: {e}")
        return False

def test_chat_message_handling():
    """Test how chat messages are handled."""
    print("\n🔍 Testing chat message handling...")
    try:
        from api.telegram import handle_message
        
        # Test regular chat message (should trigger AI response)
        message = {
            "chat": {"id": 12345},
            "text": "Tell me about your mobile development services",
            "from": {"first_name": "TestUser"}
        }
        
        print("Testing regular chat message...")
        handle_message(message)
        
        # Test unknown command
        message["text"] = "/unknown"
        print("Testing unknown command...")
        handle_message(message)
        
        print("✅ Chat message handling working")
        return True
        
    except Exception as e:
        print(f"❌ Chat message handling error: {e}")
        return False

def simulate_webhook_request():
    """Simulate a complete webhook request."""
    print("\n🔍 Simulating webhook request...")
    try:
        from api.telegram import Handler
        
        # Create mock handler
        handler = object.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.headers = {'Content-Length': '100'}
        
        # Create test update
        update = {
            "message": {
                "chat": {"id": 12345},
                "text": "What technologies do you use for mobile development?",
                "from": {"first_name": "TestUser"}
            }
        }
        
        # Mock rfile
        import io
        handler.rfile = io.BytesIO(json.dumps(update).encode())
        
        # Call POST handler
        handler.do_POST()
        
        # Check response
        handler.send_response.assert_called_with(200)
        print("✅ Webhook simulation successful")
        return True
        
    except Exception as e:
        print(f"❌ Webhook simulation error: {e}")
        return False

def main():
    """Run all AI bot tests."""
    print("🤖 Testing AI-Enhanced Telegram Bot")
    print("=" * 50)
    
    tests = [
        test_ai_imports,
        test_knowledge_base,
        test_enhanced_commands,
        test_ai_response_without_key,
        test_chat_message_handling,
        simulate_webhook_request
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 ALL AI BOT TESTS PASSED!")
        print()
        print("✅ Your AI-enhanced bot is ready!")
        print()
        print("📋 To enable AI features:")
        print("1. Get a free Groq API key from: https://console.groq.com/")
        print("2. Set environment variable: GROQ_API_KEY=your_key_here")
        print("3. Deploy to Vercel with both tokens:")
        print("   TELEGRAM_BOT_TOKEN=8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84")
        print("   GROQ_API_KEY=your_groq_key")
        print()
        print("🤖 Features:")
        print("   • AI-powered chat responses")
        print("   • Company knowledge base")
        print("   • Team member information")
        print("   • Technical guidance")
        print("   • Fallback to basic info when AI unavailable")
        
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
