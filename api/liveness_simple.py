import json
import base64
import io
from PIL import Image
import numpy as np

def handler(request, response):
    try:
        if request.method != 'POST':
            response.status_code = 405
            response.body = json.dumps({'error': 'Method not allowed'})
            return

        content_type = request.headers.get("content-type", "")

        if "multipart/form-data" not in content_type:
            response.status_code = 400
            response.body = json.dumps({'error': 'Expected multipart/form-data'})
            return

        # Read body as bytes and parse manually (for multipart parsing)
        body_bytes = request.body
        boundary = content_type.split("boundary=")[-1]
        parts = body_bytes.split(f"--{boundary}".encode())

        image_data = None

        for part in parts:
            if b'Content-Disposition' in part and b'name="image"' in part:
                header_body_split = part.split(b'\r\n\r\n', 1)
                if len(header_body_split) > 1:
                    image_data = header_body_split[1].rstrip(b'\r\n--')

        if not image_data:
            response.status_code = 400
            response.body = json.dumps({"error": "No image field found"})
            return

        # Process image and return response
        result = process_image(image_data)
        response.status_code = 200
        response.body = json.dumps(result)
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({"error": str(e)})

def process_image(image_data):
    # Simulated dummy liveness analysis
    image_hash = hash(image_data) % 1000
    antispoof_score = 0.7 + (image_hash % 300) / 1000
    confidence = 0.6 + (image_hash % 400) / 1000
    eye_distance = 30 + (image_hash % 20)
    is_real = antispoof_score > 0.8

    return {
        "is_real": is_real,
        "antispoof_score": antispoof_score,
        "confidence": confidence,
        "eye_distance": float(eye_distance)
    }
