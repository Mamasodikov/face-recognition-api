#!/usr/bin/env python3
"""
Test the fixes for command handling with bot username and reply functionality.
"""

import os
import sys
import json
from unittest.mock import Mock, patch

# Set up environment
os.environ['TELEGRAM_BOT_TOKEN'] = '8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84'
os.environ['TELEGRAM_CHAT_ID'] = '-1002063224194'
os.environ['TELEGRAM_TOPIC_ID'] = '918'

sys.path.append('.')

def test_commands_with_bot_username():
    """Test that commands work with @botusername suffix."""
    print("🤖 Testing commands with bot username...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test /start@optimuspremiumbot
            start_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/start@optimuspremiumbot",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(start_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                if "xush kelibsiz" in response.lower() or "welcome" in response.lower():
                    print("✅ /start@optimuspremiumbot working")
                else:
                    print("❌ /start@optimuspremiumbot not working properly")
                    return False
            else:
                print("❌ No response for /start@optimuspremiumbot")
                return False
            
            mock_send.reset_mock()
            
            # Test /help@optimuspremiumbot
            help_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/help@optimuspremiumbot",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(help_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                if "mavjud buyruqlar" in response.lower() or "available commands" in response.lower():
                    print("✅ /help@optimuspremiumbot working")
                else:
                    print("❌ /help@optimuspremiumbot not working properly")
                    return False
            else:
                print("❌ No response for /help@optimuspremiumbot")
                return False
        
        print("✅ Commands with bot username working")
        return True
        
    except Exception as e:
        print(f"❌ Commands with bot username test error: {e}")
        return False

def test_clean_command_text():
    """Test the clean_command_text function."""
    print("\n🧹 Testing command text cleaning...")
    try:
        from api.telegram import clean_command_text
        
        test_cases = [
            ("/start@optimuspremiumbot", "/start"),
            ("/help@optimuspremiumbot", "/help"),
            ("/info@optimuspremiumbot", "/info"),
            ("/start", "/start"),  # Should remain unchanged
            ("hello@optimuspremiumbot", "hello"),
            ("regular message", "regular message")  # Should remain unchanged
        ]
        
        for input_text, expected in test_cases:
            result = clean_command_text(input_text)
            if result == expected:
                print(f"✅ '{input_text}' → '{result}'")
            else:
                print(f"❌ '{input_text}' → '{result}', expected '{expected}'")
                return False
        
        print("✅ Command text cleaning working")
        return True
        
    except Exception as e:
        print(f"❌ Command text cleaning test error: {e}")
        return False

def test_reply_detection():
    """Test reply to bot detection."""
    print("\n💬 Testing reply detection...")
    try:
        from api.telegram import is_reply_to_bot
        
        # Test message that is a reply to bot
        reply_message = {
            "reply_to_message": {
                "from": {
                    "is_bot": True,
                    "username": "optimuspremiumbot"
                }
            }
        }
        
        if is_reply_to_bot(reply_message):
            print("✅ Reply to bot detected correctly")
        else:
            print("❌ Reply to bot not detected")
            return False
        
        # Test message that is not a reply
        non_reply_message = {}
        
        if not is_reply_to_bot(non_reply_message):
            print("✅ Non-reply message handled correctly")
        else:
            print("❌ Non-reply message incorrectly detected as reply")
            return False
        
        # Test reply to human
        reply_to_human = {
            "reply_to_message": {
                "from": {
                    "is_bot": False,
                    "username": "human_user"
                }
            }
        }
        
        if not is_reply_to_bot(reply_to_human):
            print("✅ Reply to human correctly ignored")
        else:
            print("❌ Reply to human incorrectly detected as reply to bot")
            return False
        
        print("✅ Reply detection working")
        return True
        
    except Exception as e:
        print(f"❌ Reply detection test error: {e}")
        return False

def test_group_behavior_with_replies():
    """Test that bot responds to replies in groups."""
    print("\n👥 Testing group behavior with replies...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test reply to bot in group (should respond)
            reply_in_group = {
                "chat": {"id": 12345, "type": "group"},
                "text": "Tell me about your services",
                "from": {"first_name": "TestUser", "id": 12345},
                "reply_to_message": {
                    "from": {
                        "is_bot": True,
                        "username": "optimuspremiumbot"
                    }
                }
            }
            
            handle_message(reply_in_group)
            
            if mock_send.called:
                print("✅ Bot responds to replies in groups")
            else:
                print("❌ Bot doesn't respond to replies in groups")
                return False
            
            mock_send.reset_mock()
            
            # Test regular message in group without mention (should not respond)
            regular_group_message = {
                "chat": {"id": 12345, "type": "group"},
                "text": "Hello everyone",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(regular_group_message)
            
            if not mock_send.called:
                print("✅ Bot ignores regular group messages without mention")
            else:
                print("❌ Bot responds to regular group messages")
                return False
        
        print("✅ Group behavior with replies working")
        return True
        
    except Exception as e:
        print(f"❌ Group behavior with replies test error: {e}")
        return False

def test_enhanced_bot_mention_detection():
    """Test enhanced bot mention detection."""
    print("\n🔍 Testing enhanced bot mention detection...")
    try:
        from api.telegram import is_bot_mentioned
        
        test_cases = [
            ("@optimuspremiumbot hello", True),
            ("/start", True),
            ("/start@optimuspremiumbot", True),
            ("/help@optimuspremiumbot", True),
            ("/info@optimuspremiumbot", True),
            ("hello everyone", False),
            ("/unknown@optimuspremiumbot", True),  # Should still be detected as mention
            ("regular message", False)
        ]
        
        for text, expected in test_cases:
            result = is_bot_mentioned(text)
            if result == expected:
                print(f"✅ '{text}' → {result}")
            else:
                print(f"❌ '{text}' → {result}, expected {expected}")
                return False
        
        print("✅ Enhanced bot mention detection working")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced bot mention detection test error: {e}")
        return False

def test_language_detection_with_cleaned_text():
    """Test that language detection works with cleaned command text."""
    print("\n🌐 Testing language detection with cleaned text...")
    try:
        from api.telegram import detect_language, clean_command_text
        
        test_cases = [
            ("/start@optimuspremiumbot", "uzbek"),  # Should default to Uzbek
            ("Salom, kompaniya haqida ma'lumot bering@optimuspremiumbot", "uzbek"),
            ("Hello, tell me about the company@optimuspremiumbot", "english")
        ]
        
        for text, expected_lang in test_cases:
            cleaned = clean_command_text(text)
            detected = detect_language(cleaned)
            if detected == expected_lang:
                print(f"✅ '{text}' → cleaned: '{cleaned}' → {detected}")
            else:
                print(f"❌ '{text}' → cleaned: '{cleaned}' → {detected}, expected {expected_lang}")
                return False
        
        print("✅ Language detection with cleaned text working")
        return True
        
    except Exception as e:
        print(f"❌ Language detection with cleaned text test error: {e}")
        return False

def main():
    """Run all command fix tests."""
    print("🔧 Testing Command Fixes for PremiumSoft Bot")
    print("=" * 60)
    
    tests = [
        test_clean_command_text,
        test_enhanced_bot_mention_detection,
        test_commands_with_bot_username,
        test_reply_detection,
        test_group_behavior_with_replies,
        test_language_detection_with_cleaned_text
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL COMMAND FIX TESTS PASSED!")
        print()
        print("✅ Fixed issues:")
        print("   🤖 Commands with @botusername now work correctly")
        print("   💬 Bot responds to replies even without mentions")
        print("   🧹 Command text cleaning removes bot username")
        print("   🔍 Enhanced mention detection for all commands")
        print("   👥 Proper group behavior with reply support")
        print("   🌐 Language detection works with cleaned text")
        print()
        print("🚀 Your bot now handles all command formats correctly!")
        
        return 0
    else:
        print("❌ SOME COMMAND FIX TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
