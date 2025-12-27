"""Extract icons from SVG file."""

from __future__ import annotations

import contextlib
import json
import logging
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

try:
    import cairosvg
except ImportError:
    cairosvg = None

from pathlib import Path

import svgwrite
from colour import Color
from svgpathtools import Path as ToolsPath
from svgpathtools import parse_path
from svgwrite import Drawing
from svgwrite.container import Group

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from svgwrite.base import BaseElement
    from svgwrite.path import Path as SVGPath

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

logger: logging.Logger = logging.getLogger(__name__)

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

RELATIVE_TOLERANCE: float = 1e-05
ABSOLUTE_TOLERANCE: float = 1e-08
SVG_TOLERANCE: float = 1e-05


def is_bright(color: Color) -> bool:
    """Check whether color is bright.

    Meaning that the color is bright enough to have black outline instead of
    white.
    """
    return (
        0.2126 * color.red + 0.7152 * color.green + 0.0722 * color.blue
        > 0.78125  # noqa: PLR2004
    )


def allclose(
    a: tuple[float, float],
    b: tuple[float, float],
    rtol: float = RELATIVE_TOLERANCE,
    atol: float = ABSOLUTE_TOLERANCE,
) -> bool:
    """Check if two tuples are element-wise equal within a tolerance."""
    return abs(a[0] - b[0]) <= atol + rtol * abs(b[0]) and abs(
        a[1] - b[1]
    ) <= atol + rtol * abs(b[1])


def round_complex(value: complex, precision: int) -> complex:
    """Round complex number to the given precision."""
    return round(value.real, precision) + round(value.imag, precision) * 1j


@dataclass
class PathOnCanvas:
    """Path on canvas."""

    path: str
    """SVG path commands."""

    offset: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
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
        point: tuple[float, float],
        offset: tuple[float, float],
        scale: tuple[float, float],
        use_transform: bool = False,
    ) -> SVGPath:
        """Get SVG path for the shape.

        :param point: icon position
        :param offset: additional offset
        :param scale: scale resulting image
        :param use_transform: use SVG `translate` method instead of rewriting
            path
        """
        shift: tuple[float, float] = (
            point[0] + offset[0],
            point[1] + offset[1],
        )

        if use_transform:
            path_on_canvas: PathOnCanvas = self.paths[version]
            path: SVGPath = svgwrite.path.Path(d=path_on_canvas.path)
            if not allclose(shift, (0.0, 0.0)):
                path.translate(shift[0], shift[1])
            if not allclose(scale, (1.0, 1.0)):
                path.scale(scale[0], scale[1])
            if not allclose(path_on_canvas.offset, (0.0, 0.0)):
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
            if not allclose(path_on_canvas.offset, (0.0, 0.0)):
                parsed_path = parsed_path.translated(
                    path_on_canvas.offset[0] + path_on_canvas.offset[1] * 1j
                )
            if not allclose(scale, (1.0, 1.0)):
                parsed_path = parsed_path.scaled(scale[0], scale[1])
            if not allclose(shift, (0.0, 0.0)):
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
        and abs(parse_length(style["stroke-width"]) - 0.1) < SVG_TOLERANCE
    )


def check_sketch_stroke_element(style: dict[str, str]) -> bool:
    """Check whether style is black stroke, no fill, 20% opacity."""
    return (
        "fill" in style
        and style["fill"] == "none"
        and style["stroke"] == "#000000"
        and "opacity" in style
        and abs(float(style["opacity"]) - 0.2) < SVG_TOLERANCE
        and (
            "stroke-width" not in style
            or abs(parse_length(style["stroke-width"]) - 0.7) < SVG_TOLERANCE
            or abs(parse_length(style["stroke-width"]) - 1) < SVG_TOLERANCE
            or abs(parse_length(style["stroke-width"]) - 2) < SVG_TOLERANCE
            or abs(parse_length(style["stroke-width"]) - 3) < SVG_TOLERANCE
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


def get_icon_specifications(
    configuration_path: Path,
) -> list[IconSpecification]:
    """Get icons from configuration."""
    icon_specifications: list[IconSpecification] = []
    configuration: dict[str, Any] = {}
    with configuration_path.open() as input_file:
        parse_configuration(json.load(input_file), configuration, "")
    for key, value in configuration.items():
        icon_specifications.append(IconSpecification.from_structure(key, value))
    return icon_specifications


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
        logger.info("Importing shapes from `%s`...", svg_file_name)
        root: Element = ET.parse(svg_file_name).getroot()  # noqa: S314
        self.__parse(root, svg_file_name)

    def add_from_iconscript(self, iconscript_file_name: Path) -> None:
        """Add shapes from iconscript file.

        :param iconscript_file_name: input iconscript file name.
        """
        logger.info("Importing shapes from `%s`...", iconscript_file_name)
        temp_output_directory: Path = Path(tempfile.mkdtemp())

        message: str

        iconscript_path: str | None = shutil.which("iconscript")
        if iconscript_path is None:
            message = "`iconscript` executable not found in `PATH`"
            raise FileNotFoundError(message)

        # TODO(enzet): run `iconscript version` and check it, when this is
        # implemented in iconscript project.

        if not iconscript_file_name.is_file():
            message = f"`{iconscript_file_name}` is not a valid file"
            raise FileNotFoundError(message)

        command: list[str] = [
            iconscript_path,
            str(iconscript_file_name),
            str(temp_output_directory),
        ]
        subprocess.check_call(  # noqa: S603
            command,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        offset: tuple[float, float] = (-8.0, -8.0)

        for svg_file_name in temp_output_directory.glob("*.svg"):
            version: str = "main"
            id_: str = svg_file_name.stem
            if match := VERSION_MATCHER.match(id_):
                version = match.group("version")
                id_ = match.group("id")
            content: str = svg_file_name.read_text()
            root: Element = ET.fromstring(content)  # noqa: S314
            for node in root:
                if node.tag == r"{http://www.w3.org/2000/svg}path":
                    path: str = node.attrib["d"]
                    if id_ in self.shapes:
                        shape: Shape = self.shapes[id_]
                        shape.paths[version] = PathOnCanvas(path, offset=offset)
                    else:
                        self.shapes[id_] = Shape(
                            {version: PathOnCanvas(path, offset=offset)},
                            id_,
                        )
        shutil.rmtree(str(temp_output_directory))

    def add_from_json(self, json_file_name: Path) -> None:
        """Add shapes from JSON file.

        :param json_file_name: input JSON file name with shapes.
        """
        logger.info("Importing shapes from `%s`...", json_file_name)
        with json_file_name.open() as input_file:
            shapes: dict = json.load(input_file)
        for id_, shape in shapes.items():
            self.shapes[id_] = Shape({"main": PathOnCanvas(shape)}, id_)

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

            offset: tuple[float, float] = (
                get_offset(matcher.group(1)),
                get_offset(matcher.group(2)),
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

    def get_shape(self, id_: str) -> Shape | None:
        """Get shape or `None` if there is no shape with such identifier.

        :param id_: string icon identifier
        """
        return self.shapes.get(id_)


@dataclass
class ShapeSpecification:
    """Specification for shape as a part of an icon."""

    shape_id: str
    """Shape identifier."""

    version: str = "main"
    """Shape version."""

    offset: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    """Shape offset."""

    flip_horizontally: bool = False
    """Flip shape horizontally."""

    flip_vertically: bool = False
    """Flip shape vertically."""

    use_outline: bool = True
    """If the shape is supposed to be outlined."""

    color: Color | None = None
    """Fill color."""

    @classmethod
    def from_structure(cls, structure: dict[str, Any]) -> ShapeSpecification:
        """Parse shape specification from structure."""
        offset_value = structure.get("offset", (0.0, 0.0))
        offset_tuple: tuple[float, float] = (
            tuple(offset_value)
            if isinstance(offset_value, (list, tuple))
            else (0.0, 0.0)
        )
        return cls(
            structure["id"],
            structure.get("version", "main"),
            offset_tuple,
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
            and allclose(self.offset, other.offset)
        )

    def __lt__(self, other: ShapeSpecification) -> bool:
        return self.shape_id < other.shape_id

    def draw(
        self,
        svg: BaseElement,
        shapes: Shapes,
        position: tuple[float, float],
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
        scale_vector: tuple[float, float] = (scale, scale)
        if self.flip_vertically:
            scale_vector = (scale, -scale)
        if self.flip_horizontally:
            scale_vector = (-scale, scale)

        if not color:
            color = Color("black")

        point: tuple[float, float] = (
            float(int(position[0])),
            float(int(position[1])),
        )

        shape: Shape | None = shapes.get_shape(self.shape_id)
        if shape is None:
            return

        offset_scaled: tuple[float, float] = (
            self.offset[0] * scale,
            self.offset[1] * scale,
        )
        path: SVGPath = shape.get_path(
            self.version,
            point=point,
            offset=offset_scaled,
            scale=scale_vector,
        )
        path.update({"fill": color.hex})

        if outline and self.use_outline:
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
class IconSpecification:
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
    def from_structure(
        cls, id_: str, structure: dict[str, Any]
    ) -> IconSpecification:
        """Parse icon description from structure."""
        shapes: list[ShapeSpecification]
        if "shapes" in structure:
            shapes = [
                ShapeSpecification.from_structure(x)
                for x in structure["shapes"]
            ]
        else:
            shapes = [ShapeSpecification(id_, "main")]

        icon_specification: IconSpecification = cls(
            id_,
            shapes,
            name=structure["name"],
            sketch=structure.get("sketch", False),
            is_part=structure.get("is_part", False),
        )

        if "unicode" in structure:
            icon_specification.unicode = set(structure["unicode"])

        if "sketch" in structure:
            icon_specification.sketch = structure["sketch"]

        if "keywords" in structure:
            icon_specification.keywords = set(structure["keywords"])

        icon_specification.is_part = structure.get("is_part", False)
        icon_specification.group = structure.get("group", "")

        if "categories" in structure:
            icon_specification.categories = set(structure["categories"])

        if "directed" in structure:
            if structure["directed"] == "right":
                icon_specification.is_right_directed = True
            if structure["directed"] == "left":
                icon_specification.is_right_directed = False

        return icon_specification

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
        position: tuple[float, float],
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
        if outline:
            bright: bool = is_bright(color)
            opacity = 0.7 if bright else 0.5
            outline_group: Group = Group(opacity=opacity)
            for shape_specification in self.shape_specifications:
                shape_specification.draw(
                    outline_group,
                    shapes,
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
                shape_specification.draw(
                    group,
                    shapes,
                    position,
                    tags,
                    scale=scale,
                    color=color,
                )
            svg.add(group)
        else:
            self.shape_specifications[0].draw(
                svg,
                shapes,
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
                    offset_value: tuple[float, float] = (
                        shape_specification.offset[0] * 1.0,
                        shape_specification.offset[1] * 1.0,
                    )
                    path: str = shapes.get_shape(
                        shape_specification.shape_id
                    ).get_path(
                        shape_specification.version,
                        point=(8.0, 8.0),
                        offset=offset_value,
                        scale=(1.0, 1.0),
                    )
                    d = path.get_xml().attrib["d"]
                    output_file.write(f'<path d="{d}" fill="#000" />')
                output_file.write("</svg>")
            return

        svg: Drawing = Drawing(str(file_name), (16, 16))

        if outline:
            for shape_specification in self.shape_specifications:
                shape_specification.draw(
                    svg,
                    shapes,
                    position=(8.0, 8.0),
                    outline=outline,
                    outline_opacity=outline_opacity,
                )

        for shape_specification in self.shape_specifications:
            shape_specification.draw(svg, shapes, (8.0, 8.0))

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
        if not isinstance(other, IconSpecification):
            return False

        return sorted(self.shape_specifications) == sorted(
            other.shape_specifications
        )

    def __lt__(self, other: IconSpecification) -> bool:
        return self.get_full_id() < other.get_full_id()
