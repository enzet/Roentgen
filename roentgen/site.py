"""Generate site files from templates with icon data."""

from __future__ import annotations

import json
import logging
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from roentgen.icon import Icon, get_icons

logger: logging.Logger = logging.getLogger(__name__)


def flatten_config(
    config: dict[str, Any], prefix: str = ""
) -> list[tuple[str, dict[str, Any]]]:
    """Flatten nested config structure.

    :returns: a list of (identifier, metadata) tuples
    """
    result: list[tuple[str, dict[str, Any]]] = []

    for key, value in config.items():
        current_prefix = f"{prefix}_{key}" if prefix else key

        if isinstance(value, dict):
            if key.startswith("__"):  # This is a category.
                result.extend(flatten_config(value, current_prefix))
            else:  # This is an icon entry.
                result.append((key, value))

    return result


def extract_path_from_svg(svg_file: Path) -> list[str]:
    """Extract path data from SVG file."""

    tree: ET.ElementTree = ET.parse(svg_file)  # noqa: S314
    root: ET.Element = tree.getroot()

    result: list[str] = []

    # Find all path elements.
    paths: list[ET.Element] = root.findall(
        ".//{http://www.w3.org/2000/svg}path"
    )
    if not paths:
        return []

    for path in paths:
        if d := path.get("d"):
            result.append(d)  # noqa: PERF401

    return result


def generate_icon_name(file_path: Path) -> str:
    """Generate a human-readable name from filename."""

    name: str = file_path.stem
    name = " ".join(word.capitalize() for word in name.split("_"))

    # Handle special cases like "___" which are used as separators.
    return re.sub(r"\s+", " ", name)


def generate_icon_identifier(file_path: Path) -> str:
    """Generate an identifier from filename."""
    return file_path.stem


def generate_icon_grid_item(identifier: str, path_data: list[str]) -> str:
    """Generate HTML for a single icon grid item."""
    result = (
        f'<div class="icon-item" data-name="{identifier}">'
        '<svg viewBox="0 0 16 16" width="40" height="40">'
    )
    for path in path_data:
        assert len(path) > 1
        result += f'<path d="{path}"/>'
    result += "</svg></div>"
    return result


def capitalize(name: str) -> str:
    """Capitalize the first letters of the name.

    Capitalize the first letter of each word, but skip some words as "and",
    "of", "the", etc.

    E.g. "apartments 1 story" -> "Apartments 1 Story".
    """
    words: list[str] = name.split(" ")
    skip_words: set[str] = {
        "and",
        "at",
        "for",
        "from",
        "in",
        "of",
        "on",
        "or",
        "px",
        "the",
        "to",
        "with",
    }
    capitalized: list[str] = []
    for word in words:
        if not word:
            continue

        if "-" in word:
            parts: list[str] = word.split("-")
            capitalized.append("-".join(part.capitalize() for part in parts))
            continue

        if word.lower() in skip_words and capitalized:
            capitalized.append(word.lower())
        elif word.isdigit() or not (word.isalpha()) or word.lower() != word:
            capitalized.append(word)
        else:
            capitalized.append(word.capitalize())

    return " ".join(capitalized)


def process_icons(
    icons_dirs: list[Path], config_path: Path
) -> tuple[dict[str, dict], str]:
    """Process all SVG files.

    Process files in the icons directory according to config order.
    """
    icons_data: dict[str, dict] = {}
    icon_grid_items: list[str] = []

    # Load and flatten config.
    icons: list[Icon] = get_icons(config_path)

    # Process icons in config order.
    for icon in icons:
        if icon.is_sketch():
            continue

        found: bool = False
        for icons_dir in icons_dirs:
            svg_file = icons_dir / f"{icon.icon_id}.svg"
            if svg_file.exists():
                found = True
                break

        if not found:
            continue

        path_data: list[str] = extract_path_from_svg(svg_file)
        if not path_data:
            continue

        # Use metadata from config.
        icons_data[icon.icon_id] = {
            "name": icon.name,
            "capitalized_name": capitalize(icon.name),
            "identifier": icon.icon_id,
            "tags": list(icon.keywords),
            "paths": path_data,
        }
        icons_data[icon.icon_id]["unicode"] = list(icon.unicode)

        icon_grid_items.append(generate_icon_grid_item(icon.icon_id, path_data))

    return icons_data, "\n".join(icon_grid_items)


def generate_site_files(
    icons_data: dict[str, dict],
    icon_grid_html: str,
    template_dir: Path,
    site_path: Path,
    version: str,
    zip_path: Path,
) -> None:
    """Generate site files from templates with icon data."""

    icons_js: str = json.dumps(icons_data, indent=4)

    with (template_dir / "code.template.js").open() as input_file:
        code_template: str = input_file.read()
        code_template = code_template.replace("%ICONS_DATA%", icons_js)
    with (site_path / "roentgen.js").open("w") as output_file:
        output_file.write(code_template)

    with (site_path / "index.html").open() as input_file:
        content: str = input_file.read()
        content = content.replace("%ROENTGEN_ICON_GRID%", icon_grid_html)
        content = content.replace("%ROENTGEN_VERSION%", version)
        content = content.replace("%ICONS_COUNT%", str(len(icons_data)))
        content = content.replace(
            "%ICONS_FILE_SIZE%",
            str(zip_path.stat().st_size // 1024),
        )
    with (site_path / "index.html").open("w") as output_file:
        output_file.write(content)

    shutil.copy(template_dir / "style.css", site_path / "roentgen.css")


def main(site_path: Path) -> None:
    """Generate site files from templates with icon data."""

    icons_dirs: list[Path] = [
        Path("icons"),
        Path("icons_sketches"),
    ]
    template_dir: Path = Path("data")
    config_path: Path = Path("data/config.json")
    version_path: Path = Path("VERSION")

    with version_path.open() as version_file:
        version: str = version_file.read().strip()

    zip_path: Path = Path("out") / f"roentgen-{version}.zip"

    # Process icons.
    icons_data, icon_grid_html = process_icons(icons_dirs, config_path)

    # Generate site files.
    generate_site_files(
        icons_data, icon_grid_html, template_dir, site_path, version, zip_path
    )
    logger.info("Generated site files in %s.", site_path)
