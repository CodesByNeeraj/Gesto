"""Map detected gesture labels to configured system actions."""

from typing import Any


ACTION_KEY = "action"
GESTURES_KEY = "gestures"
GESTURE_ID_KEY = "id"
VALUE_KEY = "value"


def mapGestureToAction(
    gestureLabel: str, config: dict[str, Any]
) -> dict[str, Any] | None:
    """Return the configured action for a gesture, if one exists."""
    for gesture in config.get(GESTURES_KEY, []):
        if gesture.get(GESTURE_ID_KEY) == gestureLabel:
            return {
                ACTION_KEY: gesture.get(ACTION_KEY),
                VALUE_KEY: gesture.get(VALUE_KEY),
            }

    return None
