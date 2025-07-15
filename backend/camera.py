import cv2
import torch
import numpy as np
import torchvision.transforms as transforms
from emotion_lib.face_detector.face_detector import DnnDetector
from emotion_lib.model.model import Mini_Xception
from emotion_lib.utils import get_label_emotion, histogram_equalization
from emotion_lib.face_alignment.face_alignment import FaceAlignment
print(torch.cuda.is_available())  # Should print True if GPU is usable
print(torch.cuda.current_device())  # The index of the current CUDA device
print(torch.cuda.get_device_name(0))  # The name of the GPU (index 0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load model weights
model_path = 'emotion_lib/checkpoint/model_weights/weights_epoch_75.pth.tar'
checkpoint = torch.load(model_path, map_location=device)

mini_xception = Mini_Xception().to(device)
mini_xception.load_state_dict(checkpoint['mini_xception'])
mini_xception.eval()

# Face detector and alignment
face_detector = DnnDetector('emotion_lib/face_detector')  # or HaarCascadeDetector('face_detector')
face_alignment = FaceAlignment()

# Open webcam video stream (0 for default camera)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = face_detector.detect_faces(frame)

    for (x, y, w, h) in faces:
        # Align and preprocess face
        face_img = face_alignment.frontalize_face((x, y, w, h), frame)
        face_img = cv2.resize(face_img, (48, 48))
        face_img = histogram_equalization(face_img)

        # Convert to tensor and normalize
        face_tensor = transforms.ToTensor()(face_img).to(device)
        face_tensor = torch.unsqueeze(face_tensor, 0)

        with torch.no_grad():
            output = mini_xception(face_tensor)
            probs = torch.nn.Softmax(dim=1)(output)
            top_prob, top_idx = torch.max(probs, 1)
            emotion = get_label_emotion(top_idx.item())
            confidence = top_prob.item()

        # Draw bounding box and label
        label = f"{emotion} ({confidence*100:.1f}%)"
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 0), 2)

    cv2.imshow('Emotion Detection', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
