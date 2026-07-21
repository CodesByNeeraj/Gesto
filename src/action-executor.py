"""Execute mapped Gesto actions on macOS."""

import ctypes
import platform
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
LOCK_SCREEN_SCRIPT_PATH = Path(__file__).with_name("lock-screen.swift")
RIGHT_ARROW_KEY = 124
LEFT_ARROW_KEY = 123
COMMAND_KEY = 55
OPTION_KEY = 58
COMMAND_FLAG = 1 << 20
OPTION_FLAG = 1 << 19
HID_EVENT_TAP = 0


def postBrowserTabShortcut(isPreviousTab: bool) -> None:
    """Post Chrome's Command-Option arrow shortcut from this process."""
    if platform.system() != "Darwin":
        raise OSError("Browser tab shortcuts require macOS.")

    coreGraphics = ctypes.CDLL(
        "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
    )
    createEvent = coreGraphics.CGEventCreateKeyboardEvent
    createEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint16, ctypes.c_bool]
    createEvent.restype = ctypes.c_void_p
    setFlags = coreGraphics.CGEventSetFlags
    setFlags.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
    postEvent = coreGraphics.CGEventPost
    postEvent.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

    def postKey(keyCode: int, isDown: bool, flags: int = 0) -> None:
        event = createEvent(None, keyCode, isDown)
        if not event:
            raise OSError("macOS could not create a keyboard event.")
        setFlags(event, flags)
        postEvent(HID_EVENT_TAP, event)

    tabKey = LEFT_ARROW_KEY if isPreviousTab else RIGHT_ARROW_KEY
    navigationFlags = COMMAND_FLAG | OPTION_FLAG
    postKey(COMMAND_KEY, True)
    postKey(OPTION_KEY, True)
    postKey(tabKey, True, navigationFlags)
    postKey(tabKey, False, navigationFlags)
    postKey(OPTION_KEY, False)
    postKey(COMMAND_KEY, False)


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
        postBrowserTabShortcut(isPreviousTab)

    def lockScreen(self) -> None:
        """Post macOS's native Control-Command-Q lock shortcut."""
        self.commandRunner(
            [
                SWIFT_EXECUTABLE,
                str(LOCK_SCREEN_SCRIPT_PATH),
            ],
            check=True,
        )
