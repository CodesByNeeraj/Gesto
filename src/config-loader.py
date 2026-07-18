"""Read and write Gesto's local gesture configuration."""

import json
from pathlib import Path
from typing import Any


CONFIG_FILE_PATH = Path.home() / ".gesto" / "config.json"
DEFAULT_CONFIDENCE_THRESHOLD = 0.80
DEFAULT_COOLDOWN_SECONDS = 1
GESTURES_KEY = "gestures"
GESTURE_ID_KEY = "id"


def createDefaultConfig() -> dict[str, Any]:
    """Return a new default configuration for a first-time user."""
    return {
        "gestures": [],
        "settings": {
            "confidenceThreshold": DEFAULT_CONFIDENCE_THRESHOLD,
            "cooldownSeconds": DEFAULT_COOLDOWN_SECONDS,
        },
    }


def loadConfig(configPath: Path = CONFIG_FILE_PATH) -> dict[str, Any]:
    """Load the local configuration, creating the default on first launch."""
    if configPath.exists():
        with configPath.open(encoding="utf-8") as configFile:
            return json.load(configFile)

    config = createDefaultConfig()
    saveConfig(config, configPath)
    return config


def saveConfig(
    config: dict[str, Any], configPath: Path = CONFIG_FILE_PATH
) -> None:
    """Persist configuration as readable JSON in Gesto's local folder."""
    configPath.parent.mkdir(parents=True, exist_ok=True)
    with configPath.open("w", encoding="utf-8") as configFile:
        json.dump(config, configFile, indent=2)
        configFile.write("\n")


def upsertGestureMapping(
    config: dict[str, Any],
    mapping: dict[str, Any],
    configPath: Path = CONFIG_FILE_PATH,
) -> None:
    """Add or replace one gesture mapping and save it locally."""
    gestures = config[GESTURES_KEY]
    for index, existingMapping in enumerate(gestures):
        if existingMapping[GESTURE_ID_KEY] == mapping[GESTURE_ID_KEY]:
            gestures[index] = mapping
            saveConfig(config, configPath)
            return

    gestures.append(mapping)
    saveConfig(config, configPath)


def deleteGestureMapping(
    config: dict[str, Any],
    gestureLabel: str,
    configPath: Path = CONFIG_FILE_PATH,
) -> None:
    """Delete one gesture mapping and save the updated configuration."""
    config[GESTURES_KEY] = [
        mapping
        for mapping in config[GESTURES_KEY]
        if mapping[GESTURE_ID_KEY] != gestureLabel
    ]
    saveConfig(config, configPath)
