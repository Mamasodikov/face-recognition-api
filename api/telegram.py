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
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    if parse_mode:
        payload["parse_mode"] = parse_mode
    
    try:
        logger.info(f"Sending message to {chat_id}")
        response = requests.post(url, json=payload, timeout=10)
        response_json = response.json()
        
        if not response_json.get("ok"):
            logger.error(f"Telegram API error: {response_json}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
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
            try:
                host = self.headers.get('Host')
                
                if '=' in self.path:
                    custom_url = self.path.split('=')[1]
                    webhook_url = custom_url
                else:
                    webhook_url = f"https://{host}/api/telegram"
                
                # Set the webhook
                set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}&drop_pending_updates=true"
                response = requests.get(set_webhook_url, timeout=10)
                result = response.json()
                
                webhook_result = f"\nWebhook setup result: {json.dumps(result)}"
                self.wfile.write(webhook_result.encode())
                logger.info(f"Webhook setup to {webhook_url}: {result}")
                
            except Exception as e:
                error_msg = f"\nError setting webhook: {str(e)}"
                self.wfile.write(error_msg.encode())
                logger.error(f"Error setting webhook: {e}")
        
        # Test endpoint
        elif self.path == '/test-bot':
            try:
                get_me_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
                response = requests.get(get_me_url, timeout=10)
                result = response.json()
                
                test_result = f"\nBot test result: {json.dumps(result)}"
                self.wfile.write(test_result.encode())
                
            except Exception as e:
                error_msg = f"\nError testing bot: {str(e)}"
                self.wfile.write(error_msg.encode())
    
    def do_POST(self):
        """Handle POST requests - process Telegram updates."""
        try:
            # Get the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_json = post_data.decode()
            
            logger.info(f"Received update")
            
            # Parse the update
            update = json.loads(update_json)
            
            # Process the update
            if 'message' in update:
                message = update['message']
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                user_name = message.get('from', {}).get('first_name', 'User')
                
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
            
            # Send response to Telegram
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            
            # Still return 200 to Telegram to prevent retries
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())
