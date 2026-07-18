"""Recognize built-in gestures with MediaPipe's local task model."""

from collections.abc import Callable
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import cv2
import numpy as np


MODEL_FILE_PATH = (
    Path(__file__).parents[1] / "assets" / "models" / "gesture_recognizer.task"
)
BUILT_IN_GESTURE_LABELS = {
    "Closed_Fist": "fist",
    "Open_Palm": "open-palm",
    "Pointing_Up": "pointing",
    "Thumb_Down": "thumbs-down",
    "Thumb_Up": "thumbs-up",
    "Victory": "peace-sign",
}


class GestureDetector:
    """Recognize MediaPipe's canned gestures from local camera frames."""

    def __init__(
        self,
        recognizer: Any | None = None,
        imageFactory: Callable[[np.ndarray], Any] | None = None,
        customGestureDetector: Callable[
            [list[Any]], tuple[str, float] | None
        ] | None = None,
    ) -> None:
        self.recognizer = recognizer or createGestureRecognizer()
        self.imageFactory = imageFactory or createMediaPipeImage
        self.customGestureDetector = (
            customGestureDetector or createCustomGestureDetector()
        )

    def detectGesture(
        self, frame: np.ndarray | None, threshold: float
    ) -> tuple[str, float] | None:
        """Return a supported built-in gesture above the user threshold."""
        if frame is None or frame.size == 0:
            return None

        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mediaPipeImage = self.imageFactory(rgbFrame)
        recognitionResult = self.recognizer.recognize(mediaPipeImage)
        category = getTopGestureCategory(recognitionResult)
        if category is not None:
            gestureLabel = BUILT_IN_GESTURE_LABELS.get(category.category_name)
            confidenceScore = float(category.score)
            if gestureLabel is not None and confidenceScore >= threshold:
                return gestureLabel, confidenceScore

        landmarks = getFirstHandLandmarks(recognitionResult)
        if landmarks is None:
            return None

        customResult = self.customGestureDetector(landmarks)
        if customResult is None:
            return None

        gestureLabel, confidenceScore = customResult
        if confidenceScore < threshold:
            return None

        return gestureLabel, confidenceScore


def createGestureRecognizer() -> Any:
    """Create the local MediaPipe canned-gesture recognizer."""
    if not MODEL_FILE_PATH.exists():
        raise FileNotFoundError(f"Gesture model is missing: {MODEL_FILE_PATH}")

    import mediapipe as mp

    baseOptions = mp.tasks.BaseOptions(
        model_asset_path=str(MODEL_FILE_PATH),
        delegate=mp.tasks.BaseOptions.Delegate.CPU,
    )
    options = mp.tasks.vision.GestureRecognizerOptions(
        base_options=baseOptions
    )
    return mp.tasks.vision.GestureRecognizer.create_from_options(options)


def createMediaPipeImage(rgbFrame: np.ndarray) -> Any:
    """Convert an OpenCV RGB frame to a MediaPipe image."""
    import mediapipe as mp

    return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgbFrame)


def createCustomGestureDetector() -> Callable[
    [list[Any]], tuple[str, float] | None
]:
    """Load the custom trainer without violating Gesto's kebab-case files."""
    trainerPath = Path(__file__).with_name("custom-trainer.py")
    moduleSpec = spec_from_file_location("customTrainer", trainerPath)
    if moduleSpec is None or moduleSpec.loader is None:
        raise ImportError("Unable to load the custom gesture trainer.")

    customTrainer = module_from_spec(moduleSpec)
    moduleSpec.loader.exec_module(customTrainer)
    return customTrainer.detectCustomGesture


def getTopGestureCategory(recognitionResult: Any) -> Any | None:
    """Return the highest-scoring category for the first detected hand."""
    if not recognitionResult.gestures or not recognitionResult.gestures[0]:
        return None

    return recognitionResult.gestures[0][0]


def getFirstHandLandmarks(recognitionResult: Any) -> list[Any] | None:
    """Return the first hand's landmarks when MediaPipe detected a hand."""
    handLandmarks = getattr(recognitionResult, "hand_landmarks", [])
    if not handLandmarks:
        return None

    firstHand = handLandmarks[0]
    return getattr(firstHand, "landmark", firstHand)
