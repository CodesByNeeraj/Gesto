"""Execute mapped Gesto actions on macOS."""

import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any


ACTION_KEY = "action"
OPEN_APPLICATION_ACTION = "open-app"
SCREENSHOT_ACTION = "take-screenshot"
VALUE_KEY = "value"
DEFAULT_SCREENSHOT_DIRECTORY = Path.home() / "Desktop"


class ActionExecutor:
    """Execute supported local system actions without a shell."""

    def __init__(
        self,
        commandRunner: Callable[..., Any] = subprocess.run,
        screenshotDirectory: Path = DEFAULT_SCREENSHOT_DIRECTORY,
        timestampProvider: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.commandRunner = commandRunner
        self.screenshotDirectory = screenshotDirectory
        self.timestampProvider = timestampProvider

    def executeAction(self, action: dict[str, Any]) -> None:
        """Execute one supported gesture-mapped action."""
        actionName = action.get(ACTION_KEY)
        if actionName == SCREENSHOT_ACTION:
            self.captureScreenshot()
            return

        if actionName == OPEN_APPLICATION_ACTION:
            self.openApplication(action.get(VALUE_KEY))
            return

        raise ValueError(f"Unsupported action: {actionName}")

    def captureScreenshot(self) -> None:
        """Save a unique screenshot to the configured desktop directory."""
        timestamp = self.timestampProvider().strftime("%Y%m%d-%H%M%S")
        screenshotPath = self.screenshotDirectory / f"gesto-{timestamp}.png"
        self.commandRunner(["screencapture", str(screenshotPath)], check=True)

    def openApplication(self, applicationName: Any) -> None:
        """Open the configured macOS application by name."""
        if not isinstance(applicationName, str) or not applicationName:
            raise ValueError("Open-app actions require an application name.")

        self.commandRunner(["open", "-a", applicationName], check=True)
