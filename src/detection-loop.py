"""Run local gesture detection and execute configured actions."""

import time
from collections.abc import Callable
from typing import Any


CONFIDENCE_THRESHOLD_KEY = "confidenceThreshold"
COOLDOWN_SECONDS_KEY = "cooldownSeconds"
SETTINGS_KEY = "settings"


class DetectionLoop:
    """Connect camera capture, gesture recognition, mapping, and execution."""

    def __init__(
        self,
        cameraHandler: Any,
        gestureDetector: Any,
        mapGestureToAction: Callable[
            [str, dict[str, Any]], dict[str, Any] | None
        ],
        executeAction: Callable[[dict[str, Any]], None],
        config: dict[str, Any],
        timeProvider: Callable[[], float] = time.monotonic,
        onDetection: Callable[[str, float], None] | None = None,
    ) -> None:
        self.cameraHandler = cameraHandler
        self.gestureDetector = gestureDetector
        self.mapGestureToAction = mapGestureToAction
        self.executeAction = executeAction
        self.config = config
        self.timeProvider = timeProvider
        self.onDetection = onDetection
        self.lastTriggeredAt: dict[str, float] = {}

    def startDetection(self) -> bool:
        """Open the camera before processing frames."""
        return bool(self.cameraHandler.openCamera())

    def stopDetection(self) -> None:
        """Release the camera when detection stops."""
        self.cameraHandler.releaseCamera()

    def processNextFrame(self) -> bool:
        """Process one frame and execute its mapped action when permitted."""
        frame = self.cameraHandler.captureFrame()
        settings = self.config[SETTINGS_KEY]
        threshold = float(settings[CONFIDENCE_THRESHOLD_KEY])
        detection = self.gestureDetector.detectGesture(frame, threshold)
        if detection is None:
            return False

        gestureLabel, confidenceScore = detection
        if self.onDetection is not None:
            self.onDetection(gestureLabel, confidenceScore)

        if confidenceScore < threshold:
            return False

        if self.isGestureInCooldown(gestureLabel):
            return False

        action = self.mapGestureToAction(gestureLabel, self.config)
        if action is None:
            return False

        self.executeAction(action)
        self.lastTriggeredAt[gestureLabel] = self.timeProvider()
        return True

    def isGestureInCooldown(self, gestureLabel: str) -> bool:
        """Return whether the same gesture was triggered too recently."""
        if gestureLabel not in self.lastTriggeredAt:
            return False

        settings = self.config[SETTINGS_KEY]
        cooldownSeconds = float(settings[COOLDOWN_SECONDS_KEY])
        elapsedSeconds = (
            self.timeProvider() - self.lastTriggeredAt[gestureLabel]
        )
        return elapsedSeconds < cooldownSeconds
