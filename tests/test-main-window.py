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
WINDOW_PATH = PROJECT_ROOT / "src" / "ui" / "main-window.py"


def test_saveMappingAddsTrainedGestureMappingToConfig() -> None:
    config = {"gestures": [], "settings": {}}
    upsertGestureMapping = Mock()
    controller = mappingController.MainWindowController(
        config,
        upsertGestureMapping,
        Mock(),
    )

    controller.saveMapping("my-open-palm", "take-screenshot", None)

    expectedMapping = {
        "id": "my-open-palm",
        "type": "custom",
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


def test_mainWindowProvidesRetrainControlForSelectedGesture() -> None:
    source = WINDOW_PATH.read_text()

    assert 'text="Retrain"' in source
    assert "command=self.retrainSelectedGesture" in source
    assert "self.retrainButton.configure(state=\"disabled\")" in source


def test_mainWindowProvidesInstalledApplicationSuggestions() -> None:
    source = WINDOW_PATH.read_text()

    assert "CTkComboBox" in source
    assert "Choose installed app or type a name" in source
    assert "placeholder_text" not in source
    assert "valueEntry.delete" not in source
    assert "Select from the dropdown or type in the box." in source
