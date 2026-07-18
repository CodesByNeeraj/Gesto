"""Manage exclusive access to Gesto's camera capture device."""

from typing import Any

import cv2


DEFAULT_CAMERA_INDEX = 0


class CameraHandler:
    """Open, capture from, and release one camera device."""

    def __init__(self, cameraIndex: int = DEFAULT_CAMERA_INDEX) -> None:
        self.cameraIndex = cameraIndex
        self.camera: Any | None = None

    def openCamera(self) -> bool:
        """Open the configured camera and report whether it is available."""
        self.releaseCamera()
        self.camera = cv2.VideoCapture(self.cameraIndex)

        if not self.camera.isOpened():
            self.releaseCamera()
            return False

        return True

    def captureFrame(self) -> Any | None:
        """Return the next camera frame, or None when no frame is available."""
        if self.camera is None:
            return None

        wasFrameRead, frame = self.camera.read()
        if not wasFrameRead:
            return None

        return frame

    def releaseCamera(self) -> None:
        """Release the camera when detection stops or the app exits."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
