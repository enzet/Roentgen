"""Main module."""

import argparse
import logging
from pathlib import Path

from colour import Color

from roentgen.icon import Icon, Shapes, get_icons
from roentgen.icon_collection import IconCollection
from roentgen.site import main as site_main
from roentgen.taginfo import main as taginfo_main

logger: logging.Logger = logging.getLogger(__name__)


def draw_icons(
    collection: IconCollection,
    shapes: Shapes,
    *,
    root_path: Path,
    doc_path: Path,
    output_path: Path,
) -> None:
    """Draw all possible icon shapes combinations.

    Draw them
      - as grid in one SVG file and
      - as individual SVG files.
    """

    license_path: Path = root_path / "LICENSE"
    version_path: Path = root_path / "VERSION"

    # Draw individual icons.

    icons_by_id_path: Path = output_path / "icons"
    collection.draw_icons(
        output_directory=icons_by_id_path,
        shapes=shapes,
        license_path=license_path,
        version_path=version_path,
    )

    icons_by_name_path: Path = output_path / "icons_sketches"
    icons_by_name_path.mkdir(exist_ok=True)
    collection.draw_icons(
        output_directory=icons_by_name_path,
        shapes=shapes,
        license_path=license_path,
        version_path=version_path,
        only_sketch=True,
    )

    logger.info(
        "Icons are written to %s and %s.", icons_by_name_path, icons_by_id_path
    )

    # Draw grids.

    collection.draw_grid(
        doc_path / "grid_black.svg",
        shapes,
        background_color=None,
        scale=2.0,
        color=Color("#444"),
    )

    collection.draw_grid(
        doc_path / "grid_white.svg",
        shapes,
        background_color=None,
        scale=2.0,
        color=Color("#BBB"),
    )


def main() -> None:
    """Run the main function."""

    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    subparsers: argparse._SubParsersAction = parser.add_subparsers(
        dest="command"
    )
    _: argparse.ArgumentParser = subparsers.add_parser(
        "icons", help="Draw icons as grid and individual SVG files."
    )

    taginfo_parser: argparse.ArgumentParser = subparsers.add_parser(
        "taginfo", help="Generate insights about OSM tag coverage."
    )
    taginfo_parser.add_argument(
        "--id-tagging-schema",
        type=Path,
        help="Path to the id-tagging-schema directory.",
    )
    taginfo_parser.add_argument(
        "--id",
        type=Path,
        help="Path to the iD directory.",
    )
    taginfo_parser.add_argument(
        "--maki",
        type=Path,
        help="Path to the Maki directory.",
    )
    taginfo_parser.add_argument(
        "--temaki", type=Path, help="Path to the Temaki directory."
    )

    site_parser: argparse.ArgumentParser = subparsers.add_parser(
        "site",
        help="Generate Röntgen website.",
    )
    site_parser.add_argument(
        "-o",
        "--output",
        default=Path("site"),
        type=Path,
        help="Path to the output directory.",
    )

    arguments: argparse.Namespace = parser.parse_args()

    if arguments.command == "icons":
        logging.basicConfig(level=logging.INFO)

        shapes: Shapes = Shapes()
        for path in [
            Path("data") / "icons.svg",
            Path("data") / "connectors.svg",
        ]:
            shapes.add_from_file(path)

        icons: list[Icon] = get_icons(Path("data") / "config.json")
        main_collection: IconCollection = IconCollection.from_icons(
            icons,
            filter_=lambda icon: not icon.is_part,
        )
        draw_icons(
            main_collection,
            shapes,
            root_path=Path(),
            doc_path=Path("doc"),
            output_path=Path(),
        )
        return

    if arguments.command == "taginfo":
        id_tagging_schema_path: Path | None = (
            Path(arguments.id_tagging_schema)
            if arguments.id_tagging_schema is not None
            else None
        )
        id_path: Path | None = (
            Path(arguments.id) if arguments.id is not None else None
        )
        maki_path: Path | None = (
            Path(arguments.maki) if arguments.maki is not None else None
        )
        temaki_path: Path | None = (
            Path(arguments.temaki) if arguments.temaki is not None else None
        )
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        taginfo_main(
            Path("data") / "tags.json",
            id_tagging_schema_path=id_tagging_schema_path,
            id_path=id_path,
            maki_path=maki_path,
            temaki_path=temaki_path,
        )
        return

    if arguments.command == "site":
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        site_main(output_path=arguments.output)
        return


if __name__ == "__main__":
    main()
