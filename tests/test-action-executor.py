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
