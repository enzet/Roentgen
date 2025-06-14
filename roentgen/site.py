"""Generate site files from templates with icon data."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_path_from_svg(svg_file: Path) -> str | None:
    """Extract path data from SVG file."""

    tree: ET.ElementTree = ET.parse(svg_file)  # noqa: S314
    root: ET.Element = tree.getroot()

    # Find the first path element.
    path: ET.Element | None = root.find(".//{http://www.w3.org/2000/svg}path")
    if path is not None:
        return path.get("d")

    return None


def generate_icon_name(file_path: Path) -> str:
    """Generate a human-readable name from filename."""

    name: str = file_path.stem
    name = " ".join(word.capitalize() for word in name.split("_"))

    # Handle special cases like "___" which are used as separators.
    return re.sub(r"\s+", " ", name)


def generate_icon_identifier(file_path: Path) -> str:
    """Generate an identifier from filename."""
    return file_path.stem


def generate_icon_tags(file_path: Path) -> list[str]:
    """Generate tags based on filename."""
    name: str = file_path.stem
    words: list[str] = [word for word in name.split("_") if word]
    return sorted(set(words))


def generate_icon_description(name: str, tags: list[str]) -> str:
    """Generate a simple description based on name and tags."""
    return (
        f"A {name.lower()} icon, useful for {', '.join(tags)} related "
        "interfaces."
    )


def generate_icon_grid_item(identifier: str, path_data: str) -> str:
    """Generate HTML for a single icon grid item."""
    return f"""<div class="icon-item" data-name="{identifier}">
        <svg viewBox="0 0 16 16" width="40" height="40">
            <path d="{path_data}"/>
        </svg>
    </div>"""


def process_icons(icons_dir: Path) -> tuple[dict[str, dict], str]:
    """Process all SVG files in the icons directory."""
    icons_data: dict[str, dict] = {}
    icon_grid_items: list[str] = []

    for file_path in sorted(icons_dir.iterdir()):
        if file_path.suffix != ".svg":
            continue

        path_data = extract_path_from_svg(file_path)

        if path_data:
            name = generate_icon_name(file_path)
            identifier = generate_icon_identifier(file_path)
            tags = generate_icon_tags(file_path)
            description = generate_icon_description(name, tags)

            icons_data[identifier] = {
                "name": name,
                "identifier": identifier,
                "description": description,
                "tags": tags,
                "path": path_data,
            }

            icon_grid_items.append(
                generate_icon_grid_item(identifier, path_data)
            )

    return icons_data, "\n".join(icon_grid_items)


def generate_site_files(
    icons_data: dict[str, dict],
    icon_grid_html: str,
    template_dir: Path,
    output_dir: Path,
) -> None:
    """Generate site files from templates with icon data."""

    output_dir.mkdir(parents=True, exist_ok=True)

    icons_js: str = json.dumps(icons_data, indent=4)

    for template_file in ["site.template.html", "code.template.js"]:
        template_path: Path = template_dir / template_file
        output_path: Path = output_dir / template_file.replace(".template", "")

        with template_path.open() as src:
            content: str = src.read()

        if template_file == "site.template.html":
            content = content.replace("%ICONS_GRID%", icon_grid_html)
        else:
            content = content.replace("%ICONS_DATA%", icons_js)

        with output_path.open("w") as dst:
            dst.write(content)

    style_css_path: Path = template_dir / "style.css"
    output_style_css_path: Path = output_dir / "style.css"

    if style_css_path.exists():
        with (
            style_css_path.open() as src,
            output_style_css_path.open("w") as dst,
        ):
            dst.write(src.read())


def main() -> None:
    """Generate site files from templates with icon data."""

    icons_dir: Path = Path("icons")
    template_dir: Path = Path("data")
    output_dir: Path = Path("site")

    # Process icons
    icons_data, icon_grid_html = process_icons(icons_dir)

    # Generate site files
    generate_site_files(icons_data, icon_grid_html, template_dir, output_dir)
