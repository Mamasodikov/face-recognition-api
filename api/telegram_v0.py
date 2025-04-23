from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import traceback

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DEBUG_CHAT_ID = os.environ.get("DEBUG_CHAT_ID")

# Simple logging function that writes to a file
def log_debug(message):
    with open("/tmp/debug.log", "a") as f:
        f.write(f"{message}\n")

def send_telegram_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        log_debug(f"Sending message to {chat_id}: {text}")
        response = requests.post(url, json=payload)
        log_debug(f"Telegram API response: {response.text}")
        return response.json()
    except Exception as e:
        log_debug(f"Error sending message: {str(e)}")
        return {"ok": False, "error": str(e)}

def log_to_telegram(message):
    if BOT_TOKEN and DEBUG_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": DEBUG_CHAT_ID, "text": f"DEBUG: {message}"}
            )
        except Exception as e:
            log_debug(f"Error logging to Telegram: {str(e)}")

# Required handler class for Vercel Python functions
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Telegram bot is live! Use POST to interact.".encode())
        return
    
    def do_POST(self):
        try:
            log_debug("POST request received")
            
            # Get content length and read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Debug the raw post data
            log_debug(f"Raw POST data: {post_data.decode('utf-8')}")
            
            # Parse the JSON body
            body = json.loads(post_data.decode('utf-8'))
            log_debug(f"Parsed body: {json.dumps(body)}")
            
            # Log environment variables status
            log_debug(f"BOT_TOKEN set: {bool(BOT_TOKEN)}")
            log_debug(f"DEBUG_CHAT_ID set: {bool(DEBUG_CHAT_ID)}")
            
            # Process the message
            if "message" in body:
                msg = body["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                log_debug(f"Received message: '{text}' from chat_id: {chat_id}")
                
                # Also log to Telegram for easier debugging
                log_to_telegram(f"Received message: '{text}' from chat_id: {chat_id}")
                
                if text == "/start":
                    send_telegram_message(chat_id, "Hi 👋! Send me a face photo and I'll tell you the liveness score 🧠.")
                elif "photo" in msg:
                    send_telegram_message(chat_id, "I received your photo! This is a simplified version that doesn't process images yet.")
                else:
                    send_telegram_message(chat_id, f"You said: {text}")

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("OK".encode())
            
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            log_debug(f"Error: {error_msg}")
            log_to_telegram(f"Error: {error_msg}")
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {error_msg}".encode())