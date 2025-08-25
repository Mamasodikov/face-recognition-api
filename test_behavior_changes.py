#!/usr/bin/env python3
"""
Test the behavior changes for topic-aware responses, language matching, and consolidated messages.
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

def test_topic_aware_responses():
    """Test that bot responds to the same topic/thread."""
    print("🧵 Testing topic-aware responses...")
    try:
        from api.telegram import handle_message
        
        # Mock the send_telegram_message function to capture calls
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test message with topic ID
            message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
                "from": {"first_name": "TestUser", "id": 12345},
                "message_thread_id": 918
            }
            
            handle_message(message)
            
            # Check that send_telegram_message was called with the topic ID
            mock_send.assert_called()
            call_kwargs = mock_send.call_args[1]
            
            if 'message_thread_id' in call_kwargs and call_kwargs['message_thread_id'] == 918:
                print("✅ Topic ID correctly passed to response")
            else:
                print("❌ Topic ID not passed to response")
                return False
        
        print("✅ Topic-aware responses working")
        return True
        
    except Exception as e:
        print(f"❌ Topic-aware test error: {e}")
        return False

def test_language_detection():
    """Test language detection functionality."""
    print("\n🌐 Testing language detection...")
    try:
        from api.telegram import detect_language
        
        test_cases = [
            ("Salom, qanday yordam bera olaman?", "uzbek"),
            ("Hello, how can I help you?", "english"),
            ("Men mobil ilova kerak", "uzbek"),
            ("I need a mobile app", "english"),
            ("Rahmat sizga", "uzbek"),
            ("Thank you very much", "english"),
            ("Loyiha haqida", "uzbek"),
            ("About the project", "english"),
            ("/start", "uzbek"),  # Default to Uzbek
            ("", "uzbek")  # Default to Uzbek
        ]
        
        for text, expected_lang in test_cases:
            detected = detect_language(text)
            if detected == expected_lang:
                print(f"✅ '{text}' -> {detected}")
            else:
                print(f"❌ '{text}' -> {detected}, expected {expected_lang}")
                return False
        
        print("✅ Language detection working")
        return True
        
    except Exception as e:
        print(f"❌ Language detection test error: {e}")
        return False

def test_language_matching_responses():
    """Test that bot responds in the same language as user."""
    print("\n🗣️ Testing language matching responses...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test Uzbek message
            uzbek_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Salom, kompaniya haqida ma'lumot bering",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(uzbek_message)
            
            # Check that response contains Uzbek text
            uzbek_call = mock_send.call_args[0][1]  # Get the message text
            if any(uzbek_word in uzbek_call.lower() for uzbek_word in ['salom', 'rahmat', 'kompaniya', 'haqida']):
                print("✅ Uzbek message gets Uzbek response")
            else:
                print("❌ Uzbek message didn't get Uzbek response")
                return False
            
            mock_send.reset_mock()
            
            # Test English message
            english_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Hello, tell me about the company",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(english_message)
            
            # Check that response contains English text
            english_call = mock_send.call_args[0][1]  # Get the message text
            if any(eng_word in english_call.lower() for eng_word in ['hello', 'thank', 'company', 'about']):
                print("✅ English message gets English response")
            else:
                print("❌ English message didn't get English response")
                return False
        
        print("✅ Language matching responses working")
        return True
        
    except Exception as e:
        print(f"❌ Language matching test error: {e}")
        return False

def test_consolidated_follow_up_messages():
    """Test that follow-up messages are consolidated into main response."""
    print("\n📝 Testing consolidated follow-up messages...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test service inquiry that should trigger consolidated response
            service_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Men mobil ilova kerak",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(service_message)
            
            # Should only be called once (consolidated message)
            call_count = mock_send.call_count
            if call_count == 1:
                print("✅ Only one message sent (consolidated)")
                
                # Check that the message contains both AI response and order prompt
                message_text = mock_send.call_args[0][1]
                if "/order" in message_text and ("loyihangiz uchun" in message_text or "detailed proposal" in message_text):
                    print("✅ Message contains consolidated order prompt")
                else:
                    print("❌ Message missing order prompt")
                    return False
            else:
                print(f"❌ Expected 1 message, got {call_count}")
                return False
        
        print("✅ Consolidated follow-up messages working")
        return True
        
    except Exception as e:
        print(f"❌ Consolidated messages test error: {e}")
        return False

def test_order_prompt_language():
    """Test that order prompt appears in correct language."""
    print("\n💼 Testing order prompt language...")
    try:
        from api.telegram import get_order_prompt
        
        uzbek_prompt = get_order_prompt("uzbek")
        english_prompt = get_order_prompt("english")
        
        if "loyihangiz uchun" in uzbek_prompt and "/order" in uzbek_prompt:
            print("✅ Uzbek order prompt correct")
        else:
            print("❌ Uzbek order prompt incorrect")
            return False
        
        if "detailed proposal" in english_prompt and "/order" in english_prompt:
            print("✅ English order prompt correct")
        else:
            print("❌ English order prompt incorrect")
            return False
        
        print("✅ Order prompt language working")
        return True
        
    except Exception as e:
        print(f"❌ Order prompt language test error: {e}")
        return False

def test_lead_collection_language():
    """Test that lead collection works in both languages."""
    print("\n📋 Testing lead collection language support...")
    try:
        from api.telegram import start_lead_collection
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test Uzbek lead collection
            start_lead_collection(12345, None, "uzbek")
            uzbek_message = mock_send.call_args[0][1]
            
            if "loyihangiz haqida" in uzbek_message:
                print("✅ Uzbek lead collection message correct")
            else:
                print("❌ Uzbek lead collection message incorrect")
                return False
            
            mock_send.reset_mock()
            
            # Test English lead collection
            start_lead_collection(12346, None, "english")
            english_message = mock_send.call_args[0][1]
            
            if "about your project" in english_message:
                print("✅ English lead collection message correct")
            else:
                print("❌ English lead collection message incorrect")
                return False
        
        print("✅ Lead collection language support working")
        return True
        
    except Exception as e:
        print(f"❌ Lead collection language test error: {e}")
        return False

def main():
    """Run all behavior change tests."""
    print("🔄 Testing PremiumSoft Bot Behavior Changes")
    print("=" * 60)
    
    tests = [
        test_topic_aware_responses,
        test_language_detection,
        test_language_matching_responses,
        test_consolidated_follow_up_messages,
        test_order_prompt_language,
        test_lead_collection_language
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL BEHAVIOR CHANGE TESTS PASSED!")
        print()
        print("✅ Implemented features:")
        print("   🧵 Topic-aware responses")
        print("   🌐 Language matching (Uzbek/English)")
        print("   📝 Consolidated follow-up messages")
        print("   💼 Language-specific order prompts")
        print("   📋 Multilingual lead collection")
        print()
        print("🚀 Your bot now provides a much better user experience!")
        
        return 0
    else:
        print("❌ SOME BEHAVIOR TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
