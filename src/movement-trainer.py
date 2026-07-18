"""Create direction-aware features from recorded hand landmark sequences."""

from pathlib import Path
from typing import Any

import joblib
import numpy as np


INDEX_FINGER_TIP_INDEX = 8
MIN_MOVEMENT_RECORDINGS = 3
MIN_MOVEMENT_DISTANCE = 0.05
MOVEMENT_MODEL_DIRECTORY = Path.home() / ".gesto" / "movement-models"


def createMovementFeature(landmarkSequence: list[list[Any]]) -> list[float]:
    """Describe index-finger movement from first to final recorded frame."""
    if len(landmarkSequence) < 2:
        raise ValueError("Movement gestures require at least two frames.")

    firstTip = landmarkSequence[0][INDEX_FINGER_TIP_INDEX]
    finalTip = landmarkSequence[-1][INDEX_FINGER_TIP_INDEX]
    return [
        finalTip.x - firstTip.x,
        finalTip.y - firstTip.y,
        finalTip.z - firstTip.z,
    ]


def trainMovementGesture(
    gestureLabel: str,
    recordings: list[list[list[Any]]],
    modelDirectory: Path = MOVEMENT_MODEL_DIRECTORY,
) -> Path:
    """Save local direction samples for one recorded movement gesture."""
    gestureLabel = normalizeMovementLabel(gestureLabel)
    if len(recordings) < MIN_MOVEMENT_RECORDINGS:
        raise ValueError("Movement gestures require three recordings.")

    features = np.array(
        [createMovementFeature(recording) for recording in recordings]
    )
    centroid = features.mean(axis=0)
    distances = np.linalg.norm(features - centroid, axis=1)
    distanceThreshold = max(
        float(np.quantile(distances, 0.95)),
        MIN_MOVEMENT_DISTANCE,
    )
    modelDirectory.mkdir(parents=True, exist_ok=True)
    modelPath = modelDirectory / f"{gestureLabel}.joblib"
    joblib.dump(
        {
            "gestureLabel": gestureLabel,
            "centroid": centroid,
            "distanceThreshold": distanceThreshold,
        },
        modelPath,
    )
    return modelPath


def detectMovementGesture(
    landmarkSequence: list[list[Any]],
    modelDirectory: Path = MOVEMENT_MODEL_DIRECTORY,
) -> tuple[str, float] | None:
    """Return the closest locally trained movement from a live sequence."""
    if not modelDirectory.exists() or len(landmarkSequence) < 2:
        return None

    feature = np.array(createMovementFeature(landmarkSequence))
    closestResult: tuple[str, float] | None = None
    for modelPath in modelDirectory.glob("*.joblib"):
        model = joblib.load(modelPath)
        distance = float(np.linalg.norm(feature - model["centroid"]))
        threshold = float(model["distanceThreshold"])
        if distance > threshold:
            continue
        confidenceScore = 1.0 - distance / threshold
        if closestResult is None or confidenceScore > closestResult[1]:
            closestResult = (str(model["gestureLabel"]), confidenceScore)

    return closestResult


def listMovementGestureLabels(
    modelDirectory: Path = MOVEMENT_MODEL_DIRECTORY,
) -> list[str]:
    """Return the locally trained movement labels."""
    if not modelDirectory.exists():
        return []

    modelPaths = modelDirectory.glob("*.joblib")
    return sorted(modelPath.stem for modelPath in modelPaths)


def normalizeMovementLabel(gestureLabel: str) -> str:
    """Normalize a movement name before saving its local model."""
    normalizedLabel = gestureLabel.strip()
    if not normalizedLabel:
        raise ValueError("Movement gesture names cannot be empty.")

    return normalizedLabel
