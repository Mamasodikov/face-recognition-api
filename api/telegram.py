from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import logging

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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - used for webhook setup and testing."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        response_text = 'PremiumSoft.uz Info Bot is active!\n'
        
        if BOT_TOKEN:
            response_text += f"Bot token is configured\n"
        else:
            response_text += "WARNING: Bot token is not configured!\n"
            
        self.wfile.write(response_text.encode())

        # Set up webhook if requested
        if self.path == '/setup-webhook' or self.path.startswith('/setup-webhook'):
            if not BOT_TOKEN:
                error_msg = f"\nError: Bot token not configured"
                self.wfile.write(error_msg.encode())
                return

            try:
                host = self.headers.get('Host')

                if '=' in self.path:
                    custom_url = self.path.split('=')[1]
                    webhook_url = custom_url
                else:
                    webhook_url = f"https://{host}/api/telegram"

                # Validate webhook URL
                if not webhook_url.startswith('https://'):
                    error_msg = f"\nError: Webhook URL must use HTTPS"
                    self.wfile.write(error_msg.encode())
                    return

                # Set the webhook
                set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
                params = {
                    'url': webhook_url,
                    'drop_pending_updates': True
                }
                response = requests.post(set_webhook_url, json=params, timeout=10)
                result = response.json()

                webhook_result = f"\nWebhook setup result: {json.dumps(result)}"
                self.wfile.write(webhook_result.encode())

                if result.get('ok'):
                    logger.info(f"Webhook successfully set to {webhook_url}")
                else:
                    logger.error(f"Failed to set webhook: {result.get('description', 'Unknown error')}")

            except Exception as e:
                error_msg = f"\nError setting webhook: {str(e)}"
                self.wfile.write(error_msg.encode())
                logger.error(f"Error setting webhook: {e}")
        
        # Test endpoint
        elif self.path == '/test-bot':
            if not BOT_TOKEN:
                error_msg = f"\nError: Bot token not configured"
                self.wfile.write(error_msg.encode())
                return

            try:
                get_me_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
                response = requests.get(get_me_url, timeout=10)
                result = response.json()

                if result.get('ok'):
                    bot_info = result.get('result', {})
                    test_result = f"\nBot test successful!\nBot name: {bot_info.get('first_name', 'Unknown')}\nUsername: @{bot_info.get('username', 'Unknown')}"
                else:
                    test_result = f"\nBot test failed: {result.get('description', 'Unknown error')}"

                self.wfile.write(test_result.encode())

            except Exception as e:
                error_msg = f"\nError testing bot: {str(e)}"
                self.wfile.write(error_msg.encode())
    
    def do_POST(self):
        """Handle POST requests - process Telegram updates."""
        try:
            # Get the request body
            content_length = self.headers.get('Content-Length')
            if not content_length:
                logger.error("Missing Content-Length header")
                self._send_ok_response()
                return

            content_length = int(content_length)
            if content_length > 10000:  # Limit request size
                logger.error(f"Request too large: {content_length} bytes")
                self._send_ok_response()
                return

            post_data = self.rfile.read(content_length)
            update_json = post_data.decode('utf-8')

            logger.info("Received update")

            # Parse the update
            update = json.loads(update_json)

            # Process the update
            if 'message' in update:
                self._handle_message(update['message'])
            else:
                logger.info("Received non-message update (ignored)")

            self._send_ok_response()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in update: {e}")
            self._send_ok_response()
        except ValueError as e:
            logger.error(f"Invalid Content-Length: {e}")
            self._send_ok_response()
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            self._send_ok_response()

    def _handle_message(self, message):
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

    def _send_ok_response(self):
        """Send OK response to Telegram."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('OK'.encode())
