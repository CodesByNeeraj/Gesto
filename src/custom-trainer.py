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
SIMILARITY_DISTANCE_MULTIPLIER = 2.0


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
    centroid = calculateCentroid(normalizedSamples)
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


def listCustomGestureLabels(
    modelDirectory: Path = MODEL_DIRECTORY,
) -> list[str]:
    """Return locally trained gesture labels in a stable order."""
    if not modelDirectory.exists():
        return []

    modelPaths = modelDirectory.glob("*.joblib")
    return sorted(modelPath.stem for modelPath in modelPaths)


def findSimilarGesture(
    landmarkSamples: list[list[Any]],
    modelDirectory: Path = MODEL_DIRECTORY,
) -> str | None:
    """Return an existing label when new samples are too similar to it."""
    if not landmarkSamples or not modelDirectory.exists():
        return None

    candidateCentroid = calculateCentroid(
        [normalizeLandmarks(landmarks) for landmarks in landmarkSamples]
    )
    for modelPath in modelDirectory.glob("*.joblib"):
        savedModel = loadCustomGestureModel(modelPath)
        centroidDistance = float(
            np.linalg.norm(candidateCentroid - savedModel["centroid"])
        )
        similarityThreshold = (
            savedModel["distanceThreshold"] * SIMILARITY_DISTANCE_MULTIPLIER
        )
        if centroidDistance <= similarityThreshold:
            return str(savedModel["gestureLabel"])

    return None


def detectCustomGesture(
    landmarks: list[Any],
    modelDirectory: Path = MODEL_DIRECTORY,
) -> tuple[str, float] | None:
    """Return the nearest saved custom gesture within its distance limit."""
    if not modelDirectory.exists():
        return None

    normalizedLandmarks = normalizeLandmarks(landmarks)
    closestResult: tuple[str, float] | None = None
    for modelPath in modelDirectory.glob("*.joblib"):
        savedModel = loadCustomGestureModel(modelPath)
        distance = float(
            savedModel["classifier"].kneighbors(
                [normalizedLandmarks], n_neighbors=1
            )[0][0][0]
        )
        threshold = float(savedModel["distanceThreshold"])
        if distance > threshold:
            continue

        confidenceScore = 1.0 - (distance / threshold)
        if closestResult is None or confidenceScore > closestResult[1]:
            closestResult = (str(savedModel["gestureLabel"]), confidenceScore)

    return closestResult


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


def calculateCentroid(normalizedSamples: list[list[float]]) -> np.ndarray:
    """Return the average feature vector for a recorded gesture."""
    return np.array(normalizedSamples).mean(axis=0)
