from http.server import BaseHTTPRequestHandler
import json
import io
import os
import base64
import numpy as np
from PIL import Image
import cgi
from deepface import DeepFace

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse form data
        content_type, pdict = cgi.parse_header(self.headers.get('Content-Type', ''))
        
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # Get the image file
            if 'image' in form:
                fileitem = form['image']
                if fileitem.file:
                    # Read the image data
                    image_data = fileitem.file.read()
                    
                    try:
                        # Save image to a temporary file
                        temp_dir = "/tmp"
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_path = os.path.join(temp_dir, "face.jpg")
                        
                        with open(temp_path, "wb") as f:
                            f.write(image_data)
                        
                        # Process the image using DeepFace
                        result = self.process_image(temp_path)
                        
                        # Send response
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        
                        # Clean up
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                            
                        return
                    except Exception as e:
                        # Send error response
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())
                        return
        
        # If we get here, something went wrong
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Invalid request"}).encode())
    
    def process_image(self, image_path):
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
            
            # In a real implementation, you would use a proper liveness detection model
            # This is a simplified implementation using confidence from DeepFace
            
            # Extract useful information
            dominant_emotion = face_data.get('dominant_emotion', 'unknown')
            emotion_score = face_data.get('emotion', {}).get(dominant_emotion, 0)
            gender = face_data.get('dominant_gender', 'unknown')
            age = face_data.get('age', 0)
            
            # Calculate a dummy liveness score based on confidence
            # In a real implementation, you would use a specialized anti-spoofing model
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
