"""Tests for settings-window mapping behavior without a display."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "ui" / "mapping-controller.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "mappingController", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
mappingController = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(mappingController)


def test_saveMappingAddsBuiltInGestureMappingToConfig() -> None:
    config = {"gestures": [], "settings": {}}
    upsertGestureMapping = Mock()
    controller = mappingController.MainWindowController(
        config,
        upsertGestureMapping,
        Mock(),
    )

    controller.saveMapping("open-palm", "take-screenshot", None)

    expectedMapping = {
        "id": "open-palm",
        "type": "builtin",
        "action": "take-screenshot",
        "value": None,
    }
    assert config["gestures"] == [expectedMapping]
    upsertGestureMapping.assert_called_once_with(config, expectedMapping)


def test_saveMappingIgnoresValueForNonApplicationActions() -> None:
    config = {"gestures": [], "settings": {}}
    controller = mappingController.MainWindowController(
        config,
        Mock(),
        Mock(),
    )

    controller.saveMapping("thumbs-down", "take-screenshot", "Spotify")

    assert config["gestures"][0]["value"] is None
