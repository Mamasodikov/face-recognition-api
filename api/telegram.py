from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from telegram import Bot, Update
import asyncio

# Get environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Get the base URL of the current deployment
def get_base_url():
    # In production, use the VERCEL_URL environment variable
    if os.environ.get("VERCEL_URL"):
        return f"https://{os.environ.get('VERCEL_URL')}"
    # For local development
    return "http://localhost:3000"

# Liveness API endpoint
def get_liveness_url():
    return f"{get_base_url()}/api/liveness"

async def handle_update(update_data):
    try:
        # Create bot instance
        bot = Bot(token=BOT_TOKEN)

        # Parse update
        update = Update.de_json(update_data, bot)

        # Handle commands
        if update.message and update.message.text:
            if update.message.text == '/start':
                await bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Hi 👋! Send me a face photo and I'll tell you the liveness score 🧠."
                )
                return

        # Handle photos
        if update.message and update.message.photo:
            # Send processing message
            processing_msg = await bot.send_message(
                chat_id=update.message.chat_id,
                text="🔍 Processing your image..."
            )

            try:
                # Get the photo with the highest resolution
                photo = update.message.photo[-1]
                file = await bot.get_file(photo.file_id)

                # Get the file URL
                file_url = file.file_path

                # Download the image
                image_response = requests.get(file_url)
                image_data = image_response.content

                # Send the image to the liveness API endpoint
                files = {"image": ("face.jpg", image_data)}
                response = requests.post(get_liveness_url(), files=files)

                # Check if the request was successful
                if response.status_code != 200:
                    await bot.edit_message_text(
                        chat_id=update.message.chat_id,
                        message_id=processing_msg.message_id,
                        text=f"⚠️ Error: API returned status code {response.status_code}"
                    )
                    return

                # Parse the response
                data = response.json()

                if "error" in data:
                    await bot.edit_message_text(
                        chat_id=update.message.chat_id,
                        message_id=processing_msg.message_id,
                        text=f"⚠️ {data['error']}"
                    )
                else:
                    # Format the response
                    reply = (
                        f"🤖 Liveness Info:\n"
                        f"✅ Real: {data['is_real']}\n"
                        f"🧪 Score: {data['antispoof_score']:.3f}\n"
                        f"🔍 Confidence: {data['confidence']:.2f}\n"
                        f"👁 Eye Distance: {data['eye_distance']:.2f}"
                    )
                    await bot.edit_message_text(
                        chat_id=update.message.chat_id,
                        message_id=processing_msg.message_id,
                        text=reply
                    )

            except Exception as e:
                await bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    message_id=processing_msg.message_id,
                    text=f"❌ Something went wrong while processing the image: {str(e)}"
                )

    except Exception as e:
        print(f"Error handling update: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Telegram Bot Webhook is active!'.encode())

        # Set the webhook URL
        if self.path == '/setup-webhook':
            bot = Bot(token=BOT_TOKEN)
            webhook_url = f"{get_base_url()}/api/telegram"
            result = asyncio.run(bot.set_webhook(url=webhook_url))
            self.wfile.write(f"\nWebhook setup result: {result}".encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_data = json.loads(post_data.decode())

        # Process the update asynchronously
        asyncio.run(handle_update(update_data))

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('OK'.encode())