"""Main module."""

import argparse
import logging
import shutil
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
    version: str,
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

    icons_path: Path = root_path / "icons"
    collection.draw_icons(
        output_directory=icons_path,
        shapes=shapes,
        license_path=license_path,
        version_path=version_path,
    )
    to_zip_path: Path = output_path / f"roentgen-{version}"
    if to_zip_path.exists():
        shutil.rmtree(to_zip_path)
    shutil.copytree(icons_path, to_zip_path)
    # Zip `roentgen-<version>` directory to `roentgen-<version>.zip`.
    shutil.make_archive(
        str(output_path / f"roentgen-{version}"),
        "zip",
        to_zip_path,
    )
    shutil.rmtree(to_zip_path)

    icons_sketches_path: Path = root_path / "icons_sketches"
    icons_sketches_path.mkdir(exist_ok=True)
    collection.draw_icons(
        output_directory=icons_sketches_path,
        shapes=shapes,
        license_path=license_path,
        version_path=version_path,
        only_sketch=True,
    )

    logger.info(
        "Icons are written to `%s`, sketch icons to `%s`.",
        icons_path,
        icons_sketches_path,
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
    logger.info(
        "Grids are written to `%s` and `%s`.",
        doc_path / "grid_black.svg",
        doc_path / "grid_white.svg",
    )


def main() -> None:
    """Run the main function."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")

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
        type=Path,
        help="Path to the output directory.",
    )

    arguments: argparse.Namespace = parser.parse_args()

    if arguments.command == "icons":
        shapes: Shapes = Shapes()
        for path in [
            Path("data") / "icons.svg",
            Path("data") / "connectors.svg",
            Path("data") / "power.svg",
            Path("data") / "letters.svg",
            Path("data") / "flag.svg",
        ]:
            shapes.add_from_file(path)

        version: str = Path("VERSION").read_text().strip()

        icons: list[Icon] = get_icons(Path("data") / "config.json")
        main_collection: IconCollection = IconCollection.from_icons(
            icons,
            filter_=lambda icon: not icon.is_part,
        )

        for shape_id in shapes.shapes:
            found: bool = False
            for icon in icons:
                if shape_id in icon.get_shape_ids():
                    found = True
                    break
            if not found:
                logger.warning("No configuration for `%s` found.", shape_id)

        draw_icons(
            main_collection,
            shapes,
            version=version,
            root_path=Path(),
            doc_path=Path("doc"),
            output_path=Path("out"),
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
        taginfo_main(
            Path("data") / "tags.json",
            id_tagging_schema_path=id_tagging_schema_path,
            id_path=id_path,
            maki_path=maki_path,
            temaki_path=temaki_path,
            show_defined_tags=True,
        )
        return

    if arguments.command == "site":
        site_main(site_path=arguments.output)
        return


if __name__ == "__main__":
    main()
