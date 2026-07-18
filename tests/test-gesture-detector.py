"""Tests for MediaPipe gesture recognition."""

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


def test_detectGestureMapsMediaPipeOpenPalmToGestoLabel() -> None:
    recognizer = Mock()
    recognizer.recognize.return_value = createGestureResult("Open_Palm", 0.92)
    detector = gestureDetector.GestureDetector(recognizer, lambda image: image)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detectGesture(frame, threshold=0.80)

    assert result == ("open-palm", 0.92)


def test_detectGestureRejectsResultBelowUserConfidenceThreshold() -> None:
    recognizer = Mock()
    recognizer.recognize.return_value = createGestureResult(
        "Closed_Fist", 0.65
    )
    detector = gestureDetector.GestureDetector(recognizer, lambda image: image)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detectGesture(frame, threshold=0.80)

    assert result is None


def test_detectGestureUsesCustomModelWhenNoBuiltInGestureMatches() -> None:
    recognizer = Mock()
    landmarks = [SimpleNamespace(x=0.5, y=0.5, z=0.0) for _ in range(21)]
    recognizer.recognize.return_value = SimpleNamespace(
        gestures=[],
        hand_landmarks=[SimpleNamespace(landmark=landmarks)],
    )
    customDetector = Mock(return_value=("three-finger-tap", 0.91))
    detector = gestureDetector.GestureDetector(
        recognizer,
        lambda image: image,
        customDetector,
    )
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detectGesture(frame, threshold=0.80)

    assert result == ("three-finger-tap", 0.91)
    customDetector.assert_called_once_with(landmarks)


def createGestureResult(label: str, score: float) -> SimpleNamespace:
    category = SimpleNamespace(category_name=label, score=score)
    return SimpleNamespace(gestures=[[category]])
