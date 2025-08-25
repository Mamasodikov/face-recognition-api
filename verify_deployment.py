#!/usr/bin/env python3
"""
Final verification script for Vercel deployment.
This ensures everything is ready for deployment.
"""

import sys
import os
from http.server import BaseHTTPRequestHandler

def test_imports():
    """Test that all imports work correctly."""
    print("🔍 Testing imports...")
    try:
        sys.path.append('.')
        from api.telegram import Handler, send_telegram_message, get_premiumsoft_info, setup_webhook, test_bot
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_handler_class():
    """Test that Handler class is properly defined."""
    print("🔍 Testing Handler class...")
    try:
        from api.telegram import Handler
        
        # Check if it's a class
        if not isinstance(Handler, type):
            print(f"❌ Handler is not a class: {type(Handler)}")
            return False
        
        # Check if it's a subclass of BaseHTTPRequestHandler
        if not issubclass(Handler, BaseHTTPRequestHandler):
            print("❌ Handler is not a subclass of BaseHTTPRequestHandler")
            return False
        
        print("✅ Handler class properly defined")
        return True
    except Exception as e:
        print(f"❌ Handler class error: {e}")
        return False

def test_functions():
    """Test that all functions work correctly."""
    print("🔍 Testing functions...")
    try:
        from api.telegram import get_premiumsoft_info, send_telegram_message
        
        # Test info function
        info = get_premiumsoft_info()
        if not info or "PremiumSoft.uz" not in info:
            print("❌ get_premiumsoft_info() not working")
            return False
        
        print("✅ All functions working")
        return True
    except Exception as e:
        print(f"❌ Function error: {e}")
        return False

def test_with_bot_token():
    """Test functions with real bot token."""
    print("🔍 Testing with bot token...")

    try:
        # We need to test this in a subprocess since BOT_TOKEN is loaded at import time
        import subprocess
        import json as json_module

        test_script = '''
import os
os.environ["TELEGRAM_BOT_TOKEN"] = "8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84"
import sys
sys.path.append(".")
from api.telegram import test_bot, setup_webhook
import json

# Test bot connectivity
result = test_bot()
print(json.dumps({"test_bot": result}))

# Test webhook setup
result = setup_webhook("test.vercel.app")
print(json.dumps({"setup_webhook": result}))
'''

        result = subprocess.run(['python3', '-c', test_script],
                              capture_output=True, text=True, cwd='.')

        if result.returncode != 0:
            print(f"❌ Bot token test failed: {result.stderr}")
            return False

        # Parse the output
        lines = result.stdout.strip().split('\n')
        test_bot_result = None
        webhook_result = None

        for line in lines:
            if line.startswith('{"test_bot":'):
                test_bot_result = json_module.loads(line)["test_bot"]
            elif line.startswith('{"setup_webhook":'):
                webhook_result = json_module.loads(line)["setup_webhook"]

        if not test_bot_result or not test_bot_result.get('success'):
            print(f"❌ Bot test failed: {test_bot_result}")
            return False

        print(f"✅ Bot test successful: {test_bot_result['bot_name']} (@{test_bot_result['username']})")

        if not webhook_result or not webhook_result.get('ok'):
            print(f"❌ Webhook setup failed: {webhook_result}")
            return False

        print("✅ Webhook setup successful")
        return True

    except Exception as e:
        print(f"❌ Bot token test error: {e}")
        return False

def check_file_structure():
    """Check that all required files exist."""
    print("🔍 Checking file structure...")
    
    required_files = [
        'api/telegram.py',
        'vercel.json',
        'requirements.txt'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            return False
    
    print("✅ All required files present")
    return True

def check_vercel_config():
    """Check vercel.json configuration."""
    print("🔍 Checking Vercel configuration...")
    
    try:
        import json
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check for required fields
        if 'version' not in config:
            print("❌ Missing 'version' in vercel.json")
            return False
        
        if 'builds' not in config:
            print("❌ Missing 'builds' in vercel.json")
            return False
        
        if 'routes' not in config:
            print("❌ Missing 'routes' in vercel.json")
            return False
        
        print("✅ Vercel configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Vercel config error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🚀 Verifying Telegram Bot for Vercel Deployment")
    print("=" * 60)
    
    tests = [
        check_file_structure,
        check_vercel_config,
        test_imports,
        test_handler_class,
        test_functions,
        test_with_bot_token
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your bot is ready for Vercel deployment!")
        print()
        print("📋 Deployment Steps:")
        print("1. Set environment variable in Vercel:")
        print("   TELEGRAM_BOT_TOKEN=8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84")
        print("2. Deploy: vercel --prod")
        print("3. Setup webhook: https://your-app.vercel.app/api/telegram?setup-webhook")
        print("4. Test bot: https://your-app.vercel.app/api/telegram?test-bot")
        print()
        print("🤖 Bot Info:")
        print("   Name: OptimusPremium")
        print("   Username: @optimuspremiumbot")
        print("   ID: 8018149559")
        
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == '__main__':
    exit(main())
