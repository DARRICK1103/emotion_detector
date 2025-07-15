from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import base64
import json

app = FastAPI()

@app.websocket("/ws/emotion")
async def emotion_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print("Received from client:", data)  # Check data received
            payload = json.loads(data)
            img_b64 = payload.get("image")
            if img_b64:
                header, encoded = img_b64.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                # Dummy emotion prediction:
                emotion = "Happy"
                await websocket.send_text(json.dumps({"emotion": emotion}))
            else:
                await websocket.send_text(json.dumps({"error": "No image data"}))
    except WebSocketDisconnect:
        print("Client disconnected")
