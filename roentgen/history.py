"""Icon history tracking and commit preparation utilities."""

import argparse
import json
import logging
import os
import re
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from xml.etree.ElementTree import parse as parse_xml

logger: logging.Logger = logging.getLogger(__name__)

REPO = Path(__file__).parent.parent
TAGS = [f"v0.{minor}.0" for minor in range(1, 15)]
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


def stash() -> bool:
    """Stash all local changes including untracked files.

    :return: True if changes were stashed, False if there was nothing to stash
    """
    result = git("stash", "--include-untracked")
    return result.stdout.strip() != "No local changes to save"


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
        root = parse_xml(svg_file).getroot()  # noqa: S314
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
        stashed = stash()
        try:
            previous_icons: set[str] = set(get_icons(previous_tag).keys())
        finally:
            git("checkout", original)
            if stashed:
                git("stash", "pop")
        return set(get_head_icons().keys()) - previous_icons

    tag = f"v{version}"
    if tag not in TAGS:
        message = f"Unknown version tag: {tag}. Known tags: {TAGS}"
        raise ValueError(message)

    original = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if original == "HEAD":
        original = git("rev-parse", "HEAD").stdout.strip()

    stashed = stash()

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
        if stashed:
            git("stash", "pop")

    return current_icons - previous_icons


def get_versions() -> dict[str, Version]:
    """Print icon counts and new icons for each version tag."""
    original = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if original == "HEAD":
        original = git("rev-parse", "HEAD").stdout.strip()

    versions: dict[str, Version] = {}

    stashed = stash()

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
        if stashed:
            git("stash", "pop")

    head_icons = get_head_icons()
    new_head_icons = [
        (icon_id, head_icons[icon_id])
        for icon_id in sorted(head_icons.keys() - previous_ids)
    ]
    versions["HEAD"] = Version(count=len(head_icons), new_icons=new_head_icons)

    return versions


# ---------------------------------------------------------------------------
# Commit preparation
# ---------------------------------------------------------------------------

REPO_ISSUES = "https://github.com/enzet/Roentgen/issues"
MAX_LINE = 78


def get_icon_changes() -> tuple[list[str], list[str]]:
    """Return (new_icons, modified_icons) from git status in icons/."""
    result = git("status", "--short", "icons/")
    new_icons: list[str] = []
    modified_icons: list[str] = []

    for line in result.stdout.splitlines():
        xy = line[:2]
        path = line[3:]
        if not path.endswith(".svg"):
            continue
        stem = Path(path).stem
        if xy in ("A ", "??"):
            new_icons.append(stem)
        elif "M" in xy:
            modified_icons.append(stem)

    return sorted(new_icons), sorted(modified_icons)


def _parse_entries(
    lines: list[str], start: int, end: int
) -> list[tuple[str, list[str]]]:
    """Parse section entries as (icon_name, raw_lines) pairs.

    An entry begins with ``  - `name``` and may continue on subsequent lines
    (indented with 4 spaces) until the next ``  - `` line or the closing
    blank line.
    """
    entries: list[tuple[str, list[str]]] = []
    current: list[str] = []

    def flush(buf: list[str]) -> None:
        if not buf:
            return
        m = re.match(r"  - `([^`]+)`", buf[0])
        entries.append((m.group(1) if m else "", buf))

    for i in range(start + 1, end):
        line = lines[i]
        if line.startswith("  - "):
            flush(current)
            current = [line]
        else:
            current.append(line)

    flush(current)
    return entries


def _set_terminator(lines: list[str], char: str) -> list[str]:
    """Replace the trailing comma or period on the last non-empty line."""
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].rstrip("\n")
        if stripped.endswith((",", ".")):
            lines[i] = stripped[:-1] + char + "\n"
            break
    return lines


def _format_add_entry(name: str, issue: int | None) -> list[str]:
    """Build raw lines for a new 'Add icons' entry (comma-terminated)."""
    if issue is None:
        return [f"  - `{name}`,\n"]
    url = f"{REPO_ISSUES}/{issue}"
    inline = f"  - `{name}` ([#{issue}]({url})),"
    if len(inline) <= MAX_LINE:
        return [inline + "\n"]
    return [f"  - `{name}`\n", f"    ([#{issue}]({url})),\n"]


def _format_redraw_entry(name: str) -> list[str]:
    """Build raw lines for a 'Redraw icons' entry (comma-terminated)."""
    return [f"  - `{name}`,\n"]


def _insert_into_section(
    lines: list[str],
    section_header: str,
    new_names: list[str],
    make_entry: Callable[[str], list[str]],
) -> list[str]:
    """Insert *new_names* into a sorted CHANGELOG section."""
    header_line = section_header + "\n"
    try:
        start = lines.index(header_line)
    except ValueError:
        return lines

    end = start + 1
    while end < len(lines) and lines[end] != "\n":
        end += 1

    existing = _parse_entries(lines, start, end)
    existing_names = {name for name, _ in existing}

    all_entries = list(existing) + [
        (name, make_entry(name))
        for name in new_names
        if name not in existing_names
    ]
    all_entries.sort(key=lambda t: t[0])

    rebuilt: list[str] = []
    for i, (_, raw_lines) in enumerate(all_entries):
        entry_lines = list(raw_lines)
        _set_terminator(entry_lines, "." if i == len(all_entries) - 1 else ",")
        rebuilt.extend(entry_lines)

    return lines[: start + 1] + rebuilt + lines[end:]


def _build_commit_message(
    new_icons: list[str], modified_icons: list[str], issue: int | None
) -> str:
    """Generate a one-line commit message."""
    prefix = f"[#{issue}] " if issue is not None else ""
    parts: list[str] = []

    if new_icons:
        if len(new_icons) == 1:
            parts.append(f"Add {new_icons[0].replace('_', ' ')} icon")
        else:
            parts.append(f"Add {len(new_icons)} icons")

    if modified_icons:
        if len(modified_icons) == 1:
            parts.append(f"redraw {modified_icons[0].replace('_', ' ')} icon")
        else:
            parts.append("redraw other icons")

    if not parts:
        return f"{prefix}Update icons"

    msg = "; ".join(parts)
    return prefix + msg[0].upper() + msg[1:]


def prepare_commit(*, issue: int | None = None, dry_run: bool = False) -> None:
    """Update CHANGELOG.md and open a commit message in $EDITOR."""
    new_icons, modified_icons = get_icon_changes()

    if not new_icons and not modified_icons:
        logger.info("No new or modified icons found in icons/.")
        return

    if new_icons:
        logger.info("New icons:      %s", ", ".join(new_icons))
    if modified_icons:
        logger.info("Modified icons: %s", ", ".join(modified_icons))

    changelog = REPO / "CHANGELOG.md"
    lines = changelog.read_text().splitlines(keepends=True)

    if new_icons:
        lines = _insert_into_section(
            lines,
            "Add icons:",
            new_icons,
            lambda name: _format_add_entry(name, issue),
        )
    if modified_icons:
        lines = _insert_into_section(
            lines, "Redraw icons:", modified_icons, _format_redraw_entry
        )

    if dry_run:
        logger.info("--- CHANGELOG.md (Unreleased section) ---")
        in_unreleased = False
        for line in lines:
            if line.startswith("## Unreleased"):
                in_unreleased = True
            elif line.startswith("## ") and in_unreleased:
                break
            if in_unreleased:
                logger.info("%s", line.rstrip())
    else:
        changelog.write_text("".join(lines))
        logger.info("Updated %s", changelog.relative_to(REPO))

    message = _build_commit_message(new_icons, modified_icons, issue)
    comments = []
    if new_icons:
        comments.append("# New icons: " + ", ".join(new_icons))
    if modified_icons:
        comments.append("# Modified icons: " + ", ".join(modified_icons))
    comments.append("#")
    comments.append("# Lines starting with '#' will be ignored.")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", prefix="commit_msg_", delete=False
    ) as tmp:
        tmp.write(message + "\n\n" + "\n".join(comments) + "\n")
        tmp_path = tmp.name

    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    subprocess.run([editor, tmp_path], check=False)  # noqa: S603

    raw = Path(tmp_path).read_text()
    Path(tmp_path).unlink()
    final_message = "\n".join(
        line for line in raw.splitlines() if not line.startswith("#")
    ).strip()

    logger.info("Commit message:\n  %s", final_message)

    if not dry_run:
        icon_files = [f"icons/{n}.svg" for n in new_icons + modified_icons]
        logger.info("To commit:")
        logger.info("  git add CHANGELOG.md %s", " ".join(icon_files))
        logger.info("  git commit -m '%s'", final_message)


def main() -> None:
    """Entry point for commit preparation CLI."""
    parser = argparse.ArgumentParser(
        description="Prepare a commit for new and modified icons."
    )
    parser.add_argument(
        "--issue",
        "-i",
        type=int,
        default=None,
        help="GitHub issue number (optional)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would change without writing files",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    prepare_commit(issue=args.issue, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
