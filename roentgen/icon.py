"""Extract icons from SVG file."""

from __future__ import annotations

import contextlib
import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

try:
    import cairosvg
except ImportError:
    cairosvg = None

import numpy as np
import svgwrite
from colour import Color
from svgpathtools import Path as ToolsPath
from svgpathtools import parse_path
from svgwrite import Drawing
from svgwrite.container import Group

if TYPE_CHECKING:
    from pathlib import Path
    from xml.etree.ElementTree import Element

    from numpy.typing import NDArray
    from svgwrite.base import BaseElement
    from svgwrite.path import Path as SVGPath

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

DEFAULT_SHAPE_ID: str = "default"
DEFAULT_SMALL_SHAPE_ID: str = "default_small"

STANDARD_INKSCAPE_ID_MATCHER: re.Pattern = re.compile(
    "^((circle|defs|ellipse|grid|guide|marker|metadata|namedview|path|rect|use)"
    "[\\d-]+|base)$"
)
VERSION_MATCHER: re.Pattern = re.compile(
    "^(?P<id>[a-z0-9_]+)_(?P<version>v[0-9]+)$"
)

PATH_MATCHER: re.Pattern = re.compile("[Mm] ([0-9.e-]*)[, ]([0-9.e-]*)")

GRID_STEP: int = 16

USED_ICON_COLOR: str = "#000000"
UNUSED_ICON_COLORS: list[str] = ["#0000ff", "#ff0000"]
FUTURE_ICON_COLOR: str = "880000"


def is_bright(color: Color) -> bool:
    """Check whether color is bright.

    Meaning that the color is bright enough to have black outline instead of
    white.
    """
    return (
        0.2126 * color.red + 0.7152 * color.green + 0.0722 * color.blue
        > 0.78125  # noqa: PLR2004
    )


def round_complex(value: complex, precision: int) -> complex:
    """Round complex number to the given precision."""
    return round(value.real, precision) + round(value.imag, precision) * 1j


@dataclass
class PathOnCanvas:
    """Path on canvas."""

    path: str
    """SVG path commands."""

    offset: NDArray
    """Offset of the path on the canvas."""


@dataclass
class Shape:
    """SVG icon path description."""

    paths: dict[str, PathOnCanvas]
    """Paths and their offsets for different versions."""

    id_: str
    """Shape unique string identifier, e.g. `tree`."""

    def is_default(self) -> bool:
        """Return true if the shape doesn't represent anything."""
        return self.id_ in [DEFAULT_SHAPE_ID, DEFAULT_SMALL_SHAPE_ID]

    def get_path(
        self,
        version: str,
        *,
        point: NDArray,
        offset: NDArray,
        scale: NDArray,
        use_transform: bool = False,
    ) -> SVGPath:
        """Get SVG path for the shape.

        :param point: icon position
        :param offset: additional offset
        :param scale: scale resulting image
        :param use_transform: use SVG `translate` method instead of rewriting
            path
        """
        shift: NDArray = point + offset

        if use_transform:
            path_on_canvas: PathOnCanvas = self.paths[version]
            path: SVGPath = svgwrite.path.Path(d=path_on_canvas.path)
            if not np.allclose(shift, np.array((0.0, 0.0))):
                path.translate(shift[0], shift[1])
            if not np.allclose(scale, np.array((1.0, 1.0))):
                path.scale(scale[0], scale[1])
            if not np.allclose(path_on_canvas.offset, np.array((0.0, 0.0))):
                path.translate(
                    path_on_canvas.offset[0], path_on_canvas.offset[1]
                )
        else:
            if version not in self.paths:
                message = (
                    f"No version {version} for shape `{self.id_}`, available "
                    f"versions: {', '.join(self.paths.keys())}"
                )
                raise ValueError(message)
            path_on_canvas = self.paths[version]
            parsed_path: ToolsPath = parse_path(path_on_canvas.path)
            if not np.allclose(path_on_canvas.offset, np.array((0.0, 0.0))):
                parsed_path = parsed_path.translated(
                    path_on_canvas.offset[0] + path_on_canvas.offset[1] * 1j
                )
            if not np.allclose(scale, np.array((1.0, 1.0))):
                parsed_path = parsed_path.scaled(scale[0], scale[1])
            if not np.allclose(shift, np.array((0.0, 0.0))):
                parsed_path = parsed_path.translated(shift[0] + shift[1] * 1j)

            for element in parsed_path:
                for attribute in (
                    "start",
                    "end",
                    "control1",
                    "control2",
                    "radius",
                ):
                    if hasattr(element, attribute):
                        setattr(
                            element,
                            attribute,
                            round_complex(getattr(element, attribute), 4),
                        )
            path = svgwrite.path.Path(d=parsed_path.d())

        return path


def parse_length(text: str) -> float:
    """Parse length from SVG attribute."""
    text = text.removesuffix("px")
    return float(text)


def check_sketch_fill_element(style: dict[str, str]) -> bool:
    """Check whether style is black 0.1 px stroke, no fill."""
    return (
        "fill" in style
        and style["fill"] == "none"
        and style["stroke"] == "#000000"
        and "stroke-width" in style
        and np.allclose(parse_length(style["stroke-width"]), 0.1)
    )


def check_sketch_stroke_element(style: dict[str, str]) -> bool:
    """Check whether style is black stroke, no fill, 20% opacity."""
    return (
        "fill" in style
        and style["fill"] == "none"
        and style["stroke"] == "#000000"
        and "opacity" in style
        and np.allclose(float(style["opacity"]), 0.2)
        and (
            "stroke-width" not in style
            or np.allclose(parse_length(style["stroke-width"]), 0.7)
            or np.allclose(parse_length(style["stroke-width"]), 1)
            or np.allclose(parse_length(style["stroke-width"]), 2)
            or np.allclose(parse_length(style["stroke-width"]), 3)
        )
    )


def check_future_shape(style: dict[str, str]) -> bool:
    """Check whether style is future icon."""
    return (
        "fill" in style
        and style["fill"] == FUTURE_ICON_COLOR
        and "stroke" in style
        and style["stroke"] == "none"
    )


def check_experimental_shape(style: dict[str, str]) -> bool:
    """Check whether style is blue or red fill, no stroke."""
    return (
        "fill" in style
        and style["fill"] in [*UNUSED_ICON_COLORS, FUTURE_ICON_COLOR]
        and "stroke" in style
        and style["stroke"] == "none"
    )


def is_sketch_element(element: Element, id_: str) -> bool:
    """Check whether SVG element is a sketch element.

    Sketch element is a primitive (path, ellipse, rectangle, etc.) that is used
    to create shapes. It may be
      - a stroke element (has black stroke, has no fill, opacity is 20%) or
      - a fill element (has no fill, has black stroke with 0.1 width, opacity is
        100%).

    :param element: sketch SVG element (element with standard Inkscape
        identifier)
    :param id_: element `id` attribute
    :return: True iff SVG element has valid style
    """
    style: dict[str, str] = {
        x.split(":")[0]: x.split(":")[1]
        for x in element.attrib["style"].split(";")
    }
    return (
        check_sketch_stroke_element(style)
        or check_sketch_fill_element(style)
        or not (style and not id_.startswith("use"))
    )


def parse_configuration(root: dict, configuration: dict, group: str) -> None:
    """Parse shape configuration.

    Shape description is a probably empty dictionary with optional fields
    `name`, `unicode`, `is_part`, `directed`, `keywords`, and `categories`.
    Shape configuration is a dictionary that contains shape descriptions.
    Shape descriptions may be grouped and the nesting level may be arbitrary.
    Group identifier should be started with `__`, e.g. `__buildings`.

    ```json
    {
        <shape id>: {<shape description>},
        <shape id>: {<shape description>},
        <group id>: {
            <shape id>: {<shape description>},
            <shape id>: {<shape description>}
        },
        <group id>: {
            <subgroup id>: {
                <shape id>: {<shape description>},
                <shape id>: {<shape description>}
            }
        }
    }
    ```
    """
    for key, value in root.items():
        if key.startswith("__"):
            parse_configuration(value, configuration, f"{group}_{key}")
        else:
            configuration[key] = value | {"group": group}


def get_icons(configuration_path: Path) -> list[Icon]:
    """Get icons from configuration."""
    icons: list[Icon] = []
    configuration: dict[str, Any] = {}
    with configuration_path.open() as input_file:
        parse_configuration(json.load(input_file), configuration, "")
    for key, value in configuration.items():
        icons.append(Icon.from_structure(key, value))
    return icons


@dataclass
class Shapes:
    """Extract shapes from SVG file.

    Shape is a single path with "id" attribute that aligned to 16 × 16 grid.
    """

    shapes: dict[str, Shape] = field(default_factory=dict)
    """Shapes."""

    def add_from_file(self, svg_file_name: Path) -> None:
        """Add shapes from SVG file.

        :param svg_file_name: input SVG file name with icons.  File may contain
            any other irrelevant graphics.
        """
        root: Element = ET.parse(svg_file_name).getroot()  # noqa: S314
        self.__parse(root, svg_file_name)

    def __parse(self, node: Element, svg_file_name: Path) -> None:
        """Extract icon paths into a map.

        :param node: XML node that contains icon
        """
        if node.tag.endswith("}g") or node.tag.endswith("}svg"):
            for sub_node in node:
                self.__parse(sub_node, svg_file_name)
            return

        if "id" not in node.attrib or not node.attrib["id"]:
            return

        if "style" not in node.attrib or not node.attrib["style"]:
            return

        id_: str = node.attrib["id"]
        if STANDARD_INKSCAPE_ID_MATCHER.match(id_) is not None:
            if not is_sketch_element(node, id_):
                path_part = ""
                with contextlib.suppress(KeyError, ValueError):
                    path_part = f", {node.attrib['d'].split(' ')[:3]}"
                message: str = (
                    f"Not verified SVG element `{id_}`{path_part} in "
                    f"`{svg_file_name}`"
                )
                raise ValueError(message)
            return

        version: str = "main"

        if match := VERSION_MATCHER.match(id_):
            style: dict[str, str] = {
                x.split(":")[0]: x.split(":")[1]
                for x in node.attrib["style"].split(";")
            }
            version = match.group("version")
            id_ = match.group("id")
            if not check_experimental_shape(style):
                message = (
                    f"Not verified experimental SVG element `{id_}` in "
                    f"`{svg_file_name}`"
                )
                raise ValueError(message)

        if node.attrib.get("d"):
            path: str = node.attrib["d"]
            matcher = PATH_MATCHER.match(path)
            if not matcher:
                return

            def get_offset(value: str) -> float:
                """Get negated icon offset from the origin."""
                return (
                    -int(float(value) / GRID_STEP) * GRID_STEP - GRID_STEP / 2.0
                )

            offset: NDArray = np.array(
                (get_offset(matcher.group(1)), get_offset(matcher.group(2)))
            )
            if id_ in self.shapes:
                shape = self.shapes[id_]
                shape.paths[version] = PathOnCanvas(path, offset)
            else:
                self.shapes[id_] = Shape(
                    {version: PathOnCanvas(path, offset)}, id_
                )
        else:
            message = f"Not standard ID `{id_}` in `{svg_file_name}`."
            raise ValueError(message)

    def has_shape(self, id_: str) -> bool:
        """Check whether shape with such identifier exists."""
        return id_ in self.shapes

    def get_shape(self, id_: str) -> Shape:
        """Get shape or `None` if there is no shape with such identifier.

        :param id_: string icon identifier
        """
        if id_ in self.shapes:
            return self.shapes[id_]

        message: str = f"no shape with id `{id_}` in icons file"
        raise AssertionError(message)


@dataclass
class ShapeSpecification:
    """Specification for shape as a part of an icon."""

    shape_id: str
    """Shape identifier."""

    version: str
    """Shape version."""

    offset: NDArray = field(default_factory=lambda: np.array((0.0, 0.0)))
    """Shape offset."""

    flip_horizontally: bool = False
    """Flip shape horizontally."""

    flip_vertically: bool = False
    """Flip shape vertically."""

    use_outline: bool = True
    """If the shape is supposed to be outlined."""

    @classmethod
    def from_structure(cls, structure: dict[str, Any]) -> ShapeSpecification:
        """Parse shape specification from structure."""
        return cls(
            structure["id"],
            structure.get("version", "main"),
            np.array(structure.get("offset", (0.0, 0.0))),
            structure.get("flip_horizontally", False),
            structure.get("flip_vertically", False),
            structure.get("use_outline", True),
        )

    def is_default(self) -> bool:
        """Check whether shape is default."""
        return self.shape_id == DEFAULT_SHAPE_ID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ShapeSpecification):
            return False

        return (
            self.shape_id == other.shape_id
            and self.version == other.version
            and np.allclose(self.offset, other.offset)
        )

    def __lt__(self, other: ShapeSpecification) -> bool:
        return self.shape_id < other.shape_id


class Drawer:
    """Drawer for shapes."""

    def __init__(self, shapes: Shapes) -> None:
        """Initialize drawer."""
        self.shapes = shapes

    def draw(
        self,
        svg: BaseElement,
        specification: ShapeSpecification,
        position: NDArray,
        tags: dict[str, Any] | None = None,
        *,
        outline: bool = False,
        outline_opacity: float = 1.0,
        scale: float = 1.0,
        color: Color | None = None,
    ) -> None:
        """Draw icon shape into SVG file.

        :param svg: output SVG file
        :param point: 2D position of the shape centre
        :param tags: tags to be displayed as a tooltip, if tooltip should not be
            displayed, this argument should be None
        :param outline: draw outline for the shape
        :param outline_opacity: opacity of the outline
        :param scale: scale icon by the magnitude
        :param color: fill color
        """
        scale_vector: NDArray = np.array((scale, scale))
        if specification.flip_vertically:
            scale_vector = np.array((scale, -scale))
        if specification.flip_horizontally:
            scale_vector = np.array((-scale, scale))

        if not color:
            color = Color("black")

        point = np.array(list(map(int, position)))
        path: SVGPath = self.shapes.get_shape(specification.shape_id).get_path(
            specification.version,
            point=point,
            offset=specification.offset * scale,
            scale=scale_vector,
        )
        path.update({"fill": color.hex})

        if outline and specification.use_outline:
            outline_color: Color = (
                Color("black") if is_bright(color) else Color("white")
            )
            style: dict[str, Any] = {
                "fill": outline_color.hex,
                "stroke": outline_color.hex,
                "stroke-width": 2.2,
                "stroke-linejoin": "round",
                "opacity": outline_opacity,
            }
            path.update(style)
        if tags:
            title: str = "\n".join(x + ": " + tags[x] for x in tags)
            path.set_desc(title=title)

        svg.add(path)


@dataclass
class Icon:
    """Icon that consists of (probably) multiple shapes."""

    icon_id: str
    """Icon identifier."""

    shape_specifications: list[ShapeSpecification]
    """List of shape specifications."""

    name: str
    """Human-readable icon name."""

    sketch: bool = False
    """Whether the icon is a sketch."""

    unicode: set[str] = field(default_factory=set)
    """Set of Unicode characters that represent the same entity.

    E.g. 🍐 (pear) for `pear`; 🍏 (green apple) and 🍎 (red apple) for `apple`.
    """

    is_part: bool = False
    """If shape is used only as a part of other icons."""

    group: str = ""
    """Hierarchical icon group.  Is used for icon sorting."""

    categories: set[str] = field(default_factory=set)
    """Icon categories that is used in OpenStreetMap wiki.

    E.g. `barrier` means
    https://wiki.openstreetmap.org/wiki/Category:Barrier_icons.
    """

    keywords: set[str] = field(default_factory=set)
    """Keywords that are used to search for the icon."""

    is_right_directed: bool | None = None
    """If shape is directed.

    If value is `None`, shape doesn't have distinct direction or its
    direction doesn't make sense.  Shape is directed to the right if value is
    `True` and to the left if value is `False`.

    E.g. CCTV camera shape has direction and may be flipped horizontally to
    follow surveillance direction, whereas car shape has direction but
    flipping icon doesn't make any sense.
    """

    @classmethod
    def from_structure(cls, id_: str, structure: dict[str, Any]) -> Icon:
        """Parse icon description from structure."""

        shapes: list[ShapeSpecification]
        if "shapes" in structure:
            shapes = [
                ShapeSpecification.from_structure(x)
                for x in structure["shapes"]
            ]
        else:
            shapes = [ShapeSpecification(id_, "main")]

        icon: Icon = cls(
            id_,
            shapes,
            name=structure["name"],
            sketch=structure.get("sketch", False),
            is_part=structure.get("is_part", False),
        )

        if "unicode" in structure:
            icon.unicode = set(structure["unicode"])

        if "sketch" in structure:
            icon.sketch = structure["sketch"]

        if "keywords" in structure:
            icon.keywords = set(structure["keywords"])

        icon.is_part = structure.get("is_part", False)
        icon.group = structure.get("group", "")

        if "categories" in structure:
            icon.categories = set(structure["categories"])

        if "directed" in structure:
            if structure["directed"] == "right":
                icon.is_right_directed = True
            if structure["directed"] == "left":
                icon.is_right_directed = False

        return icon

    def get_id(self) -> str:
        """Get icon identifier."""
        return self.icon_id

    def get_shape_ids(self) -> list[str]:
        """Get all shape identifiers in the icon."""
        return [x.shape_id for x in self.shape_specifications]

    def get_name(self) -> str:
        """Get combined human-readable icon name."""
        return self.name

    def has_categories(self) -> bool:
        """Check whether oll shape categories are known."""
        return bool(self.categories)

    def get_categories(self) -> set[str]:
        """Get all shape names in the icon."""
        return self.categories

    def draw(
        self,
        svg: svgwrite.Drawing,
        shapes: Shapes,
        position: NDArray,
        tags: dict[str, Any] | None = None,
        *,
        opacity: float = 1.0,
        outline: bool = False,
        scale: float = 1.0,
        color: Color | None = None,
    ) -> None:
        """Draw icon to SVG.

        :param svg: output SVG file
        :param point: 2D position of the icon centre
        :param tags: tags to be displayed as a tooltip
        :param outline: draw outline for the icon
        :param scale: scale icon by the magnitude
        :param color: fill color
        """
        drawer: Drawer = Drawer(shapes)

        if outline:
            bright: bool = is_bright(color)
            opacity = 0.7 if bright else 0.5
            outline_group: Group = Group(opacity=opacity)
            for shape_specification in self.shape_specifications:
                drawer.draw(
                    outline_group,
                    shape_specification,
                    position,
                    tags,
                    outline=True,
                    scale=scale,
                    color=color,
                )
            svg.add(outline_group)
        elif len(self.shape_specifications) > 1 or opacity != 1.0:
            group: Group = Group(opacity=opacity)
            for shape_specification in self.shape_specifications:
                drawer.draw(
                    group,
                    shape_specification,
                    position,
                    tags,
                    scale=scale,
                    color=color,
                )
            svg.add(group)
        else:
            drawer.draw(
                svg,
                self.shape_specifications[0],
                position,
                tags,
                scale=scale,
                color=color,
            )

    def is_sketch(self) -> bool:
        """Check whether icon has sketch shapes."""
        return self.sketch

    def draw_to_file(
        self,
        file_name: Path,
        shapes: Shapes,
        *,
        outline: bool = False,
        outline_opacity: float = 1.0,
    ) -> None:
        """Draw icon to the SVG file.

        :param file_name: output SVG file name
        :param color: fill color
        :param outline: if true, draw outline beneath the icon
        :param outline_opacity: opacity of the outline
        """
        if not outline:
            # If we don't need outline, we draw the icon the simplest way
            # possible.
            with file_name.open("w", encoding="utf-8") as output_file:
                output_file.write(
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'width="16" height="16">'
                )
                for shape_specification in self.shape_specifications:
                    path: str = shapes.get_shape(
                        shape_specification.shape_id
                    ).get_path(
                        shape_specification.version,
                        point=np.array((8.0, 8.0)),
                        offset=shape_specification.offset * 1.0,
                        scale=np.array((1.0, 1.0)),
                    )
                    d = path.get_xml().attrib["d"]
                    output_file.write(f'<path d="{d}" fill="#000" />')
                output_file.write("</svg>")
            return

        svg: Drawing = Drawing(str(file_name), (16, 16))
        drawer: Drawer = Drawer(shapes)

        if outline:
            for shape_specification in self.shape_specifications:
                drawer.draw(
                    svg,
                    shape_specification,
                    position=np.array((8.0, 8.0)),
                    outline=outline,
                    outline_opacity=outline_opacity,
                )

        for shape_specification in self.shape_specifications:
            drawer.draw(svg, shape_specification, np.array((8.0, 8.0)))

        with file_name.open("w", encoding="utf-8") as output_file:
            svg.write(output_file)

    def rasterize(self, svg_file: Path, output_base: Path) -> None:
        """Rasterize icon to PNG."""
        if cairosvg is None:
            return

        sizes = [16, 32]

        for size in sizes:
            output_directory = output_base / str(size)
            output_directory.mkdir(parents=True, exist_ok=True)
            output_file = output_directory / (self.icon_id + ".png")
            cairosvg.svg2png(
                url=str(svg_file),
                write_to=str(output_file),
                output_width=size,
                output_height=size,
            )

    def is_default(self) -> bool:
        """Check whether first shape is default."""
        return (
            len(self.shape_specifications) == 1
            and self.shape_specifications[0].is_default()
        )

    def add_specifications(
        self, specifications: list[ShapeSpecification]
    ) -> None:
        """Add shape specifications to the icon."""
        self.shape_specifications += specifications

    def get_full_id(self) -> str:
        """Get full icon identifier for sorting."""
        return self.group + "_" + self.icon_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Icon):
            return False

        return sorted(self.shape_specifications) == sorted(
            other.shape_specifications
        )

    def __lt__(self, other: Icon) -> bool:
        return self.get_full_id() < other.get_full_id()
