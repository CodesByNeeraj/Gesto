"""Tests for local movement-gesture feature extraction."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "movement-trainer.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "movementTrainer", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
movementTrainer = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(movementTrainer)


def test_createMovementFeatureCapturesIndexFingerDirection() -> None:
    sequence = [
        createLandmarks(0.2),
        createLandmarks(0.5),
        createLandmarks(0.8),
    ]

    feature = movementTrainer.createMovementFeature(sequence)

    assert feature[0] > 0


def test_trainMovementGestureSavesThreeRecordings(tmp_path: Path) -> None:
    recordings = [
        [createLandmarks(0.2), createLandmarks(0.8)] for _ in range(3)
    ]

    modelPath = movementTrainer.trainMovementGesture(
        "swipe-right",
        recordings,
        tmp_path,
    )

    assert modelPath.exists()


def test_detectMovementGestureMatchesTrainedDirection(tmp_path: Path) -> None:
    recordings = [
        [createLandmarks(0.2), createLandmarks(0.8)] for _ in range(3)
    ]
    movementTrainer.trainMovementGesture("swipe-right", recordings, tmp_path)

    result = movementTrainer.detectMovementGesture(recordings[0], tmp_path)

    assert result == ("swipe-right", 1.0)


def createLandmarks(indexTipX: float) -> list[SimpleNamespace]:
    landmarks = [SimpleNamespace(x=0.5, y=0.5, z=0.0) for _ in range(21)]
    landmarks[8] = SimpleNamespace(x=indexTipX, y=0.5, z=0.0)
    return landmarks
