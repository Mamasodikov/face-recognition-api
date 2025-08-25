#!/usr/bin/env python3
"""
Test the updated company information: new address, phone number, and business hours.
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

def test_updated_address_info():
    """Test that company info contains updated address."""
    print("🏢 Testing updated address information...")
    try:
        from api.telegram import get_premiumsoft_info, get_premiumsoft_info_english
        
        # Test Uzbek version
        uzbek_info = get_premiumsoft_info()
        
        # Check for new address
        if "Ahmad Al-Fargʻoniy shoh koʻchasi, 53" in uzbek_info:
            print("✅ Uzbek address updated correctly")
        else:
            print("❌ Uzbek address not updated")
            return False
        
        # Check for phone number
        if "+998 73 244 05 35" in uzbek_info:
            print("✅ Phone number added to Uzbek info")
        else:
            print("❌ Phone number missing from Uzbek info")
            return False
        
        # Test English version
        english_info = get_premiumsoft_info_english()
        
        # Check for new address
        if "Ahmad Al-Fergani Shah Street, 53" in english_info:
            print("✅ English address updated correctly")
        else:
            print("❌ English address not updated")
            return False
        
        # Check for phone number
        if "+998 73 244 05 35" in english_info:
            print("✅ Phone number added to English info")
        else:
            print("❌ Phone number missing from English info")
            return False
        
        print("✅ Updated address information working")
        return True
        
    except Exception as e:
        print(f"❌ Updated address test error: {e}")
        return False

def test_updated_business_hours():
    """Test updated business hours (Monday-Saturday, 9:00-17:00)."""
    print("\n🕒 Testing updated business hours...")
    try:
        from api.telegram import is_business_hours, get_business_hours_message
        import datetime
        
        # Test business hours message
        uzbek_hours = get_business_hours_message("uzbek")
        english_hours = get_business_hours_message("english")
        
        # Check for updated hours
        if "Dushanba-Shanba, 9:00-17:00" in uzbek_hours:
            print("✅ Uzbek business hours updated correctly")
        else:
            print("❌ Uzbek business hours not updated")
            return False
        
        if "Monday-Saturday, 9:00-17:00" in english_hours:
            print("✅ English business hours updated correctly")
        else:
            print("❌ English business hours not updated")
            return False
        
        # Test business hours function exists and works
        try:
            current_status = is_business_hours()
            print(f"✅ Business hours function working (current status: {'Open' if current_status else 'Closed'})")
        except Exception as e:
            print(f"❌ Business hours function error: {e}")
            return False
        
        print("✅ Updated business hours working")
        return True
        
    except Exception as e:
        print(f"❌ Updated business hours test error: {e}")
        return False

def test_location_command_updates():
    """Test that location commands show updated address."""
    print("\n📍 Testing location command updates...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_location') as mock_location:
            with patch('api.telegram.send_telegram_message') as mock_send:
                # Test /location command
                location_message = {
                    "chat": {"id": 12345, "type": "private"},
                    "text": "/location",
                    "from": {"first_name": "TestUser", "id": 12345}
                }
                
                handle_message(location_message)
                
                # Check location was sent
                if mock_location.called:
                    print("✅ Location sent correctly")
                else:
                    print("❌ Location not sent")
                    return False
                
                # Check address in response
                if mock_send.called:
                    response = mock_send.call_args[0][1]
                    if "Ahmad Al-Fargʻoniy shoh koʻchasi, 53" in response:
                        print("✅ Updated address in location response")
                    else:
                        print("❌ Updated address missing from location response")
                        return False
                    
                    if "+998 73 244 05 35" in response:
                        print("✅ Phone number in location response")
                    else:
                        print("❌ Phone number missing from location response")
                        return False
                else:
                    print("❌ No text response for location")
                    return False
        
        print("✅ Location command updates working")
        return True
        
    except Exception as e:
        print(f"❌ Location command updates test error: {e}")
        return False

def test_location_keyword_detection():
    """Test that location keywords trigger updated address."""
    print("\n🗺️ Testing location keyword detection...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_location') as mock_location:
            with patch('api.telegram.send_telegram_message') as mock_send:
                # Test location keyword
                location_message = {
                    "chat": {"id": 12345, "type": "private"},
                    "text": "Where are you located?",
                    "from": {"first_name": "TestUser", "id": 12345}
                }
                
                handle_message(location_message)
                
                # Check location was sent
                if mock_location.called:
                    print("✅ Location keyword detected")
                else:
                    print("❌ Location keyword not detected")
                    return False
                
                # Check updated address in response
                if mock_send.called:
                    response = mock_send.call_args[0][1]
                    if "Ahmad Al-Fergani Shah Street, 53" in response:
                        print("✅ English address in keyword response")
                    else:
                        print("❌ English address missing from keyword response")
                        return False
                else:
                    print("❌ No text response for location keyword")
                    return False
        
        print("✅ Location keyword detection working")
        return True
        
    except Exception as e:
        print(f"❌ Location keyword detection test error: {e}")
        return False

def test_hours_command_updates():
    """Test that /hours command shows updated business hours."""
    print("\n⏰ Testing /hours command updates...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test /hours command
            hours_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/hours",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(hours_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                if "Dushanba-Shanba, 9:00-17:00" in response:
                    print("✅ Updated business hours in /hours command")
                else:
                    print("❌ Updated business hours missing from /hours command")
                    return False
            else:
                print("❌ No response for /hours command")
                return False
        
        print("✅ /hours command updates working")
        return True
        
    except Exception as e:
        print(f"❌ /hours command updates test error: {e}")
        return False

def test_knowledge_base_updates():
    """Test that AI knowledge base contains updated information."""
    print("\n🧠 Testing knowledge base updates...")
    try:
        from api.telegram import get_company_knowledge_base
        
        kb = get_company_knowledge_base()
        
        # Check for phone number
        if "+998 73 244 05 35" in kb:
            print("✅ Phone number in knowledge base")
        else:
            print("❌ Phone number missing from knowledge base")
            return False
        
        # Check for updated address
        if "Ahmad Al-Fergani Shah Street, 53" in kb:
            print("✅ Updated address in knowledge base")
        else:
            print("❌ Updated address missing from knowledge base")
            return False
        
        # Check for updated business hours
        if "Monday-Saturday, 9:00-17:00" in kb:
            print("✅ Updated business hours in knowledge base")
        else:
            print("❌ Updated business hours missing from knowledge base")
            return False
        
        print("✅ Knowledge base updates working")
        return True
        
    except Exception as e:
        print(f"❌ Knowledge base updates test error: {e}")
        return False

def main():
    """Run all updated information tests."""
    print("📋 Testing Updated PremiumSoft Information")
    print("=" * 60)
    
    tests = [
        test_updated_address_info,
        test_updated_business_hours,
        test_location_command_updates,
        test_location_keyword_detection,
        test_hours_command_updates,
        test_knowledge_base_updates
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL UPDATED INFORMATION TESTS PASSED!")
        print()
        print("✅ Updated information:")
        print("   🏢 New Address: Fargʻona, Ahmad Al-Fargʻoniy shoh koʻchasi, 53, 4-qavat")
        print("   📞 Phone Number: +998 73 244 05 35")
        print("   🕒 Business Hours: Monday-Saturday, 9:00-17:00")
        print("   📍 Location commands updated")
        print("   🧠 AI knowledge base updated")
        print("   🌐 Both Uzbek and English versions updated")
        print()
        print("🚀 Your bot now has the latest PremiumSoft contact information!")
        
        return 0
    else:
        print("❌ SOME UPDATED INFORMATION TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
