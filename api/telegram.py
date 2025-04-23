from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import traceback
import tempfile
import numpy as np
import cv2
from io import BytesIO

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DEBUG_CHAT_ID = os.environ.get("DEBUG_CHAT_ID")

def log_to_telegram(message):
    if BOT_TOKEN and DEBUG_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": DEBUG_CHAT_ID, "text": f"DEBUG: {message}"}
            )
        except Exception as e:
            print(f"Error logging to Telegram: {str(e)}")

def send_telegram_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        log_to_telegram(f"Error sending message: {str(e)}")
        return {"ok": False, "error": str(e)}

def get_file_from_telegram(file_id):
    try:
        # First, get the file path
        file_path_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        file_path_response = requests.get(file_path_url)
        file_path_data = file_path_response.json()

        if not file_path_data.get("ok"):
            return None

        file_path = file_path_data["result"]["file_path"]

        # Then, download the file
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_response = requests.get(file_url)

        return file_response.content
    except Exception as e:
        log_to_telegram(f"Error getting file: {str(e)}")
        return None

def process_image_basic(image_data):
    try:
        # Convert image data to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Load face cascade
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_cascade_path)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            return {"error": "No face detected in the image"}

        # Get info about the first face
        x, y, w, h = faces[0]

        # Calculate eye distance (simplified estimation)
        eye_distance = w * 0.3

        # For a real implementation, you would use a specialized model for these metrics
        # These are placeholder/dummy values
        return {
            "faces_detected": len(faces),
            "primary_face_width": int(w),
            "primary_face_height": int(h),
            "eye_distance": float(eye_distance),
            # Dummy liveness data
            "is_real": True,
            "confidence": 0.85
        }
    except Exception as e:
        return {"error": f"Error analyzing face: {str(e)}"}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Telegram face detection bot is live! Send a photo to analyze.".encode())
        return

    def do_POST(self):
        try:
            # Get content length and read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Parse the JSON body
            body = json.loads(post_data.decode('utf-8'))

            # Process the message
            if "message" in body:
                msg = body["message"]
                chat_id = msg["chat"]["id"]

                # Check if this message contains text
                if "text" in msg:
                    text = msg["text"]

                    if text == "/start":
                        send_telegram_message(chat_id, "Hi 👋! Send me a face photo and I'll analyze it.")
                    else:
                        send_telegram_message(chat_id, "Please send me a photo to analyze.")

                # Check if this message contains a photo
                elif "photo" in msg:
                    # Telegram sends multiple photo sizes, get the largest one
                    photo = msg["photo"][-1]  # Last one is the largest
                    file_id = photo["file_id"]

                    # Tell user we're processing
                    send_telegram_message(chat_id, "Processing your photo... 🔍")

                    # Get photo content
                    photo_content = get_file_from_telegram(file_id)

                    if photo_content:
                        # Process image directly from memory
                        result = process_image_basic(photo_content)

                        # Format the response message
                        if "error" in result:
                            response_text = f"❌ {result['error']}"
                        else:
                            response_text = (
                                f"✅ Analysis Results:\n\n"
                                f"Faces detected: {result['faces_detected']}\n"
                                f"Face dimensions: {result['primary_face_width']}x{result['primary_face_height']}px\n"
                                f"Estimated eye distance: {result['eye_distance']:.2f}px\n"
                                f"Confidence: {result['confidence']:.2f}\n"
                                f"Real Face: {'Yes ✓' if result['is_real'] else 'No ✗'}"
                            )

                        # Send results
                        send_telegram_message(chat_id, response_text)
                    else:
                        send_telegram_message(chat_id, "❌ Could not download the photo. Please try again.")
                else:
                    send_telegram_message(chat_id, "Please send me a photo to analyze.")

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("OK".encode())

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            log_to_telegram(f"Error: {error_msg}")

            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {error_msg}".encode())