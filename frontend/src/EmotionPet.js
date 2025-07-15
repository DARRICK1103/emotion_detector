import React, { useEffect, useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";
import { motion, AnimatePresence } from "framer-motion";

const EMOTION_TO_COLOR = {
  Angry: "#ff4d4d",
  Neutral: "#ffd93b",
  Happy: "#4caf50",
  Sad: "#5a87f5",
  Surprise: "#ff9800",
};

const EMOTION_TO_EMOJI = {
  Angry: "😠",
  Neutral: "😐",
  Happy: "😄",
  Sad: "😢",
  Surprise: "😲",
};

export default function InteractiveEmotionPet() {
  const webcamRef = useRef(null);
  const wsRef = useRef(null);
  const [emotion, setEmotion] = useState("Neutral");
  const [confidence, setConfidence] = useState(0);
  const [connected, setConnected] = useState(false);
  const [webcamOn, setWebcamOn] = useState(true);

  // Setup WebSocket connection
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/emotion");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setConnected(true);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setConnected(false);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      setConnected(false);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.emotion && data.confidence !== undefined) {
          setEmotion(data.emotion);
          setConfidence(data.confidence);
        }
      } catch {
        // Ignore parse errors
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  // Send webcam frame over WebSocket every ~300ms
  const sendFrame = useCallback(() => {
    if (
      webcamRef.current &&
      webcamRef.current.getScreenshot &&
      wsRef.current &&
      wsRef.current.readyState === WebSocket.OPEN
    ) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        wsRef.current.send(JSON.stringify({ image: imageSrc }));
      }
    }
  }, []);

  useEffect(() => {
    if (!webcamOn) return;
    let active = true;

    async function loop() {
      if (!active) return;
      sendFrame();
      setTimeout(loop, 300);
    }

    loop();

    return () => {
      active = false;
    };
  }, [sendFrame, webcamOn]);

  return (
    <motion.div
      style={{
        textAlign: "center",
        padding: 20,
        minHeight: "100vh",
        backgroundColor: EMOTION_TO_COLOR[emotion] + "33", // translucent bg
        transition: "background-color 0.5s ease",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
      animate={{ scale: confidence > 0.7 ? 1.05 : 1 }}
      transition={{ duration: 0.5 }}
    >


      {webcamOn ? (
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          width={320}
          height={240}
          videoConstraints={{ facingMode: "user" }}
          style={{ borderRadius: 8, boxShadow: "0 0 15px rgba(0,0,0,0.3)" }}
        />
      ) : (
        <div
          style={{
            width: 320,
            height: 240,
            borderRadius: 8,
            backgroundColor: "#ddd",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 18,
            color: "#666",
            boxShadow: "0 0 15px rgba(0,0,0,0.1)",
          }}
        >
          Webcam Off
        </div>
      )}

      <motion.div
        style={{
          marginTop: 30,
          fontSize: 100,
          userSelect: "none",
          textShadow: "2px 2px 4px rgba(0,0,0,0.2)",
        }}
        key={emotion}
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.7, opacity: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
      >
        {EMOTION_TO_EMOJI[emotion] || "❓"}
      </motion.div>

      <motion.h2
        animate={{
          color: EMOTION_TO_COLOR[emotion] || "black",
          scale: [1, 1.1, 1],
          opacity: confidence > 0.4 ? 1 : 0.7,
        }}
        transition={{ duration: 1, repeat: Infinity, repeatType: "mirror" }}
        style={{ marginTop: 10, userSelect: "none" }}
      >
        {emotion} ({(confidence * 100).toFixed(1)}%)
      </motion.h2>

      <div
        style={{
          marginTop: 15,
          width: 320,
          height: 15,
          backgroundColor: "#eee",
          borderRadius: 8,
          overflow: "hidden",
          boxShadow: "inset 0 0 5px rgba(0,0,0,0.1)",
        }}
      >
        <motion.div
          style={{
            height: "100%",
            backgroundColor: EMOTION_TO_COLOR[emotion] || "#333",
            borderRadius: 8,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${confidence * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>


      <p style={{ marginTop: 20 }}>
        Status: {connected ? "Connected" : "Disconnected"}
      </p>
    </motion.div>
  );
}
