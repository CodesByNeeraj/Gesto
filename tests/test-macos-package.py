"""Tests for the macOS application bundle configuration."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
BUILD_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "build-macos-app.sh"


def test_macosBuildScriptCreatesBrandedGestoApplication() -> None:
    script = BUILD_SCRIPT_PATH.read_text()

    assert "--name Gesto" in script
    assert "--icon \"${PROJECT_DIRECTORY}/assets/icons/Gesto.icns\"" in script
    assert "--osx-bundle-identifier com.gesto.app" in script
