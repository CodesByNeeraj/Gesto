"""List locally installed macOS applications for mapping suggestions."""

from pathlib import Path


APPLICATION_DIRECTORIES = (
    Path("/Applications"),
    Path("/System/Applications"),
    Path.home() / "Applications",
)


def listInstalledApplicationNames(
    applicationDirectories: tuple[Path, ...] = APPLICATION_DIRECTORIES,
) -> list[str]:
    """Return sorted names of app bundles in standard local locations."""
    applicationNames = {
        applicationPath.stem
        for directory in applicationDirectories
        if directory.exists()
        for applicationPath in directory.glob("*.app")
    }
    return sorted(applicationNames)
