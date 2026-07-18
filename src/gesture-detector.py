"""Process local camera frames through MediaPipe hand landmarks."""

from typing import Any

import cv2
import numpy as np


DEFAULT_MAX_NUM_HANDS = 1
DEFAULT_MIN_DETECTION_CONFIDENCE = 0.80
DEFAULT_MIN_TRACKING_CONFIDENCE = 0.80


class GestureDetector:
    """Detect hands locally and provide a boundary for classification."""

    def __init__(self, handProcessor: Any | None = None) -> None:
        self.handProcessor = handProcessor or createHandProcessor()

    def detectGesture(
        self, frame: np.ndarray | None, threshold: float
    ) -> tuple[str, float] | None:
        """Process a frame and return an available classification."""
        if frame is None or frame.size == 0:
            return None

        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detectionResult = self.handProcessor.process(rgbFrame)
        if not detectionResult.multi_hand_landmarks:
            return None

        return None


def createHandProcessor() -> Any:
    """Create MediaPipe's local hand-landmark processor on demand."""
    import mediapipe as mp

    return mp.solutions.hands.Hands(
        max_num_hands=DEFAULT_MAX_NUM_HANDS,
        min_detection_confidence=DEFAULT_MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=DEFAULT_MIN_TRACKING_CONFIDENCE,
    )
