"""Execute mapped Gesto actions on macOS."""

import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any


ACTION_KEY = "action"
LOCK_SCREEN_ACTION = "lock-screen"
MEDIA_PLAY_PAUSE_ACTION = "media-play-pause"
OPEN_APPLICATION_ACTION = "open-app"
SCREENSHOT_ACTION = "take-screenshot"
SWITCH_TAB_NEXT_ACTION = "switch-tab-next"
SWITCH_TAB_PREVIOUS_ACTION = "switch-tab-previous"
VALUE_KEY = "value"
DEFAULT_SCREENSHOT_DIRECTORY = Path.home() / "Desktop"
SWIFT_EXECUTABLE = "/usr/bin/swift"
MEDIA_CONTROL_SCRIPT_PATH = Path(__file__).with_name("media-control.swift")
TAB_CONTROL_SCRIPT_PATH = Path(__file__).with_name("tab-control.swift")
LOCK_SCREEN_COMMAND = [
    "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/"
    "CGSession",
    "-suspend",
]


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

        if actionName == MEDIA_PLAY_PAUSE_ACTION:
            self.toggleMediaPlayback()
            return

        if actionName == SWITCH_TAB_NEXT_ACTION:
            self.switchBrowserTab(isPreviousTab=False)
            return

        if actionName == SWITCH_TAB_PREVIOUS_ACTION:
            self.switchBrowserTab(isPreviousTab=True)
            return

        if actionName == LOCK_SCREEN_ACTION:
            self.lockScreen()
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

    def toggleMediaPlayback(self) -> None:
        """Post macOS's global media play/pause event without app targeting."""
        self.commandRunner(
            [
                SWIFT_EXECUTABLE,
                str(MEDIA_CONTROL_SCRIPT_PATH),
            ],
            check=True,
        )

    def switchBrowserTab(self, isPreviousTab: bool) -> None:
        """Post native browser next or previous tab shortcut events."""
        command = [SWIFT_EXECUTABLE, str(TAB_CONTROL_SCRIPT_PATH)]
        if isPreviousTab:
            command.append("--previous")
        self.commandRunner(command, check=True)

    def lockScreen(self) -> None:
        """Lock the current macOS session without invoking a shell."""
        self.commandRunner(LOCK_SCREEN_COMMAND, check=True)
