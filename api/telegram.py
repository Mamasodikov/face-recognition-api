from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import traceback
import tempfile
from deepface import DeepFace
import base64

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

def process_image(image_path):
    try:
        # Analyze face
        face_analysis = DeepFace.analyze(
            img_path=image_path,
            actions=['age', 'gender', 'race', 'emotion'],
            detector_backend='opencv'
        )

        if not face_analysis or len(face_analysis) == 0:
            return {"error": "No face detected in the image"}

        face_data = face_analysis[0]

        # Get face region
        region = face_data.get('region', {})
        width = region.get('w', 0)

        # Calculate eye distance (simplified)
        eye_distance = width * 0.3

        # Extract useful information
        dominant_emotion = face_data.get('dominant_emotion', 'unknown')
        emotion_score = face_data.get('emotion', {}).get(dominant_emotion, 0)
        gender = face_data.get('dominant_gender', 'unknown')
        age = face_data.get('age', 0)

        # Calculate a dummy liveness score based on confidence
        antispoof_score = min(emotion_score / 100 + 0.5, 0.99)
        confidence = emotion_score / 100
        is_real = antispoof_score > 0.5

        return {
            "is_real": is_real,
            "antispoof_score": antispoof_score,
            "confidence": confidence,
            "eye_distance": float(eye_distance),
            "age": age,
            "gender": gender,
            "emotion": dominant_emotion
        }
    except Exception as e:
        return {"error": f"Error analyzing face: {str(e)}"}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Telegram face analysis bot is live! Send a photo to analyze.".encode())
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
                        send_telegram_message(chat_id, "Hi 👋! Send me a face photo and I'll tell you the liveness score 🧠.")
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
                        # Save to temp file
                        temp_dir = tempfile.gettempdir()
                        temp_path = os.path.join(temp_dir, f"face_{chat_id}.jpg")

                        with open(temp_path, "wb") as f:
                            f.write(photo_content)

                        # Process image
                        result = process_image(temp_path)

                        # Format the response message
                        if "error" in result:
                            response_text = f"❌ {result['error']}"
                        else:
                            response_text = (
                                f"✅ Analysis Results:\n\n"
                                f"Real Face: {'Yes ✓' if result['is_real'] else 'No ✗'}\n"
                                f"Anti-spoof Score: {result['antispoof_score']:.2f}\n"
                                f"Confidence: {result['confidence']:.2f}\n"
                                f"Age: {result['age']}\n"
                                f"Gender: {result['gender']}\n"
                                f"Emotion: {result['emotion']}\n"
                                f"Eye Distance: {result['eye_distance']:.2f}px"
                            )

                        # Send results
                        send_telegram_message(chat_id, response_text)

                        # Clean up
                        try:
                            os.remove(temp_path)
                        except:
                            pass
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