"""Print the number of SVG files in the icons directory for each version tag."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from defusedxml.ElementTree import parse as parse_xml

REPO = Path(__file__).parent.parent
TAGS = [f"v0.{minor}.0" for minor in range(1, 14)]
CACHE_DIR = REPO / ".cache" / "history"


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
    cache_file = CACHE_DIR / f"{tag}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    git("checkout", tag)
    icons = get_head_icons()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(icons), encoding="utf-8")
    return icons


def get_head_icons() -> dict[str, str | None]:
    """Get icon identifiers and path commands from the current working tree."""
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


def get_new_icon_ids(version: str) -> set[str]:
    """Get icon identifiers that are new in the given version.

    :param version: version string like "0.13.0" (tag "v0.13.0"), or "HEAD"
    :return: set of icon identifiers new in that version
    """
    if version == "HEAD":
        previous_tag = TAGS[-1]
        original = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if original == "HEAD":
            original = git("rev-parse", "HEAD").stdout.strip()
        git("stash", "--include-untracked")
        try:
            previous_icons: set[str] = set(get_icons(previous_tag).keys())
        finally:
            git("checkout", original)
            git("stash", "pop")
        return set(get_head_icons().keys()) - previous_icons

    tag = f"v{version}"
    if tag not in TAGS:
        message = f"Unknown version tag: {tag}. Known tags: {TAGS}"
        raise ValueError(message)

    original = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if original == "HEAD":
        original = git("rev-parse", "HEAD").stdout.strip()

    git("stash", "--include-untracked")

    try:
        tag_index = TAGS.index(tag)
        previous_icons = (
            set(get_icons(TAGS[tag_index - 1]).keys())
            if tag_index > 0
            else set()
        )
        current_icons: set[str] = set(get_icons(tag).keys())
    finally:
        git("checkout", original)
        git("stash", "pop")

    return current_icons - previous_icons


def get_versions() -> dict[str, Version]:
    """Print icon counts and new icons for each version tag."""
    original = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if original == "HEAD":
        original = git("rev-parse", "HEAD").stdout.strip()

    versions: dict[str, Version] = {}

    git("stash", "--include-untracked")

    try:
        previous_ids: set[str] = set()
        for tag in TAGS:
            icons = get_icons(tag)
            new_icons = [
                (icon_id, icons[icon_id])
                for icon_id in sorted(icons.keys() - previous_ids)
            ]
            versions[tag] = Version(count=len(icons), new_icons=new_icons)
            previous_ids = set(icons.keys())
    finally:
        git("checkout", original)
        git("stash", "pop")

    head_icons = get_head_icons()
    new_head_icons = [
        (icon_id, head_icons[icon_id])
        for icon_id in sorted(head_icons.keys() - previous_ids)
    ]
    versions["HEAD"] = Version(count=len(head_icons), new_icons=new_head_icons)

    return versions
