"""Tests for local macOS action execution."""

import importlib.util
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "action-executor.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "actionExecutor", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
actionExecutor = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(actionExecutor)


def test_executeActionCapturesScreenshotOnDesktop(tmp_path: Path) -> None:
    commandRunner = Mock()
    executor = actionExecutor.ActionExecutor(
        commandRunner,
        tmp_path,
        Mock(return_value=datetime(2026, 7, 18, 8, 30, 0)),
    )

    executor.executeAction({"action": "take-screenshot", "value": None})

    commandRunner.assert_called_once_with(
        ["screencapture", str(tmp_path / "gesto-20260718-083000.png")],
        check=True,
    )


def test_executeActionOpensNamedApplication() -> None:
    commandRunner = Mock()
    executor = actionExecutor.ActionExecutor(commandRunner)

    executor.executeAction({"action": "open-app", "value": "Google Chrome"})

    commandRunner.assert_called_once_with(
        ["open", "-a", "Google Chrome"],
        check=True,
    )


def test_executeActionTogglesSystemMediaPlayback() -> None:
    commandRunner = Mock()
    executor = actionExecutor.ActionExecutor(commandRunner)

    executor.executeAction({"action": "media-play-pause", "value": None})

    commandRunner.assert_called_once_with(
        [
            actionExecutor.SWIFT_EXECUTABLE,
            str(actionExecutor.MEDIA_CONTROL_SCRIPT_PATH),
        ],
        check=True,
    )


def test_executeActionMovesToNextBrowserTab() -> None:
    commandRunner = Mock()
    executor = actionExecutor.ActionExecutor(commandRunner)

    executor.executeAction({"action": "switch-tab-next", "value": None})

    commandRunner.assert_called_once_with(
        [
            actionExecutor.SWIFT_EXECUTABLE,
            str(actionExecutor.TAB_CONTROL_SCRIPT_PATH),
        ],
        check=True,
    )


def test_executeActionMovesToPreviousBrowserTab() -> None:
    commandRunner = Mock()
    executor = actionExecutor.ActionExecutor(commandRunner)

    executor.executeAction({"action": "switch-tab-previous", "value": None})

    commandRunner.assert_called_once_with(
        [
            actionExecutor.SWIFT_EXECUTABLE,
            str(actionExecutor.TAB_CONTROL_SCRIPT_PATH),
            "--previous",
        ],
        check=True,
    )


def test_executeActionLocksTheScreen() -> None:
    commandRunner = Mock()
    executor = actionExecutor.ActionExecutor(commandRunner)

    executor.executeAction({"action": "lock-screen", "value": None})

    commandRunner.assert_called_once_with(
        [
            "/System/Library/CoreServices/Menu Extras/User.menu/Contents/"
            "Resources/CGSession",
            "-suspend",
        ],
        check=True,
    )
