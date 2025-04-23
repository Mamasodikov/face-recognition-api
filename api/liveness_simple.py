from http.server import BaseHTTPRequestHandler
import json
import io
import os
import base64
import numpy as np
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
        # This is a simplified implementation that doesn't use any ML models
        # It just returns dummy values for demonstration purposes
        
        # In a real implementation, you would use a proper liveness detection model
        
        # Generate random-ish but consistent values
        image_hash = hash(image_data) % 1000
        antispoof_score = 0.7 + (image_hash % 300) / 1000  # Between 0.7 and 1.0
        confidence = 0.6 + (image_hash % 400) / 1000  # Between 0.6 and 1.0
        eye_distance = 30 + (image_hash % 20)  # Between 30 and 50
        is_real = antispoof_score > 0.8
        
        return {
            "is_real": is_real,
            "antispoof_score": antispoof_score,
            "confidence": confidence,
            "eye_distance": float(eye_distance)
        }
