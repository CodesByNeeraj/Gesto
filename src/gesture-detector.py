"""Recognize built-in gestures with MediaPipe's local task model."""

from collections.abc import Callable
from collections import deque
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import time
from typing import Any

import cv2
import numpy as np


MODEL_FILE_PATH = (
    Path(__file__).parents[1] / "assets" / "models" / "gesture_recognizer.task"
)
MOVEMENT_FRAME_WINDOW = 20


class GestureDetector:
    """Recognize locally trained gestures from MediaPipe hand landmarks."""

    def __init__(
        self,
        recognizer: Any | None = None,
        imageFactory: Callable[[np.ndarray], Any] | None = None,
        customGestureDetector: Callable[
            [list[Any]], tuple[str, float] | None
        ] | None = None,
        timestampProvider: Callable[[], int] | None = None,
        recognizerFactory: Callable[[], Any] | None = None,
        movementGestureDetector: Callable[
            [list[list[Any]]], tuple[str, float] | None
        ] | None = None,
    ) -> None:
        self.recognizerFactory = recognizerFactory
        if recognizer is None:
            self.recognizerFactory = (
                recognizerFactory or createGestureRecognizer
            )
            self.recognizer = self.recognizerFactory()
        else:
            self.recognizer = recognizer
        self.imageFactory = imageFactory or createMediaPipeImage
        self.customGestureDetector = (
            customGestureDetector or createCustomGestureDetector()
        )
        self.movementGestureDetector = (
            movementGestureDetector or createMovementGestureDetector()
        )
        self.movementFrames: deque[list[Any]] = deque(
            maxlen=MOVEMENT_FRAME_WINDOW
        )
        self.timestampProvider = timestampProvider or getTimestampMilliseconds
        self.lastTimestampMilliseconds = -1

    def detectGesture(
        self, frame: np.ndarray | None, threshold: float
    ) -> tuple[str, float] | None:
        """Return a trained gesture above the user confidence threshold."""
        if frame is None or frame.size == 0:
            return None

        recognitionResult = self.getRecognitionResult(frame)
        landmarks = getFirstHandLandmarks(recognitionResult)
        if landmarks is not None:
            self.movementFrames.append(landmarks)
            movementResult = self.movementGestureDetector(
                list(self.movementFrames)
            )
            if movementResult is not None:
                gestureLabel, confidenceScore = movementResult
                if confidenceScore >= threshold:
                    return gestureLabel, confidenceScore
            customResult = self.customGestureDetector(landmarks)
            if customResult is not None:
                gestureLabel, confidenceScore = customResult
                if confidenceScore >= threshold:
                    return gestureLabel, confidenceScore

        return None

    def extractLandmarks(self, frame: np.ndarray | None) -> list[Any] | None:
        """Return one hand's landmarks for local custom-gesture training."""
        if frame is None or frame.size == 0:
            return None

        return getFirstHandLandmarks(self.getRecognitionResult(frame))

    def getRecognitionResult(self, frame: np.ndarray) -> Any:
        """Run the local recognizer once and return its full result."""
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mediaPipeImage = self.imageFactory(rgbFrame)
        return self.recognizer.recognize_for_video(
            mediaPipeImage,
            self.getNextTimestampMilliseconds(),
        )

    def getNextTimestampMilliseconds(self) -> int:
        """Return a strictly increasing timestamp for MediaPipe video mode."""
        timestampMilliseconds = self.timestampProvider()
        self.lastTimestampMilliseconds = max(
            timestampMilliseconds,
            self.lastTimestampMilliseconds + 1,
        )
        return self.lastTimestampMilliseconds

    def resetTracking(self) -> None:
        """Reset video tracking before evaluating the next gesture."""
        self.lastTimestampMilliseconds = -1
        self.movementFrames.clear()
        if self.recognizerFactory is None:
            return

        self.recognizer.close()
        self.recognizer = self.recognizerFactory()


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
        base_options=baseOptions,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
    )
    return mp.tasks.vision.GestureRecognizer.create_from_options(options)


def createMediaPipeImage(rgbFrame: np.ndarray) -> Any:
    """Convert an OpenCV RGB frame to a MediaPipe image."""
    import mediapipe as mp

    return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgbFrame)


def getTimestampMilliseconds() -> int:
    """Return a monotonic timestamp suitable for MediaPipe video processing."""
    return time.monotonic_ns() // 1_000_000


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


def createMovementGestureDetector() -> Callable[
    [list[list[Any]]], tuple[str, float] | None
]:
    """Load the local movement trainer from its kebab-case source file."""
    trainerPath = Path(__file__).with_name("movement-trainer.py")
    moduleSpec = spec_from_file_location("movementTrainer", trainerPath)
    if moduleSpec is None or moduleSpec.loader is None:
        raise ImportError("Unable to load the movement gesture trainer.")

    movementTrainer = module_from_spec(moduleSpec)
    moduleSpec.loader.exec_module(movementTrainer)
    return movementTrainer.detectMovementGesture


def getFirstHandLandmarks(recognitionResult: Any) -> list[Any] | None:
    """Return the first hand's landmarks when MediaPipe detected a hand."""
    handLandmarks = getattr(recognitionResult, "hand_landmarks", [])
    if not handLandmarks:
        return None

    firstHand = handLandmarks[0]
    return getattr(firstHand, "landmark", firstHand)
