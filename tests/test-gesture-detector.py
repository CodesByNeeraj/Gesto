"""Tests for local MediaPipe gesture detection."""

import importlib.util
from pathlib import Path
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
