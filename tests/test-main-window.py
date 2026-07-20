"""Tests for settings-window mapping behavior without a display."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest


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


def test_saveMappingRejectsConflictingActionForExistingGesture() -> None:
    existingMapping = {
        "id": "my-open-palm",
        "type": "custom",
        "action": "take-screenshot",
        "value": None,
    }
    config = {"gestures": [existingMapping], "settings": {}}
    controller = mappingController.MainWindowController(
        config,
        Mock(),
        Mock(),
    )

    with pytest.raises(ValueError, match="already mapped"):
        controller.saveMapping("my-open-palm", "lock-screen", None)

    assert config["gestures"] == [existingMapping]


def test_mainWindowProvidesRetrainControlForSelectedGesture() -> None:
    source = WINDOW_PATH.read_text()

    assert 'text="Retrain"' in source
    assert "command=self.retrainSelectedGesture" in source
    assert "self.retrainButton.configure(state=\"disabled\")" in source


def test_mainWindowDisablesDetectionAndTrainingDuringSampleCapture() -> None:
    source = WINDOW_PATH.read_text()

    assert "self.isTraining = False" in source
    assert "self.setTrainingState(True)" in source
    assert "self.setTrainingState(False)" in source
    assert 'state = "disabled" if isTraining else "normal"' in source
    assert "self.toggleButton.configure(state=state)" in source
    assert "self.trainButton.configure(state=state)" in source
    assert "self.retrainButton.configure(state=state)" in source


def test_mainWindowProvidesInstalledApplicationSuggestions() -> None:
    source = WINDOW_PATH.read_text()

    assert "CTkComboBox" in source
    assert "Choose installed app or type a name" in source
    assert "placeholder_text" not in source
    assert "valueEntry.delete" not in source
    assert "Select from the dropdown or type in the box." in source
    assert "if isApplicationAction:" in source


def test_mainWindowExplainsConflictingGestureMapping() -> None:
    source = WINDOW_PATH.read_text()

    assert "Remove the existing mapping first." in source


def test_mainWindowProvidesRoomForTrainingGuidance() -> None:
    source = WINDOW_PATH.read_text()

    assert 'self.geometry("860x620")' in source
    assert "self.minsize(760, 560)" in source
    assert "TRAINING_HINT_WRAP_LENGTH = 360" in source
    assert "wraplength=TRAINING_HINT_WRAP_LENGTH" in source


def test_mainWindowWrapsAndScrollsMappingRows() -> None:
    source = WINDOW_PATH.read_text()

    assert "MAPPING_TEXT_WRAP_LENGTH = 200" in source
    assert "wraplength=MAPPING_TEXT_WRAP_LENGTH" in source
    assert "width=MAPPING_TEXT_WRAP_LENGTH" in source
    assert "height=0" in source
    assert "self.bindMappingScroll(rowFrame)" in source
    assert (
        "self.bindMappingScroll(self.mappingsFrame._parent_canvas)"
        in source
    )
    assert "self.bindMappingScroll(self.mappingsFrame._parent_frame)" in source
    assert (
        "self.bind_all(\"<MouseWheel>\", self.handleMappingScroll, add=\"+\")"
        in source
    )


def test_mainWindowProvidesTrainingGuideTab() -> None:
    source = WINDOW_PATH.read_text()

    assert 'text="Gestures"' in source
    assert 'text="Guide"' in source
    assert "command=self.showGestures" in source
    assert "command=self.showGuide" in source
    assert "CTkTabview" not in source
    assert "40 valid snapshots" in source
    assert "replaces the old model" in source
    assert "small, realistic variations" in source
    assert "Your gestures, your rules." in source
    assert "100% Privacy" in source
    assert "Gesto neither collects, nor uploads" in source
