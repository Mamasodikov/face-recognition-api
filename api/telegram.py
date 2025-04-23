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

def send_telegram_message(chat_id, text):
    """Send a message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - used for webhook setup."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Telegram Bot Webhook is active!'.encode())
        
        # Set up webhook if requested
        if self.path == '/setup-webhook':
            try:
                # Get the host from the headers
                host = self.headers.get('Host', 'localhost')
                webhook_url = f"https://{host}/api/telegram"
                
                # Set the webhook
                set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
                response = requests.get(set_webhook_url)
                result = response.json()
                
                # Write the result
                self.wfile.write(f"\nWebhook setup result: {json.dumps(result)}".encode())
                logger.info(f"Webhook setup result: {result}")
            except Exception as e:
                self.wfile.write(f"\nError setting webhook: {str(e)}".encode())
                logger.error(f"Error setting webhook: {e}")
    
    def do_POST(self):
        """Handle POST requests - process Telegram updates."""
        try:
            # Get the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode())
            
            logger.info(f"Received update: {update}")
            
            # Process the update
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
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            self.send_response(500)
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
