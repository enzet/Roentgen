"""Icon grid drawing."""

from __future__ import annotations

import math
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
from svgwrite import Drawing

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from colour import Color
    from numpy.typing import NDArray

    from roentgen.icon import Icon, Shapes

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


@dataclass
class IconCollection:
    """Collection of icons."""

    icons: list[Icon] = field(default_factory=list)

    @classmethod
    def from_icons(
        cls,
        icons: list[Icon],
        filter_: Callable[[Icon], bool] | None = None,
    ) -> IconCollection:
        """Create icon collection from list of icons."""
        return cls([icon for icon in icons if filter_ is None or filter_(icon)])

    def draw_icons(
        self,
        output_directory: Path,
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

            def get_file_name(x: Icon) -> str:
                """Generate human-readable file name."""
                return f"Röntgen {x.get_name()}.svg"

        else:

            def get_file_name(x: Icon) -> str:
                """Generate file name with unique identifier."""
                return f"{x.get_id()}.svg"

        for icon in self.icons:
            icon.draw_to_file(
                output_directory / get_file_name(icon),
                shapes,
                outline=outline,
                outline_opacity=outline_opacity,
                only_sketch=only_sketch,
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
        only_sketch: bool = False,
        color: Color | None = None,
    ) -> None:
        """Draw icons in the form of a table.

        :param file_name: output SVG file name
        :param columns: number of columns in grid
        :param step: horizontal and vertical distance between icons in grid
        :param background_color: background color
        :param scale: scale icon by the magnitude
        :param show_boundaries: if true, draw boundaries around icons
        :param only_sketch: if true, draw only sketch icons
        :param color: fill color
        """
        position: NDArray = np.array((step / 2.0 * scale, step / 2.0 * scale))
        width: float = step * columns * scale

        icons: list[Icon] = [
            icon for icon in self.icons if only_sketch == icon.is_sketch()
        ]

        height: int = int(math.ceil(len(icons) / columns) * step * scale)
        svg: Drawing = Drawing(str(file_name), (width, height))
        if background_color is not None:
            svg.add(
                svg.rect((0, 0), (width, height), fill=background_color.hex)
            )

        for icon in icons:
            if show_boundaries:
                rectangle = svg.rect(
                    (position[0] - 14, position[1] - 14),
                    (28, 28),
                    fill="#DDFFFF",
                )
                svg.add(rectangle)
            icon.draw(svg, shapes, position, scale=scale, color=color)
            position += np.array((step * scale, 0.0))
            if position[0] > width - 8.0:
                position[0] = step / 2.0 * scale
                position += np.array((0.0, step * scale))
                height += int(step * scale)

        with file_name.open("w", encoding="utf-8") as output_file:
            svg.write(output_file, pretty=True, indent=4)

    def __len__(self) -> int:
        return len(self.icons)

    def sort(self) -> None:
        """Sort icon list."""
        self.icons = sorted(self.icons)
