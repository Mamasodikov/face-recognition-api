import json
import os
import requests
import traceback
from http.server import BaseHTTPRequestHandler

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

# This is the handler function expected by Vercel
def handler(request):
    try:
        if request.method == "GET":
            return {
                "statusCode": 200,
                "body": "Telegram bot is live! Use POST to interact."
            }

        if request.method == "POST":
            # Parse request body
            body = json.loads(request.body)
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

            return {
                "statusCode": 200,
                "body": "OK"
            }

        return {
            "statusCode": 405,
            "body": "Method not allowed"
        }

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        log_to_telegram(error_msg)
        return {
            "statusCode": 500,
            "body": f"Error: {error_msg}"
        }