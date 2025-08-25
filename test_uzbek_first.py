#!/usr/bin/env python3
"""
Test that the bot defaults to Uzbek language and only switches to English when explicitly requested.
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

def test_language_detection_uzbek_first():
    """Test that language detection defaults to Uzbek."""
    print("🇺🇿 Testing Uzbek-first language detection...")
    try:
        from api.telegram import detect_language
        
        test_cases = [
            # Should default to Uzbek
            ("Hello", "uzbek"),  # Simple English should default to Uzbek
            ("Thank you", "uzbek"),  # Simple thanks should default to Uzbek
            ("What is your company?", "uzbek"),  # Simple question should default to Uzbek
            ("/start", "uzbek"),  # Commands should default to Uzbek
            ("", "uzbek"),  # Empty should default to Uzbek
            
            # Should only be English when explicitly requested
            ("Please respond in English", "english"),
            ("Can you speak English?", "english"),
            ("inglizcha javob bering", "english"),
            ("switch to english", "english"),
            ("I would like to speak in English", "english"),
            
            # Mixed content should default to Uzbek
            ("Hello, kompaniya haqida", "uzbek"),
            ("Thank you, rahmat", "uzbek"),
            
            # Strong Uzbek should stay Uzbek
            ("Salom, qanday yordam bera olasiz?", "uzbek"),
            ("Kompaniya haqida ma'lumot bering", "uzbek"),
        ]
        
        for text, expected_lang in test_cases:
            detected = detect_language(text)
            if detected == expected_lang:
                print(f"✅ '{text}' → {detected}")
            else:
                print(f"❌ '{text}' → {detected}, expected {expected_lang}")
                return False
        
        print("✅ Uzbek-first language detection working")
        return True
        
    except Exception as e:
        print(f"❌ Language detection test error: {e}")
        return False

def test_start_command_defaults_uzbek():
    """Test that /start command defaults to Uzbek."""
    print("\n🚀 Testing /start command defaults to Uzbek...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test regular /start (should be Uzbek)
            start_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/start",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(start_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                if "Salom" in response and "xush kelibsiz" in response:
                    print("✅ /start defaults to Uzbek")
                else:
                    print("❌ /start not defaulting to Uzbek")
                    return False
            else:
                print("❌ No response for /start")
                return False
        
        print("✅ /start command Uzbek default working")
        return True
        
    except Exception as e:
        print(f"❌ /start command test error: {e}")
        return False

def test_info_command_defaults_uzbek():
    """Test that /info command defaults to Uzbek."""
    print("\n📋 Testing /info command defaults to Uzbek...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test regular /info (should be Uzbek)
            info_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/info",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(info_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                if "Biz haqimizda" in response and "Farg'ona" in response:
                    print("✅ /info defaults to Uzbek")
                else:
                    print("❌ /info not defaulting to Uzbek")
                    return False
            else:
                print("❌ No response for /info")
                return False
        
        print("✅ /info command Uzbek default working")
        return True
        
    except Exception as e:
        print(f"❌ /info command test error: {e}")
        return False

def test_english_only_when_requested():
    """Test that English is only used when explicitly requested."""
    print("\n🇬🇧 Testing English only when explicitly requested...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test English request
            english_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Please respond in English",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(english_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                # Should contain English words and no Uzbek
                if "Hello" in response or "Welcome" in response or "help" in response:
                    print("✅ English used when explicitly requested")
                else:
                    print("❌ English not used when requested")
                    return False
            else:
                print("❌ No response for English request")
                return False
        
        print("✅ English only when requested working")
        return True
        
    except Exception as e:
        print(f"❌ English request test error: {e}")
        return False

def test_greeting_defaults_uzbek():
    """Test that greetings default to Uzbek."""
    print("\n👋 Testing greetings default to Uzbek...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test English greeting (should get Uzbek response)
            greeting_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Hello",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(greeting_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                if "Salom" in response and "xush kelibsiz" in response:
                    print("✅ English greeting gets Uzbek response")
                else:
                    print("❌ English greeting not getting Uzbek response")
                    return False
            else:
                print("❌ No response for greeting")
                return False
        
        print("✅ Greeting Uzbek default working")
        return True
        
    except Exception as e:
        print(f"❌ Greeting test error: {e}")
        return False

def test_ai_responses_default_uzbek():
    """Test that AI responses default to Uzbek."""
    print("\n🤖 Testing AI responses default to Uzbek...")
    try:
        from api.telegram import get_ai_response
        
        # Test with English input but should get Uzbek instruction
        if get_ai_response:  # Only test if AI is available
            # Mock the AI to test the language instruction
            with patch('api.telegram.groq_client') as mock_groq:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "Test response"
                mock_groq.chat.completions.create.return_value = mock_response
                
                # Test with English text but Uzbek language preference
                response = get_ai_response("What services do you offer?", "TestUser", "uzbek")
                
                # Check that the system prompt included Uzbek instruction
                call_args = mock_groq.chat.completions.create.call_args
                system_prompt = call_args[1]['messages'][0]['content']
                
                if "o'zbek tilida" in system_prompt.lower() or "uzbek" in system_prompt.lower():
                    print("✅ AI instructed to respond in Uzbek")
                else:
                    print("❌ AI not instructed to respond in Uzbek")
                    return False
        else:
            print("✅ AI not available, skipping AI response test")
        
        print("✅ AI response Uzbek default working")
        return True
        
    except Exception as e:
        print(f"❌ AI response test error: {e}")
        return False

def test_mixed_language_defaults_uzbek():
    """Test that mixed language content defaults to Uzbek."""
    print("\n🔀 Testing mixed language defaults to Uzbek...")
    try:
        from api.telegram import detect_language
        
        mixed_cases = [
            ("Hello, kompaniya haqida ma'lumot bering", "uzbek"),
            ("Thank you, rahmat sizga", "uzbek"),
            ("What is your xizmatlar?", "uzbek"),
            ("Please help me, yordam kerak", "uzbek"),
        ]
        
        for text, expected in mixed_cases:
            result = detect_language(text)
            if result == expected:
                print(f"✅ Mixed: '{text}' → {result}")
            else:
                print(f"❌ Mixed: '{text}' → {result}, expected {expected}")
                return False
        
        print("✅ Mixed language Uzbek default working")
        return True
        
    except Exception as e:
        print(f"❌ Mixed language test error: {e}")
        return False

def main():
    """Run all Uzbek-first tests."""
    print("🇺🇿 Testing Uzbek-First Bot Behavior")
    print("=" * 60)
    
    tests = [
        test_language_detection_uzbek_first,
        test_start_command_defaults_uzbek,
        test_info_command_defaults_uzbek,
        test_english_only_when_requested,
        test_greeting_defaults_uzbek,
        test_ai_responses_default_uzbek,
        test_mixed_language_defaults_uzbek
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL UZBEK-FIRST TESTS PASSED!")
        print()
        print("✅ Bot behavior:")
        print("   🇺🇿 Defaults to Uzbek for all interactions")
        print("   🇬🇧 Only uses English when explicitly requested")
        print("   🔄 Mixed language content defaults to Uzbek")
        print("   🤖 AI responses instructed to use Uzbek")
        print("   📋 All commands default to Uzbek")
        print("   👋 Greetings and responses in Uzbek")
        print()
        print("💡 Users can request English by saying:")
        print("   • 'inglizcha' or 'ingliz tilida'")
        print("   • 'please respond in English'")
        print("   • 'can you speak English?'")
        print()
        print("🚀 Your bot now speaks Uzbek first!")
        
        return 0
    else:
        print("❌ SOME UZBEK-FIRST TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
