"""Print the number of SVG files in the icons directory for each version tag."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from defusedxml.ElementTree import parse as parse_xml

REPO = Path(__file__).parent.parent
TAGS = [f"v0.{minor}.0" for minor in range(1, 14)]


@dataclass
class Version:
    """Project version."""

    count: int
    """Number of icons."""

    new_icons: list[tuple[str, str | None]] | None = None
    """New icons: (identifier, path commands)."""


def git(*args: str) -> subprocess.CompletedProcess:
    """Run Git command."""
    return subprocess.run(  # noqa: S603
        ["git", "-C", str(REPO), *args],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    )


SVG_NS = "http://www.w3.org/2000/svg"


def get_icons(tag: str) -> dict[str, str | None]:
    """Get icon identifiers and path commands for a given version tag."""
    git("checkout", tag)
    icons_dir = REPO / "icons"
    if not icons_dir.exists():
        return {}
    result = {}
    for svg_file in icons_dir.glob("*.svg"):
        root = parse_xml(svg_file).getroot()
        path_el = root.find(f"{{{SVG_NS}}}path")
        icon_id = svg_file.stem.removeprefix("roentgen_")
        result[icon_id] = path_el.get("d") if path_el is not None else None
    return result


def main() -> None:
    """Print icon counts and new icons for each version tag."""
    original = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if original == "HEAD":
        original = git("rev-parse", "HEAD").stdout.strip()

    versions: list[Version] = []

    git("stash", "--include-untracked")

    try:
        previous_ids: set[str] = set()
        for tag in TAGS:
            icons = get_icons(tag)
            new_icons = [
                (icon_id, icons[icon_id])
                for icon_id in sorted(icons.keys() - previous_ids)
            ]
            versions.append(Version(count=len(icons), new_icons=new_icons))
            previous_ids = set(icons.keys())
    finally:
        git("checkout", original)
        git("stash", "pop")

    for tag, version in zip(TAGS, versions, strict=False):
        print(  # noqa: T201
            f"{tag}: {version.count} icons, {len(version.new_icons or [])} new"
        )


if __name__ == "__main__":
    main()
