"""Tests for mapping detected gestures to configured actions."""

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "action-mapper.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "actionMapper", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
actionMapper = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(actionMapper)


def test_mapGestureToActionReturnsConfiguredActionForDetectedGesture() -> None:
    config = {
        "gestures": [
            {
                "id": "thumbs-up",
                "type": "builtin",
                "action": "open-app",
                "value": "Google Chrome",
            }
        ]
    }

    mappedAction = actionMapper.mapGestureToAction("thumbs-up", config)

    assert mappedAction == {
        "action": "open-app",
        "value": "Google Chrome",
    }
