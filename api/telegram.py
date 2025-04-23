import json
import os
import requests
import traceback

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DEBUG_CHAT_ID = os.environ.get("DEBUG_CHAT_ID")

def send_telegram_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def log_to_telegram(message):
    if BOT_TOKEN and DEBUG_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": DEBUG_CHAT_ID, "text": f"DEBUG: {message}"}
            )
        except:
            pass

# Standard Python function for Vercel
def handler(req, res):
    if req.method == "GET":
        res.status = 200
        return "Telegram bot is live! Use POST to interact."
    
    if req.method == "POST":
        try:
            # Parse the request body
            body = req.json()
            
            # Try to send a debug message
            log_to_telegram(f"Webhook received: {json.dumps(body)}")
            
            if "message" in body:
                msg = body["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                
                if text == "/start":
                    send_telegram_message(chat_id, "Hi 👋! Send me a face photo and I'll tell you the liveness score 🧠.")
                elif "photo" in msg:
                    send_telegram_message(chat_id, "I received your photo! This is a simplified version that doesn't process images yet.")
                else:
                    send_telegram_message(chat_id, f"You said: {text}")
            
            res.status = 200
            return "OK"
        
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            log_to_telegram(f"Error: {error_msg}")
            
            res.status = 500
            return f"Error: {error_msg}"