"""Röntgen icons package.

This package provides access to Röntgen SVG icons and icon generation tools.
"""

from __future__ import annotations

import json
import logging
from importlib import resources
from typing import TYPE_CHECKING, Any, cast

from roentgen.icon import (
    IconSpecification,
    Shape,
    Shapes,
    get_icon_specifications,
)
from roentgen.icon_collection import IconSpecifications

if TYPE_CHECKING:
    from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)

ICON_LICENSE: str = """Röntgen icons (c) by Sergey Vartanov

Röntgen icons are licensed under a Creative Commons Attribution 4.0
International License.

You should have received a copy of the license along with this work.  If not,
see <http://creativecommons.org/licenses/by/4.0/>."""


class Roentgen:
    """Container for all Röntgen icons.

    Icons are loaded once on initialization. Each icon has an identifier (name)
    and SVG path commands.
    """

    def __init__(self) -> None:
        """Initialize and load all icons."""
        try:
            directory: Path = cast("Path", resources.files("roentgen"))
            with (directory / "config.json").open(
                encoding="utf-8"
            ) as input_file:
                self.config: dict[str, Any] = json.load(input_file)
            self.shapes: Shapes = Shapes()
            self.shapes.add_from_json(directory / "shapes.json")
        except (ModuleNotFoundError, TypeError) as exception:
            logger.fatal("Failed to load Röntgen files: %s", exception)
            return

        icon_specification_list: list[IconSpecification] = (
            get_icon_specifications(directory / "config.json")
        )
        self.icon_specifications: IconSpecifications
        self.icon_specifications = IconSpecifications.from_icon_specifications(
            icon_specification_list,
            filter_=lambda icon_specification: not icon_specification.is_part,
        )

    def get_shapes(self) -> Shapes:
        """Get all shapes."""
        return self.shapes

    def get_shape(self, shape_id: str) -> Shape | None:
        """Get shape by identifier."""
        return self.shapes.shapes.get(shape_id)

    def get_ids(self) -> list[str]:
        """Get all shape identifiers."""
        return list(self.shapes.shapes.keys())

    def get_license(self) -> str:
        """Get license text."""
        return ICON_LICENSE


_roentgen_instance: Roentgen | None = None


def get_roentgen() -> Roentgen:
    """Get the global Roentgen instance.

    :returns: Röntgen instance with all icons loaded
    """
    global _roentgen_instance  # noqa: PLW0603
    if _roentgen_instance is None:
        _roentgen_instance = Roentgen()
    return _roentgen_instance
