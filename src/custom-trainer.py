"""Train and persist local classifiers for user-defined hand gestures."""

from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.neighbors import KNeighborsClassifier


MODEL_DIRECTORY = Path.home() / ".gesto" / "models"
MIN_CUSTOM_GESTURE_SAMPLES = 20
DEFAULT_NEIGHBORS = 3
LANDMARK_COUNT = 21
MIN_DISTANCE_THRESHOLD = 0.05


def trainCustomGesture(
    gestureLabel: str,
    landmarkSamples: list[list[Any]],
    modelDirectory: Path = MODEL_DIRECTORY,
) -> Path:
    """Train and save one custom gesture from twenty or more local samples."""
    if len(landmarkSamples) < MIN_CUSTOM_GESTURE_SAMPLES:
        raise ValueError(
            "Custom gestures require at least "
            f"{MIN_CUSTOM_GESTURE_SAMPLES} samples."
        )

    normalizedSamples = [
        normalizeLandmarks(landmarks) for landmarks in landmarkSamples
    ]
    classifier = KNeighborsClassifier(
        n_neighbors=min(DEFAULT_NEIGHBORS, len(normalizedSamples))
    )
    classifier.fit(normalizedSamples, [gestureLabel] * len(normalizedSamples))

    sampleMatrix = np.array(normalizedSamples)
    centroid = sampleMatrix.mean(axis=0)
    distances = np.linalg.norm(sampleMatrix - centroid, axis=1)
    distanceThreshold = max(
        float(np.quantile(distances, 0.95)), MIN_DISTANCE_THRESHOLD
    )
    savedModel = {
        "classifier": classifier,
        "centroid": centroid,
        "distanceThreshold": distanceThreshold,
        "gestureLabel": gestureLabel,
    }

    modelDirectory.mkdir(parents=True, exist_ok=True)
    modelPath = modelDirectory / f"{gestureLabel}.joblib"
    joblib.dump(savedModel, modelPath)
    return modelPath


def loadCustomGestureModel(modelPath: Path) -> dict[str, Any]:
    """Load a model that was created in Gesto's local model directory."""
    return joblib.load(modelPath)


def normalizeLandmarks(landmarks: list[Any]) -> list[float]:
    """Create a translation- and scale-invariant landmark feature vector."""
    if len(landmarks) != LANDMARK_COUNT:
        raise ValueError(f"Expected {LANDMARK_COUNT} hand landmarks.")

    wrist = landmarks[0]
    translatedPoints = [
        (point.x - wrist.x, point.y - wrist.y, point.z - wrist.z)
        for point in landmarks
    ]
    scale = max(
        max(np.linalg.norm(point) for point in translatedPoints),
        MIN_DISTANCE_THRESHOLD,
    )
    return [
        coordinate / scale
        for point in translatedPoints
        for coordinate in point
    ]
