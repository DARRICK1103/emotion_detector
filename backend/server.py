from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import torch
import torchvision.transforms as transforms
import base64
import re

from emotion_lib.face_detector.face_detector import DnnDetector, HaarCascadeDetector
from emotion_lib.model.model import Mini_Xception
from emotion_lib.utils import get_label_emotion, histogram_equalization
from emotion_lib.face_alignment.face_alignment import FaceAlignment

app = FastAPI()

# Allow CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model once
model_path = 'emotion_lib/checkpoint/model_weights/weights_epoch_75.pth.tar'
checkpoint = torch.load(model_path, map_location=device)

mini_xception = Mini_Xception().to(device)
mini_xception.load_state_dict(checkpoint['mini_xception'])
mini_xception.eval()

face_detector = DnnDetector('emotion_lib/face_detector')  # or HaarCascadeDetector('emotion_lib/face_detector')
face_alignment = FaceAlignment()

def decode_base64_image(data_url: str):
    # Extract base64 string from data URL
    img_str = re.sub('^data:image/.+;base64,', '', data_url)
    img_bytes = base64.b64decode(img_str)
    data = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img

@app.websocket("/ws/emotion")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Expect data JSON string like {"image": "data:image/jpeg;base64,...."}
            
            import json
            try:
                json_data = json.loads(data)
                img_data = json_data.get("image", None)
                if not img_data:
                    await websocket.send_text(json.dumps({"error": "No image data"}))
                    continue
            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
                continue

            img = decode_base64_image(img_data)
            if img is None:
                await websocket.send_text(json.dumps({"error": "Invalid image"}))
                continue

            faces = face_detector.detect_faces(img)
            if len(faces) == 0:
                await websocket.send_text(json.dumps({"error": "No faces detected"}))
                continue

            # For simplicity, return only first detected face emotion
            (x, y, w, h) = faces[0]
            face_img = face_alignment.frontalize_face((x, y, w, h), img)
            face_img = cv2.resize(face_img, (48, 48))
            face_img = histogram_equalization(face_img)

            face_tensor = transforms.ToTensor()(face_img).to(device)
            face_tensor = torch.unsqueeze(face_tensor, 0)

            with torch.no_grad():
                output = mini_xception(face_tensor)
                softmax = torch.nn.Softmax(dim=1)
                probs = softmax(output)
                top_prob, top_idx = torch.max(probs, 1)
                emotion = get_label_emotion(top_idx.item())
                confidence = top_prob.item()

            result = {
                'box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                'emotion': emotion,
                'confidence': round(confidence, 3)
            }

            await websocket.send_text(json.dumps(result))

    except WebSocketDisconnect:
        print("Client disconnected")

# To run:
# uvicorn server:app --host 0.0.0.0 --port 8000 --reload
