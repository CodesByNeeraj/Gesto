"""Tests for safe, mockable camera access."""

import importlib.util
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "camera-handler.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "cameraHandler", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
cameraHandler = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(cameraHandler)


def test_openCameraOpensDefaultCameraWhenAvailable() -> None:
    with patch("cv2.VideoCapture") as mockVideoCapture:
        mockCamera = mockVideoCapture.return_value
        mockCamera.isOpened.return_value = True
        handler = cameraHandler.CameraHandler()

        isOpen = handler.openCamera()

    assert isOpen is True
    mockVideoCapture.assert_called_once_with(0)
    mockCamera.set.assert_any_call(
        cameraHandler.cv2.CAP_PROP_FRAME_WIDTH,
        cameraHandler.CAMERA_FRAME_WIDTH,
    )
    mockCamera.set.assert_any_call(
        cameraHandler.cv2.CAP_PROP_FRAME_HEIGHT,
        cameraHandler.CAMERA_FRAME_HEIGHT,
    )
