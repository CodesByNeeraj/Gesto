"""Process local camera frames through MediaPipe hand landmarks."""

from typing import Any

import cv2
import numpy as np


DEFAULT_MAX_NUM_HANDS = 1
DEFAULT_MIN_DETECTION_CONFIDENCE = 0.80
DEFAULT_MIN_TRACKING_CONFIDENCE = 0.80
FULL_CONFIDENCE = 1.0
FIST_GESTURE = "fist"
OPEN_PALM_GESTURE = "open-palm"
WRIST_LANDMARK_INDEX = 0
FINGER_LANDMARK_PAIRS = (
    (3, 4),
    (6, 8),
    (10, 12),
    (14, 16),
    (18, 20),
)


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

        landmarks = detectionResult.multi_hand_landmarks[0].landmark
        classification = classifyHandLandmarks(landmarks)
        if classification is None:
            return None

        gestureLabel, confidenceScore = classification
        if confidenceScore < threshold:
            return None

        return gestureLabel, confidenceScore


def createHandProcessor() -> Any:
    """Create MediaPipe's local hand-landmark processor on demand."""
    import mediapipe as mp

    return mp.solutions.hands.Hands(
        max_num_hands=DEFAULT_MAX_NUM_HANDS,
        min_detection_confidence=DEFAULT_MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=DEFAULT_MIN_TRACKING_CONFIDENCE,
    )


def classifyHandLandmarks(
    landmarks: list[Any],
) -> tuple[str, float] | None:
    """Classify supported gestures from one hand's landmark positions."""
    if not areAllFingersExtended(landmarks):
        if areAllFingersFolded(landmarks):
            return FIST_GESTURE, FULL_CONFIDENCE

        return None

    return OPEN_PALM_GESTURE, FULL_CONFIDENCE


def areAllFingersExtended(landmarks: list[Any]) -> bool:
    """Return whether every fingertip extends beyond its preceding joint."""
    if len(landmarks) <= FINGER_LANDMARK_PAIRS[-1][1]:
        return False

    wrist = landmarks[WRIST_LANDMARK_INDEX]
    return all(
        isFingerExtended(landmarks, wrist, jointIndex, tipIndex)
        for jointIndex, tipIndex in FINGER_LANDMARK_PAIRS
    )


def areAllFingersFolded(landmarks: list[Any]) -> bool:
    """Return whether every fingertip is closer to the wrist than its joint."""
    if len(landmarks) <= FINGER_LANDMARK_PAIRS[-1][1]:
        return False

    wrist = landmarks[WRIST_LANDMARK_INDEX]
    return all(
        not isFingerExtended(landmarks, wrist, jointIndex, tipIndex)
        for jointIndex, tipIndex in FINGER_LANDMARK_PAIRS
    )


def isFingerExtended(
    landmarks: list[Any], wrist: Any, jointIndex: int, tipIndex: int
) -> bool:
    """Return whether a fingertip extends beyond its preceding joint."""
    jointDistance = calculateSquaredDistance(wrist, landmarks[jointIndex])
    tipDistance = calculateSquaredDistance(wrist, landmarks[tipIndex])
    return tipDistance > jointDistance


def calculateSquaredDistance(firstPoint: Any, secondPoint: Any) -> float:
    """Return squared two-dimensional distance between MediaPipe landmarks."""
    horizontalDistance = firstPoint.x - secondPoint.x
    verticalDistance = firstPoint.y - secondPoint.y
    return horizontalDistance**2 + verticalDistance**2
