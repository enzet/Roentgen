import logging
from pathlib import Path

from colour import Color

from generator.icon_collection import ShapeExtractor, IconCollection


def draw_icons(
    root_path: Path,
    icons_path: Path,
    icons_config_path: Path,
    doc_path: Path,
    output_path: Path,
) -> None:
    """
    Draw all possible icon shapes combinations as grid in one SVG file and as
    individual SVG files.
    """
    extractor: ShapeExtractor = ShapeExtractor(icons_path, icons_config_path)
    collection: IconCollection = IconCollection.from_scheme(extractor)
    collection.sort()

    license_path: Path = root_path / "LICENSE"

    # Draw individual icons.

    icons_by_id_path: Path = output_path / "icons"
    collection.draw_icons(icons_by_id_path, license_path)

    icons_by_name_path: Path = output_path / "icons_by_name"
    collection.draw_icons(icons_by_name_path, license_path, by_name=True)

    logging.info(
        f"Icons are written to {icons_by_name_path} and {icons_by_id_path}."
    )

    # Draw grid.

    for icon in collection.icons:
        icon.recolor(Color("#444"))
    collection.draw_grid(
        doc_path / "grid_black.svg", background_color=None, scale=2.0
    )

    for icon in collection.icons:
        icon.recolor(Color("#ABB"))
    collection.draw_grid(
        doc_path / "grid_white.svg", background_color=None, scale=2.0
    )


if __name__ == "__main__":
    draw_icons(
        Path("."),
        Path("data") / "icons.svg",
        Path("data") / "config.json",
        Path("doc"),
        Path("."),
    )
