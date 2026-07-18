"""Capture landmark samples and train one local custom gesture."""

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


CUSTOM_GESTURE_SAMPLE_TARGET = 40
FRAME_INTERVAL_SECONDS = 0.1
MOVEMENT_RECORDING_COUNT = 3
MOVEMENT_RECORDING_FRAME_COUNT = 20


class TrainingSession:
    """Own the camera while collecting samples for a named gesture."""

    def __init__(
        self,
        cameraHandler: Any,
        extractLandmarks: Callable[[Any], list[Any] | None],
        trainCustomGesture: Callable[[str, list[list[Any]]], Path],
        sampleTarget: int = CUSTOM_GESTURE_SAMPLE_TARGET,
        waitForNextFrame: Callable[[], None] | None = None,
    ) -> None:
        self.cameraHandler = cameraHandler
        self.extractLandmarks = extractLandmarks
        self.trainCustomGesture = trainCustomGesture
        self.sampleTarget = sampleTarget
        self.waitForNextFrame = waitForNextFrame or waitForCameraFrame

    def train(self, gestureLabel: str) -> Path:
        """Capture the target number of hand samples and save the model."""
        if not self.cameraHandler.openCamera():
            raise RuntimeError(
                "Camera unavailable for custom gesture training."
            )

        samples: list[list[Any]] = []
        try:
            while len(samples) < self.sampleTarget:
                landmarks = self.extractLandmarks(
                    self.cameraHandler.captureFrame()
                )
                if landmarks is not None:
                    samples.append(landmarks)
                self.waitForNextFrame()
        finally:
            self.cameraHandler.releaseCamera()

        return self.trainCustomGesture(gestureLabel, samples)


def waitForCameraFrame() -> None:
    """Avoid collecting identical camera frames during training."""
    time.sleep(FRAME_INTERVAL_SECONDS)


class MovementTrainingSession:
    """Capture several short landmark sequences for one movement gesture."""

    def __init__(
        self,
        cameraHandler: Any,
        extractLandmarks: Callable[[Any], list[Any] | None],
        trainMovementGesture: Callable[[str, list[list[list[Any]]]], Path],
        waitForNextFrame: Callable[[], None] | None = None,
    ) -> None:
        self.cameraHandler = cameraHandler
        self.extractLandmarks = extractLandmarks
        self.trainMovementGesture = trainMovementGesture
        self.waitForNextFrame = waitForNextFrame or waitForCameraFrame

    def train(self, gestureLabel: str) -> Path:
        """Record three movement sequences, then save their local model."""
        if not self.cameraHandler.openCamera():
            raise RuntimeError("Camera unavailable for movement training.")

        recordings: list[list[list[Any]]] = []
        try:
            for _ in range(MOVEMENT_RECORDING_COUNT):
                recording: list[list[Any]] = []
                while len(recording) < MOVEMENT_RECORDING_FRAME_COUNT:
                    landmarks = self.extractLandmarks(
                        self.cameraHandler.captureFrame()
                    )
                    if landmarks is not None:
                        recording.append(landmarks)
                    self.waitForNextFrame()
                recordings.append(recording)
        finally:
            self.cameraHandler.releaseCamera()

        return self.trainMovementGesture(gestureLabel, recordings)
