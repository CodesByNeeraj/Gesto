"""Tests for local Gesto configuration persistence."""

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "config-loader.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "configLoader", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
configLoader = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(configLoader)


def test_loadConfigCreatesDefaultConfigWhenFileIsMissing(
    tmp_path: Path,
) -> None:
    configPath = tmp_path / "config.json"

    config = configLoader.loadConfig(configPath)

    assert config == {
        "gestures": [],
        "settings": {
            "confidenceThreshold": 0.80,
            "cooldownSeconds": 5,
        },
    }
    assert configPath.exists()


def test_upsertGestureMappingSavesNewMappingToLocalConfig(
    tmp_path: Path,
) -> None:
    configPath = tmp_path / "config.json"
    config = configLoader.loadConfig(configPath)
    mapping = {
        "id": "open-palm",
        "type": "builtin",
        "action": "take-screenshot",
        "value": None,
    }

    configLoader.upsertGestureMapping(config, mapping, configPath)

    savedConfig = configLoader.loadConfig(configPath)
    assert savedConfig["gestures"] == [mapping]


def test_deleteGestureMappingRemovesMappingFromLocalConfig(
    tmp_path: Path,
) -> None:
    configPath = tmp_path / "config.json"
    config = {
        "gestures": [
            {
                "id": "open-palm",
                "type": "builtin",
                "action": "take-screenshot",
                "value": None,
            }
        ],
        "settings": {
            "confidenceThreshold": 0.80,
            "cooldownSeconds": 5,
        },
    }
    configLoader.saveConfig(config, configPath)

    configLoader.deleteGestureMapping(config, "open-palm", configPath)

    savedConfig = configLoader.loadConfig(configPath)
    assert savedConfig["gestures"] == []
