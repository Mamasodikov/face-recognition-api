from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import logging
import traceback
import sys

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Debug function to log to a Telegram chat
def log_to_telegram(message):
    """Log a message to a Telegram chat for debugging."""
    # You can set this to your personal chat ID for debugging
    debug_chat_id = os.environ.get("DEBUG_CHAT_ID", "")
    if debug_chat_id and BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": debug_chat_id,
                "text": f"DEBUG: {message}",
                "disable_notification": True
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Error sending debug message: {e}")

def send_telegram_message(chat_id, text):
    """Send a message to a Telegram chat."""
    if not BOT_TOKEN:
        logger.error("No bot token provided")
        return False
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        logger.info(f"Sending message to {chat_id}: {text[:50]}...")
        response = requests.post(url, json=payload, timeout=10)
        response_json = response.json()
        logger.info(f"Telegram API response: {response_json}")
        
        if not response_json.get("ok"):
            logger.error(f"Telegram API error: {response_json}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - used for webhook setup and testing."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        response_text = 'Telegram Bot Webhook is active!\n'
        
        # Add bot token status
        if BOT_TOKEN:
            response_text += f"Bot token is configured (length: {len(BOT_TOKEN)})\n"
        else:
            response_text += "WARNING: Bot token is not configured!\n"
            
        self.wfile.write(response_text.encode())
        
        # Set up webhook if requested
        if self.path == '/setup-webhook' or self.path.startswith('/setup-webhook'):
            try:
                # Get the host from the headers or use the path parameter
                host = self.headers.get('Host')
                
                # If there's a custom URL in the path, use it
                if '=' in self.path:
                    custom_url = self.path.split('=')[1]
                    webhook_url = custom_url
                else:
                    # Otherwise construct from host
                    webhook_url = f"https://{host}/api/telegram"
                
                # Set the webhook
                set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
                response = requests.get(set_webhook_url, timeout=10)
                result = response.json()
                
                # Write the result
                webhook_result = f"\nWebhook setup result: {json.dumps(result)}"
                self.wfile.write(webhook_result.encode())
                logger.info(f"Webhook setup to {webhook_url}: {result}")
                
                # Also get webhook info
                get_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
                webhook_info = requests.get(get_webhook_url, timeout=10).json()
                webhook_info_text = f"\nWebhook info: {json.dumps(webhook_info)}"
                self.wfile.write(webhook_info_text.encode())
                
            except Exception as e:
                error_msg = f"\nError setting webhook: {str(e)}"
                self.wfile.write(error_msg.encode())
                logger.error(f"Error setting webhook: {e}")
                traceback.print_exc()
        
        # Test endpoint
        elif self.path == '/test-bot':
            try:
                # Try to get bot info as a test
                get_me_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
                response = requests.get(get_me_url, timeout=10)
                result = response.json()
                
                test_result = f"\nBot test result: {json.dumps(result)}"
                self.wfile.write(test_result.encode())
                logger.info(f"Bot test result: {result}")
                
            except Exception as e:
                error_msg = f"\nError testing bot: {str(e)}"
                self.wfile.write(error_msg.encode())
                logger.error(f"Error testing bot: {e}")
    
    def do_POST(self):
        """Handle POST requests - process Telegram updates."""
        try:
            # Get the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_json = post_data.decode()
            
            logger.info(f"Received update: {update_json[:200]}...")
            
            # Parse the update
            update = json.loads(update_json)
            
            # Process the update
            if 'message' in update:
                message = update['message']
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                logger.info(f"Received message from {chat_id}: {text}")
                
                # Handle /start command
                if text == '/start':
                    logger.info(f"Handling /start command for chat {chat_id}")
                    success = send_telegram_message(chat_id, "Hi 👋! Send me a face photo and I'll tell you the liveness score 🧠.")
                    logger.info(f"Message sent: {success}")
                
                # Handle photos
                elif 'photo' in message:
                    logger.info(f"Received photo from {chat_id}")
                    send_telegram_message(chat_id, "I received your photo! This is a simplified version that doesn't process images yet.")
                
                # Handle other messages
                else:
                    logger.info(f"Received other message from {chat_id}")
                    send_telegram_message(chat_id, f"You said: {text}\nSend /start to begin.")
            
            # Send response to Telegram
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            traceback.print_exc()
            
            # Try to log the error to Telegram for debugging
            error_details = f"Error: {str(e)}\n{traceback.format_exc()}"
            log_to_telegram(error_details)
            
            # Still return 200 to Telegram to prevent retries
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

def lambda_handler(event, context):
    """AWS Lambda handler."""
    if event.get('httpMethod') == 'POST':
        try:
            update = json.loads(event.get('body', '{}'))
            
            if 'message' in update:
                message = update['message']
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                # Handle /start command
                if text == '/start':
                    send_telegram_message(chat_id, "Hi 👋! Send me a face photo and I'll tell you the liveness score 🧠.")
                
                # Handle photos
                if 'photo' in message:
                    send_telegram_message(chat_id, "I received your photo! This is a simplified version that doesn't process images yet.")
            
            return {'statusCode': 200, 'body': 'OK'}
        except Exception as e:
            logger.error(f"Error in lambda handler: {e}")
            return {'statusCode': 500, 'body': f"Error: {str(e)}"}
    else:
        return {'statusCode': 200, 'body': 'Telegram Bot Webhook is active!'}
