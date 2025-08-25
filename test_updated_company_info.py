#!/usr/bin/env python3
"""
Test the updated company information with new statistics and team details.
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

def test_updated_statistics():
    """Test that company info contains updated statistics."""
    print("📊 Testing updated company statistics...")
    try:
        from api.telegram import get_premiumsoft_info, get_premiumsoft_info_english
        
        # Test Uzbek version
        uzbek_info = get_premiumsoft_info()
        
        # Check for new statistics
        if "1208+ veb-sayt" in uzbek_info:
            print("✅ Updated website count in Uzbek")
        else:
            print("❌ Website count not updated in Uzbek")
            return False
        
        if "46+ mobil ilova" in uzbek_info:
            print("✅ Updated mobile app count in Uzbek")
        else:
            print("❌ Mobile app count not updated in Uzbek")
            return False
        
        if "75+ Telegram bot" in uzbek_info:
            print("✅ Telegram bot count added in Uzbek")
        else:
            print("❌ Telegram bot count missing in Uzbek")
            return False
        
        if "2268+ mijoz" in uzbek_info:
            print("✅ Client count added in Uzbek")
        else:
            print("❌ Client count missing in Uzbek")
            return False
        
        # Test English version
        english_info = get_premiumsoft_info_english()
        
        if "1208+ websites" in english_info:
            print("✅ Updated website count in English")
        else:
            print("❌ Website count not updated in English")
            return False
        
        if "46+ mobile applications" in english_info:
            print("✅ Updated mobile app count in English")
        else:
            print("❌ Mobile app count not updated in English")
            return False
        
        print("✅ Updated statistics working")
        return True
        
    except Exception as e:
        print(f"❌ Updated statistics test error: {e}")
        return False

def test_updated_team_info():
    """Test that team information is updated."""
    print("\n👥 Testing updated team information...")
    try:
        from api.telegram import get_premiumsoft_info, get_premiumsoft_info_english
        
        # Test Uzbek version
        uzbek_info = get_premiumsoft_info()
        
        # Check for updated team member name
        if "Muhammadaziz Mamasaodiqov" in uzbek_info:
            print("✅ Updated team member name in Uzbek")
        else:
            print("❌ Team member name not updated in Uzbek")
            return False
        
        if "Team Lead, mobil dasturchi" in uzbek_info:
            print("✅ Team Lead titles added in Uzbek")
        else:
            print("❌ Team Lead titles missing in Uzbek")
            return False
        
        # Test English version
        english_info = get_premiumsoft_info_english()
        
        if "Muhammadaziz Mamasaodiqov" in english_info:
            print("✅ Updated team member name in English")
        else:
            print("❌ Team member name not updated in English")
            return False
        
        if "Team Lead, Mobile Developer" in english_info:
            print("✅ Team Lead titles added in English")
        else:
            print("❌ Team Lead titles missing in English")
            return False
        
        print("✅ Updated team information working")
        return True
        
    except Exception as e:
        print(f"❌ Updated team info test error: {e}")
        return False

def test_updated_services():
    """Test that services list is updated."""
    print("\n🧭 Testing updated services list...")
    try:
        from api.telegram import get_premiumsoft_info, get_premiumsoft_info_english
        
        # Test Uzbek version
        uzbek_info = get_premiumsoft_info()
        
        # Check for new services
        if "IT-konsalting va raqamlashtirish strategiyasi" in uzbek_info:
            print("✅ IT consulting service added in Uzbek")
        else:
            print("❌ IT consulting service missing in Uzbek")
            return False
        
        if "Server texnik xizmat ko'rsatish" in uzbek_info:
            print("✅ Server support service added in Uzbek")
        else:
            print("❌ Server support service missing in Uzbek")
            return False
        
        if "bepul taqdim etiladi" in uzbek_info:
            print("✅ Free consultation mentioned in Uzbek")
        else:
            print("❌ Free consultation not mentioned in Uzbek")
            return False
        
        # Test English version
        english_info = get_premiumsoft_info_english()
        
        if "IT Consulting and Digitalization Strategy" in english_info:
            print("✅ IT consulting service added in English")
        else:
            print("❌ IT consulting service missing in English")
            return False
        
        if "provided free of charge" in english_info:
            print("✅ Free consultation mentioned in English")
        else:
            print("❌ Free consultation not mentioned in English")
            return False
        
        print("✅ Updated services list working")
        return True
        
    except Exception as e:
        print(f"❌ Updated services test error: {e}")
        return False

def test_company_values():
    """Test that company values are included."""
    print("\n💡 Testing company values and approach...")
    try:
        from api.telegram import get_premiumsoft_info, get_premiumsoft_info_english
        
        # Test Uzbek version
        uzbek_info = get_premiumsoft_info()
        
        # Check for company values
        if "Innovatsiya" in uzbek_info and "Mas'uliyat" in uzbek_info:
            print("✅ Company values added in Uzbek")
        else:
            print("❌ Company values missing in Uzbek")
            return False
        
        if "Eksportga yo'naltirilganlik" in uzbek_info:
            print("✅ Export orientation mentioned in Uzbek")
        else:
            print("❌ Export orientation missing in Uzbek")
            return False
        
        # Test English version
        english_info = get_premiumsoft_info_english()
        
        if "Innovation" in english_info and "Responsibility" in english_info:
            print("✅ Company values added in English")
        else:
            print("❌ Company values missing in English")
            return False
        
        if "Export Orientation" in english_info:
            print("✅ Export orientation mentioned in English")
        else:
            print("❌ Export orientation missing in English")
            return False
        
        print("✅ Company values working")
        return True
        
    except Exception as e:
        print(f"❌ Company values test error: {e}")
        return False

def test_ai_knowledge_base_updated():
    """Test that AI knowledge base contains updated information."""
    print("\n🧠 Testing AI knowledge base updates...")
    try:
        from api.telegram import get_company_knowledge_base
        
        kb = get_company_knowledge_base()
        
        # Check for updated statistics
        if "1208+ websites" in kb:
            print("✅ Updated website count in knowledge base")
        else:
            print("❌ Website count not updated in knowledge base")
            return False
        
        if "75+ Telegram bots" in kb:
            print("✅ Telegram bot count in knowledge base")
        else:
            print("❌ Telegram bot count missing in knowledge base")
            return False
        
        if "2268+ clients" in kb:
            print("✅ Client count in knowledge base")
        else:
            print("❌ Client count missing in knowledge base")
            return False
        
        # Check for new services
        if "IT Consulting and Digitalization Strategy" in kb:
            print("✅ New services in knowledge base")
        else:
            print("❌ New services missing in knowledge base")
            return False
        
        # Check for company values
        if "Innovation" in kb and "Export Orientation" in kb:
            print("✅ Company values in knowledge base")
        else:
            print("❌ Company values missing in knowledge base")
            return False
        
        print("✅ AI knowledge base updates working")
        return True
        
    except Exception as e:
        print(f"❌ AI knowledge base test error: {e}")
        return False

def test_info_command_with_updates():
    """Test that /info command shows updated information."""
    print("\n📋 Testing /info command with updates...")
    try:
        from api.telegram import handle_message
        
        with patch('api.telegram.send_telegram_message') as mock_send:
            # Test /info command
            info_message = {
                "chat": {"id": 12345, "type": "private"},
                "text": "/info",
                "from": {"first_name": "TestUser", "id": 12345}
            }
            
            handle_message(info_message)
            
            if mock_send.called:
                response = mock_send.call_args[0][1]
                
                # Check for updated statistics
                if "1208+ veb-sayt" in response:
                    print("✅ Updated statistics in /info command")
                else:
                    print("❌ Updated statistics missing in /info command")
                    return False
                
                # Check for company values
                if "Innovatsiya" in response:
                    print("✅ Company values in /info command")
                else:
                    print("❌ Company values missing in /info command")
                    return False
                
            else:
                print("❌ No response for /info command")
                return False
        
        print("✅ /info command updates working")
        return True
        
    except Exception as e:
        print(f"❌ /info command test error: {e}")
        return False

def main():
    """Run all updated company information tests."""
    print("📋 Testing Updated Company Information")
    print("=" * 60)
    
    tests = [
        test_updated_statistics,
        test_updated_team_info,
        test_updated_services,
        test_company_values,
        test_ai_knowledge_base_updated,
        test_info_command_with_updates
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL UPDATED COMPANY INFO TESTS PASSED!")
        print()
        print("✅ Updated information:")
        print("   📊 Statistics: 1208+ websites, 46+ mobile apps, 75+ bots, 2268+ clients")
        print("   👥 Team: Updated names and Team Lead titles")
        print("   🧭 Services: Added IT consulting and digitalization strategy")
        print("   💡 Values: Innovation, Responsibility, Youth Development, Export Orientation")
        print("   🧠 AI Knowledge: All updates included in knowledge base")
        print("   📋 Commands: /info shows all updated information")
        print()
        print("🚀 Your bot now has the latest comprehensive company information!")
        
        return 0
    else:
        print("❌ SOME UPDATED COMPANY INFO TESTS FAILED!")
        return 1

if __name__ == '__main__':
    exit(main())
