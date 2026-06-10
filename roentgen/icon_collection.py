"""Icon grid drawing."""

from __future__ import annotations

import math
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from colour import Color
from svgwrite import Drawing

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from roentgen.icon import IconSpecification, Shapes

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class IconSpecifications:
    """Collection of icon specifications."""

    icon_specifications: list[IconSpecification] = field(default_factory=list)

    @classmethod
    def from_icon_specifications(
        cls,
        icon_specifications: list[IconSpecification],
        filter_: Callable[[IconSpecification], bool] | None = None,
    ) -> IconSpecifications:
        """Create icon specifications from list of icon specifications."""
        return cls(
            [
                icon_specification
                for icon_specification in icon_specifications
                if filter_ is None or filter_(icon_specification)
            ]
        )

    def draw_icons(
        self,
        output_directory: Path,
        raster_directory: Path,
        shapes: Shapes,
        *,
        license_path: Path,
        version_path: Path,
        by_name: bool = False,
        outline: bool = False,
        outline_opacity: float = 1.0,
        only_sketch: bool = False,
    ) -> None:
        """Draw individual icons.

        :param output_directory: path to the directory to store individual SVG
            files for icons
        :param license_path: path to the file with license
        :param version_path: path to the file with version number
        :param by_name: use names instead of identifiers
        :param color: fill color
        :param outline: if true, draw outline beneath the icon
        :param outline_opacity: opacity of the outline
        """
        if by_name:

            def get_file_name(x: IconSpecification) -> str:
                """Generate human-readable file name."""
                return f"Röntgen {x.get_name()}.svg"

        else:

            def get_file_name(x: IconSpecification) -> str:
                """Generate file name with unique identifier."""
                return f"{x.get_id()}.svg"

        for icon_specification in self.icon_specifications:
            if only_sketch != icon_specification.is_sketch():
                continue
            icon_specification.draw_to_file(
                output_directory / get_file_name(icon_specification),
                shapes,
                outline=outline,
                outline_opacity=outline_opacity,
            )
            icon_specification.rasterize(
                output_directory / get_file_name(icon_specification),
                raster_directory,
            )

        shutil.copy(license_path, output_directory / "LICENSE")
        shutil.copy(version_path, output_directory / "VERSION")

    def draw_grid(
        self,
        file_name: Path,
        shapes: Shapes,
        *,
        columns: int = 16,
        step: float = 24.0,
        background_color: Color | None = None,
        scale: float = 1.0,
        show_boundaries: bool = False,
        draw_final: bool = True,
        draw_sketch: bool = False,
        color: Color | None = None,
        color_sketch: Color | None = None,
        width: float | None = None,
        height: float | None = None,
    ) -> None:
        """Draw icons in the form of a table.

        :param file_name: output SVG file name
        :param columns: number of columns in grid
        :param step: horizontal and vertical distance between icons in grid
        :param background_color: background color
        :param scale: scale icon by the magnitude
        :param show_boundaries: if true, draw boundaries around icons
        :param draw_final: if true, draw final icons
        :param draw_sketch: if true, draw sketch icons
        :param color: fill color for final icons
        :param color_sketch: fill color for sketch icons
        :param width: minimum output width; adds horizontal margins when grid
            is narrower
        :param height: minimum output height; adds vertical margins when grid
            is shorter
        """
        icon_specifications: list[IconSpecification] = [
            icon_specification
            for icon_specification in self.icon_specifications
            if (icon_specification.is_sketch() and draw_sketch)
            or (not icon_specification.is_sketch() and draw_final)
        ]

        if color is None:
            color = Color("#000000")
        if color_sketch is None:
            color_sketch = Color("#AAAAAA")

        grid_width: float = step * columns * scale
        grid_height: float = (
            math.ceil(len(icon_specifications) / columns) * step * scale
        )

        svg_width: float = (
            max(grid_width, width) if width is not None else grid_width
        )
        svg_height: float = (
            max(grid_height, height) if height is not None else grid_height
        )

        margin_x: float = (svg_width - grid_width) / 2
        margin_y: float = (svg_height - grid_height) / 2

        position: tuple[float, float] = (
            step / 2.0 * scale + margin_x,
            step / 2.0 * scale + margin_y,
        )

        svg: Drawing = Drawing(str(file_name), (svg_width, svg_height))
        if background_color is not None:
            svg.add(
                svg.rect(
                    (0, 0),
                    (svg_width, svg_height),
                    fill=background_color.hex,
                )
            )

        for icon_specification in icon_specifications:
            if show_boundaries:
                rectangle = svg.rect(
                    (position[0] - 14, position[1] - 14),
                    (28, 28),
                    fill="#DDFFFF",
                )
                svg.add(rectangle)
            icon_specification.draw(
                svg,
                shapes,
                position,
                scale=scale,
                color=color_sketch if icon_specification.is_sketch() else color,
            )
            position = (position[0] + step * scale, position[1])
            if position[0] > svg_width - margin_x - 8.0:
                position = (
                    step / 2.0 * scale + margin_x,
                    position[1] + step * scale,
                )

        with file_name.open("w", encoding="utf-8") as output_file:
            svg.write(output_file, pretty=True, indent=4)

    def __len__(self) -> int:
        return len(self.icon_specifications)

    def sort(self) -> None:
        """Sort icon list."""
        self.icon_specifications = sorted(self.icon_specifications)
