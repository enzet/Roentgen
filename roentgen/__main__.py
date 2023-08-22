import json
import logging
from pathlib import Path

from colour import Color

from roentgen.icon import Shape
from roentgen.icon_collection import ShapeExtractor, IconCollection


def draw_icons(
    root_path: Path,
    icon_paths: list[Path],
    icons_config_path: Path,
    combinations_path: Path,
    doc_path: Path,
    output_path: Path,
) -> None:
    """
    Draw all possible icon shapes combinations as grid in one SVG file and as
    individual SVG files.
    """
    collection: IconCollection = IconCollection()
    shapes: dict[str, Shape] = {}
    for path in icon_paths:
        extractor: ShapeExtractor = ShapeExtractor(path, icons_config_path)
        shapes |= extractor.shapes
        collection.add_from_scheme(extractor)

    with combinations_path.open() as input_file:
        combinations = json.load(input_file)

    collection.add_combinations(combinations, shapes)
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

    IconCollection().add_from_scheme(
        ShapeExtractor(Path("data") / "connectors.svg", icons_config_path)
    ).draw_grid(Path("doc") / "connectors.svg", scale=8.0, columns=6)


def main() -> None:
    draw_icons(
        Path("."),
        [Path("data") / "icons.svg", Path("data") / "connectors.svg"],
        Path("data") / "config.json",
        Path("data") / "combinations.json",
        Path("doc"),
        Path("."),
    )


if __name__ == "__main__":
    main()
