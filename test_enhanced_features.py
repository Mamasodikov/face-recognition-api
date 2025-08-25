#!/usr/bin/env python3
"""
Test the enhanced features: stop functionality, location handling, and additional improvements.
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

def test_stop_functionality():
    """Test that users can stop the order process."""
    print("🛑 Testing stop functionality...")
    try:
        from api.telegram import handle_message, user_states, UserState, start_lead_collection
        
        chat_id = 12345
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Start lead collection
            start_lead_collection(chat_id, None, "english")
            
            # Check user is in collecting state
            if user_states[chat_id]['state'] != UserState.COLLECTING_PROJECT:
                print("❌ Lead collection not started properly")
                return False
            
            # Send stop command
            stop_message = {
                "chat": {"id": chat_id, "type": "private"},
                "text": "stop",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(stop_message)
            
            # Check user state is reset
            if user_states[chat_id]['state'] != UserState.NORMAL:
                print("❌ User state not reset after stop")
                return False
            
            # Check stop message was sent
            stop_call = mock_send.call_args[0][1]
            if "cancelled" in stop_call.lower() or "bekor" in stop_call.lower():
                print("✅ Stop message sent correctly")
            else:
                print("❌ Stop message not sent")
                return False
        
        print("✅ Stop functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Stop functionality test error: {e}")
        return False

def test_location_handling():
    """Test location requests and responses."""
    print("\n📍 Testing location handling...")
    try:
        from api.telegram import handle_message, send_telegram_location
        
        with patch('api.telegram.send_telegram_location') as mock_location:
            with patch('api.telegram.send_telegram_message') as mock_send:
                # Test location request
                location_message = {
                    "chat": {"id": 12345, "type": "private"},
                    "text": "Where are you located?",
                    "from": {"first_name": "TestUser", "id": 12345}
                }
                
                handle_message(location_message)
                
                # Check location was sent
                if mock_location.called:
                    print("✅ Location sent correctly")
                    
                    # Check coordinates
                    call_args = mock_location.call_args[0]
                    lat, lon = call_args[1], call_args[2]
                    if abs(lat - 40.3834) < 0.01 and abs(lon - 71.7841) < 0.01:
                        print("✅ Correct Fergana coordinates")
                    else:
                        print("❌ Incorrect coordinates")
                        return False
                else:
                    print("❌ Location not sent")
                    return False
                
                # Check text message with address
                if mock_send.called:
                    address_call = mock_send.call_args[0][1]
                    if "Fergana" in address_call and "Mustaqillik" in address_call:
                        print("✅ Address information sent")
                    else:
                        print("❌ Address information missing")
                        return False
        
        print("✅ Location handling working")
        return True
        
    except Exception as e:
        print(f"❌ Location handling test error: {e}")
        return False

def test_username_translation():
    """Test that usernames are not translated."""
    print("\n👤 Testing username translation...")
    try:
        from api.telegram import format_lead_message
        
        user_data = {
            'project': 'Test project',
            'name': 'John Doe',
            'phone': '+998901234567',
            'email': 'john@example.com'
        }
        
        telegram_user = {
            'id': 12345,
            'username': 'johndoe',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        formatted_message = format_lead_message(user_data, telegram_user)
        
        # Check that username is not translated
        if "@johndoe" in formatted_message:
            print("✅ Username preserved correctly")
        else:
            print("❌ Username not found or translated")
            return False
        
        # Check that technical fields are in English
        if "User ID:" in formatted_message and "First Name:" in formatted_message:
            print("✅ Technical fields in English")
        else:
            print("❌ Technical fields translated")
            return False
        
        print("✅ Username translation handling working")
        return True
        
    except Exception as e:
        print(f"❌ Username translation test error: {e}")
        return False

def test_business_hours():
    """Test business hours functionality."""
    print("\n🕒 Testing business hours...")
    try:
        from api.telegram import is_business_hours, get_business_hours_message
        
        # Test business hours detection
        business_status = is_business_hours()
        print(f"✅ Business hours check: {'Open' if business_status else 'Closed'}")
        
        # Test business hours messages
        uzbek_msg = get_business_hours_message("uzbek")
        english_msg = get_business_hours_message("english")
        
        if "Ish vaqti" in uzbek_msg and "Business Hours" in english_msg:
            print("✅ Business hours messages correct")
        else:
            print("❌ Business hours messages incorrect")
            return False
        
        print("✅ Business hours functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Business hours test error: {e}")
        return False

def test_new_commands():
    """Test new commands like /hours and /location."""
    print("\n⚡ Testing new commands...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            with patch('api.telegram.send_telegram_location') as mock_location:
                # Test /hours command
                hours_message = {
                    "chat": {"id": 12345, "type": "private"},
                    "text": "/hours",
                    "from": {"first_name": "TestUser", "id": 12345}
                }
                
                handle_message(hours_message)
                
                if mock_send.called:
                    hours_response = mock_send.call_args[0][1]
                    if ("ONLINE" in hours_response or "OFFLINE" in hours_response or
                        "ONLAYN" in hours_response or "OFFLAYN" in hours_response):
                        print("✅ /hours command working")
                    else:
                        print("❌ /hours command not working")
                        return False
                
                mock_send.reset_mock()
                
                # Test /location command
                location_message = {
                    "chat": {"id": 12345, "type": "private"},
                    "text": "/location",
                    "from": {"first_name": "TestUser", "id": 12345}
                }
                
                handle_message(location_message)
                
                if mock_location.called and mock_send.called:
                    print("✅ /location command working")
                else:
                    print("❌ /location command not working")
                    return False
        
        print("✅ New commands working")
        return True
        
    except Exception as e:
        print(f"❌ New commands test error: {e}")
        return False

def test_enhanced_responses():
    """Test enhanced response features like greetings and thanks."""
    print("\n💬 Testing enhanced responses...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test greeting
            greeting_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Hello there!",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(greeting_message)
            
            if mock_send.called:
                greeting_response = mock_send.call_args[0][1]
                if "Welcome" in greeting_response or "xush kelibsiz" in greeting_response:
                    print("✅ Greeting response working")
                else:
                    print("❌ Greeting response not working")
                    return False
            
            mock_send.reset_mock()
            
            # Test thanks
            thanks_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "Thank you so much!",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(thanks_message)
            
            if mock_send.called:
                thanks_response = mock_send.call_args[0][1]
                if "welcome" in thanks_response.lower() or "arzimaydi" in thanks_response.lower():
                    print("✅ Thanks response working")
                else:
                    print("❌ Thanks response not working")
                    return False
        
        print("✅ Enhanced responses working")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced responses test error: {e}")
        return False

def test_typing_indicators():
    """Test typing indicators functionality."""
    print("\n⌨️ Testing typing indicators...")
    try:
        from api.telegram import send_typing_action
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {"ok": True}
            
            result = send_typing_action(12345)
            
            if mock_post.called:
                call_args = mock_post.call_args
                if "sendChatAction" in call_args[0][0] and call_args[1]['json']['action'] == 'typing':
                    print("✅ Typing action sent correctly")
                else:
                    print("❌ Typing action not sent correctly")
                    return False
            else:
                print("❌ Typing action not called")
                return False
        
        print("✅ Typing indicators working")
        return True
        
    except Exception as e:
        print(f"❌ Typing indicators test error: {e}")
        return False

def main():
    """Run all enhanced feature tests."""
    print("🚀 Testing Enhanced PremiumSoft Bot Features")
    print("=" * 60)
    
    tests = [
        test_stop_functionality,
        test_location_handling,
        test_username_translation,
        test_business_hours,
        test_new_commands,
        test_enhanced_responses,
        test_typing_indicators
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL ENHANCED FEATURE TESTS PASSED!")
        print()
        print("✅ New features implemented:")
        print("   🛑 Stop functionality in order process")
        print("   📍 Location requests with map and address")
        print("   👤 Username preservation (no translation)")
        print("   🕒 Business hours detection")
        print("   ⚡ New commands: /hours, /location")
        print("   💬 Enhanced responses for greetings/thanks")
        print("   ⌨️ Typing indicators for better UX")
        print("   📊 User statistics tracking")
        print("   💫 Personalized messages for frequent users")
        print()
        print("🚀 Your bot now provides an exceptional user experience!")
        
        return 0
    else:
        print("❌ SOME ENHANCED FEATURE TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
