"""Tests for local installed-application suggestions."""

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "application-catalog.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "applicationCatalog", MODULE_PATH
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
applicationCatalog = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(applicationCatalog)


def test_listInstalledApplicationNamesReturnsSortedAppBundleNames(
    tmp_path: Path,
) -> None:
    (tmp_path / "Safari.app").mkdir()
    (tmp_path / "Google Chrome.app").mkdir()
    (tmp_path / "README.txt").write_text("not an application")

    names = applicationCatalog.listInstalledApplicationNames((tmp_path,))

    assert names == ["Google Chrome", "Safari"]
