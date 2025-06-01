"""Icon grid drawing."""

from __future__ import annotations

import math
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from colour import Color
from svgwrite import Drawing

from roentgen.icon import Icon, Shape, ShapeExtractor, ShapeSpecification

if TYPE_CHECKING:
    from pathlib import Path

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class IconCollection:
    """Collection of icons."""

    icons: list[Icon] = field(default_factory=list)

    def add_from_scheme(
        self,
        extractor: ShapeExtractor,
        *,
        background_color: Color,
        color: Color,
        add_unused: bool = False,
        add_all: bool = False,
    ) -> IconCollection:
        """Collect all possible icon combinations.

        This collection won't contain icons for tags matched with regular
        expressions. E.g. traffic_sign=maxspeed; maxspeed=42.

        :param extractor: shape extractor for icon creation
        :param background_color: background color
        :param color: icon color
        :param add_unused: create icons from shapes that have no corresponding
            tags
        :param add_all: create icons from all possible shapes including parts
        """
        for key, value in extractor.configuration.items():
            if value.get("is_part"):
                continue
            if extractor.has_shape(key):
                specifications: list[ShapeSpecification] = [
                    ShapeSpecification(extractor.get_shape(key), color)
                ]
                constructed_icon: Icon = Icon(specifications)
                constructed_icon.recolor(color, white=background_color)
                if constructed_icon not in self.icons:
                    self.icons.append(constructed_icon)

        specified_ids: set[str] = set()

        icon: Icon
        shape: Shape

        for icon in self.icons:
            specified_ids |= set(icon.get_shape_ids())

        if add_unused:
            for shape_id in extractor.shapes.keys() - specified_ids:
                shape = extractor.get_shape(shape_id)
                if shape.is_part:
                    continue
                icon = Icon([ShapeSpecification(shape, color)])
                icon.recolor(color, white=background_color)
                self.icons.append(icon)

        if add_all:
            for shape_id in extractor.shapes:
                shape = extractor.get_shape(shape_id)
                icon = Icon([ShapeSpecification(shape, color)])
                icon.recolor(color, white=background_color)
                self.icons.append(icon)

        return self

    def draw_icons(
        self,
        output_directory: Path,
        license_path: Path,
        *,
        by_name: bool = False,
        color: Color | None = None,
        outline: bool = False,
        outline_opacity: float = 1.0,
    ) -> None:
        """Draw individual icons.

        :param output_directory: path to the directory to store individual SVG
            files for icons
        :param license_path: path to the file with license
        :param by_name: use names instead of identifiers
        :param color: fill color
        :param outline: if true, draw outline beneath the icon
        :param outline_opacity: opacity of the outline
        """
        if by_name:

            def get_file_name(x: Icon) -> str:
                """Generate human-readable file name."""
                return f"Röntgen {x.get_name()}.svg"

        else:

            def get_file_name(x: Icon) -> str:
                """Generate file name with unique identifier."""
                return f"roentgen_{'___'.join(x.get_shape_ids())}.svg"

        for icon in self.icons:
            icon.draw_to_file(
                output_directory / get_file_name(icon),
                color=color,
                outline=outline,
                outline_opacity=outline_opacity,
            )

        shutil.copy(license_path, output_directory / "LICENSE")

    def draw_grid(
        self,
        file_name: Path,
        *,
        columns: int = 16,
        step: float = 24.0,
        background_color: Color | None = None,
        scale: float = 1.0,
    ) -> None:
        """Draw icons in the form of a table.

        :param file_name: output SVG file name
        :param columns: number of columns in grid
        :param step: horizontal and vertical distance between icons in grid
        :param background_color: background color
        :param scale: scale icon by the magnitude
        """
        point: np.ndarray = np.array((step / 2.0 * scale, step / 2.0 * scale))
        width: float = step * columns * scale

        height: int = int(math.ceil(len(self.icons) / columns) * step * scale)
        svg: Drawing = Drawing(str(file_name), (width, height))
        if background_color is not None:
            svg.add(
                svg.rect((0, 0), (width, height), fill=background_color.hex)
            )

        for icon in self.icons:
            icon.draw(svg, point, scale=scale)
            point += np.array((step * scale, 0.0))
            if point[0] > width - 8.0:
                point[0] = step / 2.0 * scale
                point += np.array((0.0, step * scale))
                height += int(step * scale)

        with file_name.open("w", encoding="utf-8") as output_file:
            svg.write(output_file, pretty=True, indent=4)

    def __len__(self) -> int:
        return len(self.icons)

    def sort(self) -> None:
        """Sort icon list."""
        self.icons = sorted(self.icons)

    def add_combinations(
        self,
        combinations: list[list[dict[str, Any]]],
        shapes: dict[str, Shape],
    ) -> None:
        """Add combinations of shapes to the collection."""

        # TODO(enzet): use color from the configuration.
        color = Color("black")
        background_color = Color("white")

        for elements in combinations:
            specifications: list[ShapeSpecification] = []

            for element in elements:
                specification = ShapeSpecification(
                    shapes[element["id"]],
                    offset=np.array(element.get("offset", [0, 0])),
                    flip_horizontally=element.get("flip_horizontally", False),
                    flip_vertically=element.get("flip_vertically", False),
                    color=color,
                )
                specifications.append(specification)

            constructed_icon: Icon = Icon(specifications)
            constructed_icon.recolor(color, white=background_color)
            if constructed_icon not in self.icons:
                self.icons.append(constructed_icon)
