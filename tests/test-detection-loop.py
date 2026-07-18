"""Tests for the gesture-to-action detection loop."""

import importlib.util
from pathlib import Path
import subprocess
from unittest.mock import Mock

import numpy as np


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "detection-loop.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "detectionLoop", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
detectionLoop = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(detectionLoop)


def test_processNextFrameExecutesMappedActionForDetectedGesture() -> None:
    cameraHandler = Mock()
    cameraHandler.captureFrame.return_value = np.zeros((480, 640, 3))
    gestureDetector = Mock()
    gestureDetector.detectGesture.return_value = ("open-palm", 0.92)
    mapGestureToAction = Mock(return_value={"action": "take-screenshot"})
    executeAction = Mock()
    loop = detectionLoop.DetectionLoop(
        cameraHandler,
        gestureDetector,
        mapGestureToAction,
        executeAction,
        createConfig(),
        Mock(return_value=100.0),
    )

    wasActionExecuted = loop.processNextFrame()

    assert wasActionExecuted is True
    executeAction.assert_called_once_with({"action": "take-screenshot"})
    gestureDetector.resetTracking.assert_called_once_with()


def test_processNextFrameIgnoresGestureDuringItsCooldown() -> None:
    cameraHandler = Mock()
    cameraHandler.captureFrame.return_value = np.zeros((480, 640, 3))
    gestureDetector = Mock()
    gestureDetector.detectGesture.return_value = ("open-palm", 0.92)
    mapGestureToAction = Mock(return_value={"action": "take-screenshot"})
    executeAction = Mock()
    loop = detectionLoop.DetectionLoop(
        cameraHandler,
        gestureDetector,
        mapGestureToAction,
        executeAction,
        createConfig(),
        Mock(side_effect=[100.0, 101.0]),
    )

    loop.processNextFrame()
    wasActionExecuted = loop.processNextFrame()

    assert wasActionExecuted is False
    executeAction.assert_called_once()


def test_processNextFrameReportsDetectedGestureBeforeMappingAction() -> None:
    cameraHandler = Mock()
    cameraHandler.captureFrame.return_value = np.zeros((480, 640, 3))
    gestureDetector = Mock()
    gestureDetector.detectGesture.return_value = ("open-palm", 0.92)
    onDetection = Mock()
    loop = detectionLoop.DetectionLoop(
        cameraHandler,
        gestureDetector,
        Mock(return_value=None),
        Mock(),
        createConfig(),
        Mock(return_value=100.0),
        onDetection,
    )

    loop.processNextFrame()

    onDetection.assert_called_once_with("open-palm", 0.92)


def test_processNextFrameReportsExecutedAction() -> None:
    cameraHandler = Mock()
    cameraHandler.captureFrame.return_value = np.zeros((480, 640, 3))
    gestureDetector = Mock()
    gestureDetector.detectGesture.return_value = ("open-palm", 0.92)
    onActionExecuted = Mock()
    action = {"action": "take-screenshot"}
    loop = detectionLoop.DetectionLoop(
        cameraHandler,
        gestureDetector,
        Mock(return_value=action),
        Mock(),
        createConfig(),
        Mock(return_value=100.0),
        onActionExecuted=onActionExecuted,
    )

    loop.processNextFrame()

    onActionExecuted.assert_called_once_with("open-palm", action)


def test_processNextFrameReportsActionFailureWithoutStoppingLoop() -> None:
    cameraHandler = Mock()
    cameraHandler.captureFrame.return_value = np.zeros((480, 640, 3))
    gestureDetector = Mock()
    gestureDetector.detectGesture.return_value = ("open-palm", 0.92)
    action = {"action": "open-app", "value": "Missing App"}
    executeAction = Mock(
        side_effect=subprocess.CalledProcessError(1, ["open", "-a"])
    )
    onActionFailed = Mock()
    loop = detectionLoop.DetectionLoop(
        cameraHandler,
        gestureDetector,
        Mock(return_value=action),
        executeAction,
        createConfig(),
        Mock(return_value=100.0),
        onActionFailed=onActionFailed,
    )

    wasActionExecuted = loop.processNextFrame()

    assert wasActionExecuted is False
    gestureDetector.resetTracking.assert_called_once_with()
    onActionFailed.assert_called_once()


def createConfig() -> dict[str, object]:
    return {
        "gestures": [],
        "settings": {
            "confidenceThreshold": 0.80,
            "cooldownSeconds": 5,
        },
    }
