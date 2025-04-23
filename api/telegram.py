import os
import json
import logging
import requests
from urllib.parse import urljoin

# Constants
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = os.environ.get("API_URL", "http://localhost:8000")  # Default to localhost if not set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_telegram_message(message):
    """Sends a message to a Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram bot token or chat ID not configured. Skipping message.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Optional: Use Markdown for formatting
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        logging.info("Telegram message sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def handle_update(update):
    """Handles an incoming update from the Telegram bot."""
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]

        logging.info(f"Received message: {text} from chat ID: {chat_id}")

        # Check if the message is a command
        if text.startswith("/process"):
            image_url = text.split(" ")[1]  # Extract the image URL from the command
            logging.info(f"Processing image URL: {image_url}")

            # Call the liveness API
            try:
                api_endpoint = urljoin(API_URL, "/liveness")
                response = requests.post(api_endpoint, json={"image_url": image_url})
                response.raise_for_status()
                data = response.json()

                # Format the response
                reply = (
                    f"🤖 Liveness Info:\n"
                    f"✅ Real: {data['is_real']}\n"
                    f"🧪 Score: {data['antispoof_score']:.3f}\n"
                    f"🔍 Confidence: {data['confidence']:.2f}\n"
                    f"👁 Eye Distance: {data['eye_distance']:.2f}"
                )
                
                # Add additional info if available
                if 'age' in data:
                    reply += f"\n\n👤 Additional Info:\n"
                    reply += f"🎂 Age: {data['age']}\n"
                    reply += f"⚧ Gender: {data['gender']}\n"
                    reply += f"😊 Emotion: {data['emotion']}"

                # Send the formatted response back to the user
                send_telegram_message(reply)

            except requests.exceptions.RequestException as e:
                error_message = f"Error calling liveness API: {e}"
                logging.error(error_message)
                send_telegram_message(error_message)
            except Exception as e:
                error_message = f"Error processing image: {e}"
                logging.error(error_message)
                send_telegram_message(error_message)
        else:
            # Handle other messages or commands
            send_telegram_message("I can only process images using the /process command.")

    return {"statusCode": 200}
