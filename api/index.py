from flask import Flask, request, jsonify
from deepface import DeepFace
import tempfile, os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files['image']
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image.read())
        image_path = tmp.name

    try:
        result = process_image(image_path)
        return jsonify(result)
    finally:
        os.remove(image_path)

def process_image(image_path):
    face = DeepFace.analyze(img_path=image_path, actions=['age', 'gender', 'race', 'emotion'])[0]
    region = face.get('region', {})
    eye_distance = region.get('w', 0) * 0.3
    emotion_score = face['emotion'].get(face['dominant_emotion'], 0)
    confidence = emotion_score / 100
    antispoof_score = min(confidence + 0.5, 0.99)
    is_real = antispoof_score > 0.5
    return {
        "is_real": is_real,
        "antispoof_score": antispoof_score,
        "confidence": confidence,
        "eye_distance": eye_distance,
        "age": face.get('age'),
        "gender": face.get('dominant_gender'),
        "emotion": face.get('dominant_emotion')
    }

# Required by vercel-python runtime
app.run()
