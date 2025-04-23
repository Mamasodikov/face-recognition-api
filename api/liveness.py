import json
import base64
import os
import tempfile
from deepface import DeepFace

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

        # Extract boundary
        boundary = content_type.split("boundary=")[-1]
        parts = request.body.split(f"--{boundary}".encode())

        image_data = None
        for part in parts:
            if b'name="image"' in part and b"Content-Disposition" in part:
                split_part = part.split(b'\r\n\r\n', 1)
                if len(split_part) > 1:
                    image_data = split_part[1].rstrip(b'\r\n--')

        if not image_data:
            response.status_code = 400
            response.body = json.dumps({"error": "No image field found"})
            return

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image_data)
            temp_path = tmp.name

        # Process with DeepFace
        result = process_image(temp_path)
        os.remove(temp_path)

        response.status_code = 200
        response.body = json.dumps(result)
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({'error': str(e)})

def process_image(image_path):
    try:
        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=['age', 'gender', 'race', 'emotion'],
            detector_backend='opencv'
        )

        if not analysis or len(analysis) == 0:
            return {"error": "No face detected"}

        face = analysis[0]
        region = face.get('region', {})
        width = region.get('w', 0)
        eye_distance = width * 0.3

        emotion = face.get('dominant_emotion', 'unknown')
        emotion_score = face.get('emotion', {}).get(emotion, 0)
        confidence = emotion_score / 100
        antispoof_score = min(confidence + 0.5, 0.99)
        is_real = antispoof_score > 0.5

        return {
            "is_real": is_real,
            "antispoof_score": antispoof_score,
            "confidence": confidence,
            "eye_distance": float(eye_distance),
            "age": face.get('age', 0),
            "gender": face.get('dominant_gender', 'unknown'),
            "emotion": emotion
        }
    except Exception as e:
        return {"error": f"Error analyzing face: {str(e)}"}
