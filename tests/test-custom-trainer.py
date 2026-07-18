"""Tests for local custom-gesture training and persistence."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "custom-trainer.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "customTrainer", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
customTrainer = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(customTrainer)


def test_trainCustomGestureRejectsFewerThanTwentySamples(
    tmp_path: Path,
) -> None:
    samples = [createLandmarks(0.0) for _ in range(19)]

    with pytest.raises(ValueError, match="20"):
        customTrainer.trainCustomGesture("three-finger-tap", samples, tmp_path)


def test_trainCustomGestureSavesLocalModelAfterTwentySamples(
    tmp_path: Path,
) -> None:
    samples = [
        createLandmarks(sampleIndex * 0.001) for sampleIndex in range(20)
    ]

    modelPath = customTrainer.trainCustomGesture(
        "three-finger-tap", samples, tmp_path
    )

    savedModel = customTrainer.loadCustomGestureModel(modelPath)
    assert modelPath == tmp_path / "three-finger-tap.joblib"
    assert modelPath.exists()
    assert savedModel["gestureLabel"] == "three-finger-tap"


def test_findSimilarGestureReturnsExistingGestureForMatchingSamples(
    tmp_path: Path,
) -> None:
    samples = [
        createLandmarks(sampleIndex * 0.001) for sampleIndex in range(20)
    ]
    customTrainer.trainCustomGesture("three-finger-tap", samples, tmp_path)

    similarGesture = customTrainer.findSimilarGesture(samples, tmp_path)

    assert similarGesture == "three-finger-tap"


def test_detectCustomGestureReturnsSavedGestureForMatchingLandmarks(
    tmp_path: Path,
) -> None:
    samples = [
        createLandmarks(sampleIndex * 0.001) for sampleIndex in range(20)
    ]
    customTrainer.trainCustomGesture("three-finger-tap", samples, tmp_path)

    result = customTrainer.detectCustomGesture(
        createLandmarks(0.005), tmp_path
    )

    assert result == ("three-finger-tap", 1.0)


def test_listCustomGestureLabelsReturnsSavedGestureNames(
    tmp_path: Path,
) -> None:
    samples = [createLandmarks(index * 0.001) for index in range(20)]
    customTrainer.trainCustomGesture("three-finger-tap", samples, tmp_path)

    labels = customTrainer.listCustomGestureLabels(tmp_path)

    assert labels == ["three-finger-tap"]


def createLandmarks(offset: float) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(x=index * 0.01 + offset, y=index * 0.02, z=0.0)
        for index in range(21)
    ]
