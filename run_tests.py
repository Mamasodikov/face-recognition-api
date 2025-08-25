#!/usr/bin/env python3
"""
Test runner for the Telegram bot.
This script runs all tests and provides a comprehensive report.
"""

import unittest
import sys
import os
import json
from io import StringIO

def run_tests():
    """Run all tests and return results."""
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(current_dir, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print("=" * 70)
    print("TELEGRAM BOT TEST RESULTS")
    print("=" * 70)
    print(stream.getvalue())
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0

def check_bot_issues():
    """Check for common bot configuration issues."""
    print("\n" + "=" * 70)
    print("BOT CONFIGURATION CHECK")
    print("=" * 70)
    
    issues = []
    
    # Check if bot token is set
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        issues.append("❌ TELEGRAM_BOT_TOKEN environment variable is not set")
    else:
        if bot_token.startswith('test_') or len(bot_token) < 40:
            issues.append("⚠️  TELEGRAM_BOT_TOKEN appears to be a test token")
        else:
            print("✅ TELEGRAM_BOT_TOKEN is configured")
    
    # Check requirements.txt
    req_path = 'requirements.txt'
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            requirements = f.read()
        
        if 'python-telegram-bot' in requirements and 'requests' in requirements:
            issues.append("⚠️  Both python-telegram-bot and requests are in requirements.txt, but code only uses requests")
        
        print("✅ requirements.txt exists")
    else:
        issues.append("❌ requirements.txt not found")
    
    # Check vercel.json
    vercel_path = 'vercel.json'
    if os.path.exists(vercel_path):
        try:
            with open(vercel_path, 'r') as f:
                vercel_config = json.load(f)
            print("✅ vercel.json is valid JSON")
            
            # Check routes
            routes = vercel_config.get('routes', [])
            if any('/api/telegram' in route.get('src', '') for route in routes):
                print("✅ Telegram API routes are configured")
            else:
                issues.append("❌ Telegram API routes not found in vercel.json")
                
        except json.JSONDecodeError:
            issues.append("❌ vercel.json contains invalid JSON")
    else:
        issues.append("❌ vercel.json not found")
    
    # Check API directory
    if os.path.exists('api/telegram.py'):
        print("✅ Main bot file (api/telegram.py) exists")
    else:
        issues.append("❌ Main bot file (api/telegram.py) not found")
    
    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print("\nRECOMMENDATIONS:")
        print("1. Set TELEGRAM_BOT_TOKEN environment variable with your actual bot token")
        print("2. Consider removing python-telegram-bot from requirements.txt if not used")
        print("3. Test webhook setup using /api/telegram/setup-webhook endpoint")
        print("4. Test bot connectivity using /api/telegram/test-bot endpoint")
    else:
        print("\n✅ No configuration issues found!")
    
    return len(issues) == 0

def main():
    """Main function."""
    print("Starting Telegram Bot Test Suite...")
    
    # Check configuration first
    config_ok = check_bot_issues()
    
    # Run tests
    tests_ok = run_tests()
    
    # Final status
    print("\n" + "=" * 70)
    print("FINAL STATUS")
    print("=" * 70)
    
    if config_ok and tests_ok:
        print("✅ All tests passed and no configuration issues found!")
        return 0
    elif tests_ok:
        print("✅ All tests passed, but configuration issues were found.")
        return 1
    else:
        print("❌ Some tests failed or configuration issues were found.")
        return 2

if __name__ == '__main__':
    sys.exit(main())
