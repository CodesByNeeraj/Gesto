"""Tests for local MediaPipe gesture detection."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "gesture-detector.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "gestureDetector", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
gestureDetector = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(gestureDetector)


def test_detectGestureReturnsNoneWhenNoHandIsDetected() -> None:
    handProcessor = Mock()
    handProcessor.process.return_value.multi_hand_landmarks = None
    detector = gestureDetector.GestureDetector(handProcessor)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detectGesture(frame, threshold=0.80)

    assert result is None
    handProcessor.process.assert_called_once()


def test_detectGestureReturnsOpenPalmWhenAllFingersAreExtended() -> None:
    handProcessor = Mock()
    landmarks = createOpenPalmLandmarks()
    handProcessor.process.return_value.multi_hand_landmarks = [
        SimpleNamespace(landmark=landmarks)
    ]
    detector = gestureDetector.GestureDetector(handProcessor)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detectGesture(frame, threshold=0.80)

    assert result == ("open-palm", 1.0)


def test_detectGestureReturnsFistWhenAllFingersAreFolded() -> None:
    handProcessor = Mock()
    landmarks = createFistLandmarks()
    handProcessor.process.return_value.multi_hand_landmarks = [
        SimpleNamespace(landmark=landmarks)
    ]
    detector = gestureDetector.GestureDetector(handProcessor)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detectGesture(frame, threshold=0.80)

    assert result == ("fist", 1.0)


def createOpenPalmLandmarks() -> list[SimpleNamespace]:
    landmarks = [SimpleNamespace(x=0.5, y=0.9) for _ in range(21)]
    landmarks[3] = SimpleNamespace(x=0.3, y=0.6)
    landmarks[4] = SimpleNamespace(x=0.1, y=0.5)
    landmarks[6] = SimpleNamespace(x=0.4, y=0.5)
    landmarks[8] = SimpleNamespace(x=0.4, y=0.2)
    landmarks[10] = SimpleNamespace(x=0.5, y=0.5)
    landmarks[12] = SimpleNamespace(x=0.5, y=0.2)
    landmarks[14] = SimpleNamespace(x=0.6, y=0.5)
    landmarks[16] = SimpleNamespace(x=0.6, y=0.2)
    landmarks[18] = SimpleNamespace(x=0.7, y=0.55)
    landmarks[20] = SimpleNamespace(x=0.7, y=0.3)
    return landmarks


def createFistLandmarks() -> list[SimpleNamespace]:
    landmarks = [SimpleNamespace(x=0.5, y=0.9) for _ in range(21)]
    landmarks[3] = SimpleNamespace(x=0.3, y=0.6)
    landmarks[4] = SimpleNamespace(x=0.4, y=0.75)
    landmarks[6] = SimpleNamespace(x=0.4, y=0.5)
    landmarks[8] = SimpleNamespace(x=0.45, y=0.7)
    landmarks[10] = SimpleNamespace(x=0.5, y=0.5)
    landmarks[12] = SimpleNamespace(x=0.5, y=0.7)
    landmarks[14] = SimpleNamespace(x=0.6, y=0.5)
    landmarks[16] = SimpleNamespace(x=0.55, y=0.7)
    landmarks[18] = SimpleNamespace(x=0.7, y=0.55)
    landmarks[20] = SimpleNamespace(x=0.6, y=0.75)
    return landmarks
