"""Main module."""

import argparse
import json
import logging
import shutil
from pathlib import Path

import numpy as np
from colour import Color

from roentgen.collection import main as collections_main
from roentgen.icon import IconSpecification, Shapes, get_icon_specifications
from roentgen.icon_collection import IconSpecifications
from roentgen.site import main as site_main
from roentgen.taginfo import main as taginfo_main

logger: logging.Logger = logging.getLogger(__name__)


def draw_icons(
    collection: IconSpecifications,
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
    raster_path: Path = root_path / "raster"

    collection.draw_icons(
        output_directory=icons_path,
        raster_directory=raster_path,
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
        raster_directory=raster_path,
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


def draw() -> None:
    """Draw all icons as grid and individual SVG files.

    Parse icons from SVG sketch files, iconscript files and config file.
    Generate:
      - individual SVG files for each icon,
      - grid SVG files for all icons,
      - JSON file with path for icons and part icons.
    """

    shapes: Shapes = Shapes()
    for path in [
        Path("data") / "icons.svg",
        Path("data") / "connectors.svg",
        Path("data") / "flag.svg",
        Path("data") / "lamp.svg",
        Path("data") / "letters.svg",
        Path("data") / "power.svg",
    ]:
        shapes.add_from_file(path)

    for path in [
        Path("iconscript") / "power.iconscript",
    ]:
        shapes.add_from_iconscript(path)

    version: str = Path("VERSION").read_text().strip()

    icon_specifications: list[IconSpecification] = get_icon_specifications(
        Path("data") / "config.json"
    )
    collection_no_parts: IconSpecifications = (
        IconSpecifications.from_icon_specifications(
            icon_specifications,
            filter_=lambda icon_specification: not icon_specification.is_part,
        )
    )

    for shape_id in shapes.shapes:
        found: bool = False
        for icon_specification in icon_specifications:
            if shape_id in icon_specification.get_shape_ids():
                found = True
                break
        if not found:
            logger.warning("No configuration for `%s` found.", shape_id)

    shapes_data: dict[str, str] = {
        shape_id: shape.get_path(
            "main",
            point=np.array((0, 0)),
            offset=np.array((0, 0)),
            scale=np.array((1, 1)),
        )
        .get_xml()
        .attrib["d"]
        for shape_id, shape in sorted(shapes.shapes.items())
        if "main" in shape.paths
    }
    with Path("shapes.json").open("w") as file:
        json.dump(shapes_data, file, indent=4)

    draw_icons(
        collection_no_parts,
        shapes,
        version=version,
        root_path=Path(),
        doc_path=Path("doc"),
        output_path=Path("out"),
    )


def main() -> None:
    """Run the main function."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=(
            "Röntgen CLI. You can also provide arguments in a file and use "
            "`@<filename>` on the command line. Each argument should be on a "
            "separate line in the file."
        ),
    )

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
    taginfo_parser.add_argument(
        "--defined-tags",
        action="store_true",
        default=False,
        help="Show tags defined in Röntgen or iD schema.",
    )
    taginfo_parser.add_argument(
        "--grouped-tags",
        action="store_true",
        default=False,
        help="Show tags grouped by key sorted by key frequency.",
    )
    taginfo_parser.add_argument(
        "--all-tags",
        action="store_true",
        default=False,
        help="Show all tags sorted by tag frequency.",
    )
    taginfo_parser.add_argument(
        "--min-frequency",
        type=int,
        default=1_000_000,
        help="Minimum frequency to display a tag.",
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

    collections_parser: argparse.ArgumentParser = subparsers.add_parser(
        "collections",
        help="Generate collections HTML page.",
    )
    collections_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the output directory.",
    )

    arguments: argparse.Namespace = parser.parse_args()

    if arguments.command == "icons":
        draw()
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
            min_frequency=arguments.min_frequency,
            show_defined_tags=arguments.defined_tags,
            show_grouped_tags=arguments.grouped_tags,
            show_all_tags=arguments.all_tags,
        )
        return

    if arguments.command == "collections":
        collections_main(output_directory=arguments.output)
        return

    if arguments.command == "site":
        site_main(site_path=arguments.output)
        return


if __name__ == "__main__":
    main()
