# 🎭 Emotion Detector

A full-stack emotion detection web app with a **Python FastAPI backend** and a **React.js frontend**. It uses a pre-trained deep learning model to analyze facial expressions from video or image input and predicts emotions in real time.

## 📑 Table of Contents

- [Features](#features)  
- [Technologies Used](#technologies-used)  
- [Setup and Installation](#setup-and-installation)  
  - [Backend](#backend)  
  - [Frontend](#frontend)  
- [Running the Application](#running-the-application)  
- [Usage](#usage)  
- [Contributing](#contributing)  
- [License](#license)

## 🚀 Features

- Real-time emotion detection from webcam/video input  
- FastAPI backend for image processing and inference  
- Interactive and user-friendly React.js frontend  
- Modular, full-stack architecture

## 🛠 Technologies Used

### Backend
- **Python 3.9**
- **FastAPI** – High-performance API framework  
- **Uvicorn** – ASGI server for running the backend  
- **Emotions-Recognition** – Pre-trained emotion detection model  

### Frontend
- **React.js** – Frontend library for UI  
- **npm** – JavaScript package manager  

## Setup and Installation

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install git+https://github.com/AmrElsersy/Emotions-Recognition.git
```

### Frontend

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend

```bash
# From the backend directory with virtual environment activated
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be running at:  
http://127.0.0.1:8000

### Start the Frontend

```bash
# From the frontend directory
npm start
```

Frontend will open at:  
http://localhost:3000

