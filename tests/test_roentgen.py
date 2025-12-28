"""Tests for the main Roentgen API."""

from __future__ import annotations

import tempfile
from pathlib import Path

from colour import Color
from svgwrite import Drawing
from svgwrite.path import Path as SVGPath

from roentgen import Roentgen, get_roentgen
from roentgen.icon import ShapeSpecification


class TestRoentgen:
    """Test the Roentgen class."""

    def test_initialization(self) -> None:
        """Test that Roentgen can be initialized."""
        roentgen = Roentgen()
        assert roentgen is not None
        assert roentgen.shapes is not None
        assert roentgen.icon_specifications is not None
        assert roentgen.config is not None

    def test_get_shapes(self) -> None:
        """Test getting shapes from Roentgen instance."""
        roentgen = Roentgen()
        shapes = roentgen.get_shapes()
        assert shapes is not None
        assert hasattr(shapes, "shapes")

    def test_get_shape_existing(self) -> None:
        """Test getting an existing shape by ID."""
        roentgen = Roentgen()
        shapes = roentgen.get_shapes()
        if shapes.shapes:
            # Get the first available shape ID.
            shape_id = next(iter(shapes.shapes.keys()))
            shape = roentgen.get_shape(shape_id)
            assert shape is not None

    def test_get_shape_tree(self) -> None:
        """Test getting the tree shape."""
        roentgen = Roentgen()
        shape = roentgen.get_shape("tree")
        assert shape is not None
        assert shape.id_ == "tree"
        assert shape.paths is not None
        assert len(shape.paths) > 0
        assert "main" in shape.paths

    def test_get_shape_nonexistent(self) -> None:
        """Test getting a non-existent shape returns None."""
        roentgen = Roentgen()
        shape = roentgen.get_shape("nonexistent_shape_id_12345")
        assert shape is None

    def test_icon_specifications_not_empty(self) -> None:
        """Test that icon specifications are loaded."""
        roentgen = Roentgen()
        assert len(roentgen.icon_specifications) > 0


class TestPathCommandsRoentgen:
    """Test the methods of the Roentgen class."""

    def test_svg_path(self) -> None:
        """Test getting shapes from Roentgen instance."""
        roentgen = Roentgen()
        shape = roentgen.get_shape("tree")
        svg_path: SVGPath = shape.get_svg_path()
        assert svg_path is not None
        assert isinstance(svg_path, SVGPath)

    def test_path_commands(self) -> None:
        """Test getting path commands from SVG path."""
        roentgen = Roentgen()
        shape = roentgen.get_shape("tree")
        path_commands: str = shape.get_path_commands()
        assert path_commands is not None
        assert path_commands != ""


class TestDrawingRoentgen:
    """Test the drawing of Roentgen icons."""

    def test_drawing(self) -> None:
        """Test drawing a Roentgen icon."""
        roentgen = Roentgen()
        shape_specification: ShapeSpecification = ShapeSpecification(
            shape_id="tree",
            version="main",
            offset=(0.0, 0.0),
            flip_horizontally=False,
            flip_vertically=False,
            use_outline=True,
            color=Color("red"),
        )
        temp_file_name: Path = Path(tempfile.mkdtemp()) / "test.svg"
        drawing: Drawing = Drawing(str(temp_file_name), (16, 16))
        shape_specification.draw(drawing, roentgen.shapes, (0.0, 0.0))
        drawing.save(str(temp_file_name))

        with temp_file_name.open("r", encoding="utf-8") as file:
            content: str = file.read()

        assert content.find("<path d=") != -1


class TestGetRoentgen:
    """Test the get_roentgen function."""

    def test_get_roentgen_returns_instance(self) -> None:
        """Test that get_roentgen returns a Roentgen instance."""
        roentgen = get_roentgen()
        assert isinstance(roentgen, Roentgen)

    def test_get_roentgen_singleton(self) -> None:
        """Test that get_roentgen returns the same instance (singleton)."""
        roentgen1 = get_roentgen()
        roentgen2 = get_roentgen()
        assert roentgen1 is roentgen2

    def test_get_roentgen_has_icons(self) -> None:
        """Test that the singleton instance has icons loaded."""
        roentgen = get_roentgen()
        assert len(roentgen.icon_specifications) > 0
        assert roentgen.shapes is not None
