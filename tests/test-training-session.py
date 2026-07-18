"""Tests for collecting local custom-gesture training samples."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "training-session.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "trainingSession", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
trainingSession = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(trainingSession)


def test_trainCollectsTargetSamplesAndSavesGesture() -> None:
    cameraHandler = Mock()
    cameraHandler.openCamera.return_value = True
    cameraHandler.captureFrame.return_value = object()
    extractLandmarks = Mock(return_value=[object()] * 21)
    trainCustomGesture = Mock(return_value=Path("gesture.joblib"))
    session = trainingSession.TrainingSession(
        cameraHandler,
        extractLandmarks,
        trainCustomGesture,
        sampleTarget=3,
        waitForNextFrame=lambda: None,
    )

    modelPath = session.train("my-palm")

    assert modelPath == Path("gesture.joblib")
    trainCustomGesture.assert_called_once()
    assert len(trainCustomGesture.call_args.args[1]) == 3
    cameraHandler.releaseCamera.assert_called_once_with()
