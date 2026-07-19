"""Tests for Gesto application lifecycle management."""

import importlib.util
import threading
from pathlib import Path
from unittest.mock import Mock


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "main.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "gestoMain", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
gestoMain = importlib.util.module_from_spec(
    MODULE_SPEC
)
MODULE_SPEC.loader.exec_module(gestoMain)


def test_stopDetectionWaitsForWorkerBeforeReleasingCamera() -> None:
    application = gestoMain.GestoApplication.__new__(
        gestoMain.GestoApplication
    )
    application.stopEvent = Mock()
    application.detectionLoop = Mock()
    application.detectionThread = Mock()
    application.detectionThread.is_alive.return_value = True
    callOrder: list[str] = []
    application.detectionThread.join.side_effect = lambda: callOrder.append(
        "joined"
    )
    application.detectionLoop.stopDetection.side_effect = lambda: (
        callOrder.append("camera-released")
    )

    application.stopDetection()

    application.stopEvent.set.assert_called_once_with()
    assert callOrder == ["joined", "camera-released"]


def test_recordDetectionShowsGestureWithoutConfidence() -> None:
    application = gestoMain.GestoApplication.__new__(
        gestoMain.GestoApplication
    )
    application.statusLock = threading.Lock()

    application.recordDetection("open-palm", 0.92)

    assert application.detectionStatus == "Detected open-palm"
