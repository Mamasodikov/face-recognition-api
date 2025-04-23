import os
import requests
import sys

def setup_webhook(bot_token, vercel_url):
    """Set up the Telegram webhook"""
    webhook_url = f"https://{vercel_url}/api/telegram"
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"

    response = requests.get(api_url)
    data = response.json()

    if data.get("ok"):
        print(f"✅ Webhook successfully set to: {webhook_url}")
    else:
        print(f"❌ Failed to set webhook: {data.get('description')}")

if __name__ == "__main__":
    # Get bot token from environment or command line
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token and len(sys.argv) > 1:
        bot_token = sys.argv[1]

    if not bot_token:
        print("❌ Error: No bot token provided")
        print("Usage: python setup-webhook.py [BOT_TOKEN]")
        print("Or set the TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)

    # Get Vercel URL from environment or command line
    vercel_url = os.environ.get("VERCEL_URL")
    if not vercel_url and len(sys.argv) > 2:
        vercel_url = sys.argv[2]

    if not vercel_url:
        print("❌ Error: No Vercel URL provided")
        print("Usage: python setup-webhook.py [BOT_TOKEN] [VERCEL_URL]")
        print("Or set the VERCEL_URL environment variable")
        sys.exit(1)

    # Remove https:// if present
    vercel_url = vercel_url.replace("https://", "")

    # Set up the webhook
    setup_webhook(bot_token, vercel_url)