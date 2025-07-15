import React, { useEffect, useRef } from "react";
import Lottie from "lottie-react";
import colorBallAnimation from "./animations/color-ball.json";

// Emotion to animation segment mapping (you must confirm these values!)
const EMOTION_TO_SEGMENT = {
  Angry: [0, 30],
  Neutral: [31, 60],
  Happy: [61, 90],
};

export default function ColorBall({ emotion = "Neutral" }) {
  const lottieRef = useRef();

  useEffect(() => {
    const segment = EMOTION_TO_SEGMENT[emotion] || EMOTION_TO_SEGMENT["Neutral"];
    lottieRef.current.setSpeed(1.5);
    lottieRef.current.playSegments(segment, true); // play from start to end of that emotion
  }, [emotion]);

  return (
    <div style={{ width: 300, height: 300 }}>
      <Lottie
        lottieRef={lottieRef}
        animationData={colorBallAnimation}
        loop={false}
        autoplay={false}
      />
    </div>
  );
}
