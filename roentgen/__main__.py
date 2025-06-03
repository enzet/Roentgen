"""Main module."""

import argparse
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from colour import Color

from roentgen.icon_collection import IconCollection, ShapeExtractor

if TYPE_CHECKING:
    from roentgen.icon import Shape

logger: logging.Logger = logging.getLogger(__name__)


def get_main_collection(
    *,
    icon_paths: list[Path],
    icons_config_path: Path,
    combinations: list[list[dict[str, Any]]],
) -> IconCollection:
    """Get main collection of icons."""

    collection: IconCollection = IconCollection()
    shapes: dict[str, Shape] = {}
    for path in icon_paths:
        extractor: ShapeExtractor = ShapeExtractor(path, icons_config_path)
        shapes |= extractor.shapes
        collection.add_from_scheme(
            extractor,
            background_color=Color("white"),
            color=Color("black"),
        )

    collection.add_combinations(combinations, shapes)
    collection.sort()

    return collection


def draw_icons(
    collection: IconCollection,
    *,
    root_path: Path,
    icons_config_path: Path,
    doc_path: Path,
    output_path: Path,
) -> None:
    """Draw all possible icon shapes combinations.

    Draw them
      - as grid in one SVG file and
      - as individual SVG files.
    """

    license_path: Path = root_path / "LICENSE"

    # Draw individual icons.

    icons_by_id_path: Path = output_path / "icons"
    collection.draw_icons(icons_by_id_path, license_path)

    icons_by_name_path: Path = output_path / "icons_by_name"
    icons_by_name_path.mkdir(exist_ok=True)
    collection.draw_icons(icons_by_name_path, license_path, by_name=True)

    logger.info(
        "Icons are written to %s and %s.", icons_by_name_path, icons_by_id_path
    )

    # Draw grids.

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
        ShapeExtractor(Path("data") / "connectors.svg", icons_config_path),
        background_color=Color("white"),
        color=Color("black"),
    ).draw_grid(
        Path("doc") / "connectors.svg",
        background_color=Color("white"),
        scale=8.0,
        columns=6,
    )


def main() -> None:
    """Run the main function."""

    logging.basicConfig(level=logging.INFO)

    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["generate"])

    arguments: argparse.Namespace = parser.parse_args()

    with (Path("data") / "combinations.json").open() as input_file:
        combinations: list[list[dict[str, Any]]] = json.load(input_file)

    if arguments.command == "generate":
        main_collection: IconCollection = get_main_collection(
            icon_paths=[
                Path("data") / "icons.svg",
                Path("data") / "connectors.svg",
            ],
            icons_config_path=Path("data") / "config.json",
            combinations=combinations,
        )
        draw_icons(
            main_collection,
            root_path=Path(),
            icons_config_path=Path("data") / "config.json",
            doc_path=Path("doc"),
            output_path=Path(),
        )


if __name__ == "__main__":
    main()
