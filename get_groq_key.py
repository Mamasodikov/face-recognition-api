#!/usr/bin/env python3
"""
Helper script to guide you through getting a Groq API key.
"""

import webbrowser
import time

def main():
    print("🤖 Getting Your Free Groq API Key")
    print("=" * 40)
    print()
    print("Groq provides free access to Llama3 AI models!")
    print("Perfect for our Telegram bot's AI features.")
    print()
    
    # Step 1
    print("📋 Step 1: Visit Groq Console")
    print("I'll open the Groq console in your browser...")
    time.sleep(2)
    
    try:
        webbrowser.open("https://console.groq.com/")
        print("✅ Browser opened to: https://console.groq.com/")
    except:
        print("❌ Couldn't open browser automatically")
        print("Please visit: https://console.groq.com/")
    
    print()
    input("Press Enter when you've signed up and logged in...")
    
    # Step 2
    print("\n📋 Step 2: Create API Key")
    print("1. Look for 'API Keys' in the left sidebar")
    print("2. Click 'Create API Key'")
    print("3. Give it a name like 'PremiumSoft Telegram Bot'")
    print("4. Copy the generated key (starts with 'gsk_')")
    print()
    
    api_key = input("Paste your Groq API key here: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return 1
    
    if not api_key.startswith('gsk_'):
        print("⚠️  Warning: Groq API keys usually start with 'gsk_'")
        print("Make sure you copied the correct key")
    
    # Step 3
    print("\n📋 Step 3: Test the API Key")
    print("Testing your API key...")
    
    try:
        import os
        os.environ['GROQ_API_KEY'] = api_key
        
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello, can you respond with just 'API key works!'?"}],
            model="llama3-8b-8192",
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Test Result: {result}")
        print("✅ Your Groq API key is working!")
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        print("Please check your API key and try again")
        return 1
    
    # Step 4
    print("\n📋 Step 4: Deploy to Vercel")
    print("Set these environment variables in Vercel:")
    print()
    print("TELEGRAM_BOT_TOKEN=8018149559:AAHap1B8ohX2-dof1r2mpXujkR8TY9ezz84")
    print(f"GROQ_API_KEY={api_key}")
    print()
    print("Then deploy with: vercel --prod")
    print()
    
    # Step 5
    print("📋 Step 5: Test Your AI Bot")
    print("After deployment:")
    print("1. Setup webhook: https://your-app.vercel.app/api/telegram?setup-webhook")
    print("2. Find @optimuspremiumbot on Telegram")
    print("3. Send: /start")
    print("4. Try: 'Tell me about your mobile development services'")
    print()
    
    print("🎉 Your AI-powered Telegram bot is ready!")
    print()
    print("💡 Pro Tips:")
    print("• Groq free tier includes generous limits")
    print("• The bot works even if AI is unavailable")
    print("• Check /ai command to see AI status")
    print("• Use /help to see all available commands")
    
    return 0

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Run the script again when ready!")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
