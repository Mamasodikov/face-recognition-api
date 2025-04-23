from http.server import BaseHTTPRequestHandler
import json
import io
import base64
import numpy as np
import cv2
from PIL import Image
import cgi

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
                        # Process the image
                        result = self.process_image(image_data)
                        
                        # Send response
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
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
    
    def process_image(self, image_data):
        # Convert image data to numpy array
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        # Convert to BGR (OpenCV format) if it's RGB
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        
        # Load face detector
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return {"error": "No face detected in the image"}
        
        # Get the first face
        x, y, w, h = faces[0]
        
        # Calculate eye distance (simplified)
        eye_distance = w * 0.3
        
        # In a real implementation, you would use a proper liveness detection model here
        # This is just a dummy implementation
        
        # Dummy liveness score calculation
        # In a real implementation, this would be the output of a ML model
        antispoof_score = 0.92
        confidence = 0.85
        is_real = antispoof_score > 0.5
        
        return {
            "is_real": is_real,
            "antispoof_score": antispoof_score,
            "confidence": confidence,
            "eye_distance": float(eye_distance)
        }