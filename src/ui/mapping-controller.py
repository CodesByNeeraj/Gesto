"""Toolkit-independent state management for gesture mappings."""

from collections.abc import Callable
from typing import Any


GESTURES_KEY = "gestures"
OPEN_APPLICATION_ACTION = "open-app"


class MainWindowController:
    """Manage settings-window mapping state independently of the UI toolkit."""

    def __init__(
        self,
        config: dict[str, Any],
        upsertGestureMapping: Callable[[dict[str, Any], dict[str, Any]], None],
        deleteGestureMapping: Callable[[dict[str, Any], str], None],
    ) -> None:
        self.config = config
        self.upsertGestureMapping = upsertGestureMapping
        self.deleteGestureMapping = deleteGestureMapping

    def saveMapping(
        self, gestureLabel: str, actionName: str, actionValue: str | None
    ) -> None:
        """Add or update a gesture mapping in local configuration."""
        actionValue = (
            actionValue if actionName == OPEN_APPLICATION_ACTION else None
        )
        mapping = {
            "id": gestureLabel,
            "type": self.getGestureType(gestureLabel),
            "action": actionName,
            "value": actionValue,
        }
        gestures = self.config[GESTURES_KEY]
        for existingMapping in gestures:
            if existingMapping["id"] == gestureLabel:
                if existingMapping != mapping:
                    raise ValueError(f"{gestureLabel} is already mapped.")
                return

        gestures.append(mapping)
        self.upsertGestureMapping(self.config, mapping)

    def removeMapping(self, gestureLabel: str) -> None:
        """Remove a mapping from local configuration."""
        self.deleteGestureMapping(self.config, gestureLabel)

    def getGestureType(self, gestureLabel: str) -> str:
        """Return the only supported gesture source: local training."""
        return "custom"
