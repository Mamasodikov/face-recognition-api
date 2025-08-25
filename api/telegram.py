import json
import os
import requests
import logging
from urllib.parse import parse_qs, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id, text, parse_mode=None):
    """Send a message to a Telegram chat."""
    if not BOT_TOKEN:
        logger.error("No bot token provided")
        return False

    if not chat_id:
        logger.error("No chat_id provided")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        logger.info(f"Sending message to chat {chat_id}")
        response = requests.post(url, json=payload, timeout=10)
        response_json = response.json()

        if not response_json.get("ok"):
            error_code = response_json.get("error_code", "unknown")
            error_desc = response_json.get("description", "unknown error")
            logger.error(f"Telegram API error {error_code}: {error_desc}")
            return False

        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error sending message: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        return False

def get_premiumsoft_info():
    """Get information about premiumsoft.uz"""
    info_text = """
🏢 *PremiumSoft.uz* - Premium Software Solutions

🌟 *About Us*
PremiumSoft.uz is a leading software development company in Uzbekistan, specializing in creating high-quality digital solutions for businesses of all sizes.

💼 *Our Services*
• Custom Software Development
• Web Application Development
• Mobile App Development (iOS & Android)
• E-commerce Solutions
• Database Design & Management
• Cloud Solutions & Migration
• IT Consulting & Support
• UI/UX Design Services

🚀 *Technologies We Use*
• Frontend: React, Vue.js, Angular, HTML5/CSS3
• Backend: Node.js, Python, PHP, Java
• Mobile: React Native, Flutter, Swift, Kotlin
• Databases: PostgreSQL, MySQL, MongoDB
• Cloud: AWS, Google Cloud, Azure

🎯 *Why Choose Us*
✅ Expert team of developers
✅ Agile development methodology
✅ 24/7 technical support
✅ Competitive pricing
✅ On-time project delivery
✅ Post-launch maintenance

📞 *Contact Information*
🌐 Website: https://premiumsoft.uz
📧 Email: info@premiumsoft.uz
📱 Phone: +998 (XX) XXX-XX-XX
📍 Location: Tashkent, Uzbekistan

💬 *Get Started*
Ready to transform your business with premium software solutions? Contact us today for a free consultation!

#PremiumSoft #SoftwareDevelopment #Uzbekistan #TechSolutions
    """
    return info_text.strip()

def handle_message(message):
    """Handle a message from Telegram."""
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')
    user_name = message.get('from', {}).get('first_name', 'User')

    if not chat_id:
        logger.error("Message missing chat_id")
        return

    logger.info(f"Received message from {chat_id}: {text}")

    # Handle /start command
    if text == '/start':
        welcome_text = f"👋 Hello {user_name}!\n\nWelcome to PremiumSoft.uz Info Bot!\n\nUse /info to get detailed information about our company and services."
        send_telegram_message(chat_id, welcome_text)

    # Handle /info command
    elif text == '/info':
        info_text = get_premiumsoft_info()
        send_telegram_message(chat_id, info_text, parse_mode="Markdown")

    # Handle /help command
    elif text == '/help':
        help_text = """
🤖 *PremiumSoft.uz Info Bot*

Available commands:
/start - Start the bot
/info - Get detailed information about PremiumSoft.uz
/help - Show this help message

For more information about our services, use the /info command.
        """
        send_telegram_message(chat_id, help_text.strip(), parse_mode="Markdown")

    # Handle other messages
    else:
        response_text = f"Hello {user_name}! 👋\n\nI'm the PremiumSoft.uz info bot. Use /info to learn about our company and services.\n\nAvailable commands:\n• /start - Start the bot\n• /info - Company information\n• /help - Help message"
        send_telegram_message(chat_id, response_text)


def setup_webhook(host, custom_url=None):
    """Set up webhook for the bot."""
    if not BOT_TOKEN:
        return {"error": "Bot token not configured"}

    try:
        if custom_url:
            webhook_url = custom_url
        else:
            webhook_url = f"https://{host}/api/telegram"

        # Validate webhook URL
        if not webhook_url.startswith('https://'):
            return {"error": "Webhook URL must use HTTPS"}

        # Set the webhook
        set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        params = {
            'url': webhook_url,
            'drop_pending_updates': True
        }
        response = requests.post(set_webhook_url, json=params, timeout=10)
        result = response.json()

        if result.get('ok'):
            logger.info(f"Webhook successfully set to {webhook_url}")
        else:
            logger.error(f"Failed to set webhook: {result.get('description', 'Unknown error')}")

        return result

    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return {"error": str(e)}


def test_bot():
    """Test bot connectivity."""
    if not BOT_TOKEN:
        return {"error": "Bot token not configured"}

    try:
        get_me_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(get_me_url, timeout=10)
        result = response.json()

        if result.get('ok'):
            bot_info = result.get('result', {})
            return {
                "success": True,
                "bot_name": bot_info.get('first_name', 'Unknown'),
                "username": bot_info.get('username', 'Unknown'),
                "bot_id": bot_info.get('id')
            }
        else:
            return {"error": result.get('description', 'Unknown error')}

    except Exception as e:
        logger.error(f"Error testing bot: {e}")
        return {"error": str(e)}


def handler(request, response):
    """Main Vercel handler function."""
    try:
        # Handle GET requests
        if request.method == 'GET':
            # Basic status endpoint
            response_text = '✅ PremiumSoft.uz Info Bot is active on Vercel!\n'

            if BOT_TOKEN:
                response_text += "✅ Bot token is configured\n"
            else:
                response_text += "❌ WARNING: Bot token is not configured!\n"

            # Check for specific endpoints in query parameters
            if 'setup-webhook' in request.url:
                host = request.headers.get('host', 'unknown-host')
                result = setup_webhook(host)
                response_text += f"\nWebhook setup result: {json.dumps(result)}"

            elif 'test-bot' in request.url:
                result = test_bot()
                response_text += f"\nBot test result: {json.dumps(result)}"

            response.status(200).send(response_text)
            return

        # Handle POST requests (Telegram webhooks)
        elif request.method == 'POST':
            try:
                # Get request body
                update = request.json()

                logger.info("Received Telegram update")

                # Process the update
                if 'message' in update:
                    handle_message(update['message'])
                else:
                    logger.info("Received non-message update (ignored)")

                response.status(200).send('OK')
                return

            except Exception as e:
                logger.error(f"Error processing update: {e}")
                response.status(200).send('OK')
                return

        else:
            response.status(405).send('Method Not Allowed')
            return

    except Exception as e:
        logger.error(f"Handler error: {e}")
        response.status(500).send('Internal Server Error')
        return
