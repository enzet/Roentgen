"""
Simple OpenStreetMap renderer.

Author: Sergey Vartanov (me@enzet.ru).
"""
import argparse

import numpy as np
import os
import svgwrite
import sys

from colour import Color
from svgwrite.container import Group
from svgwrite.path import Path
from svgwrite.shapes import Rect
from typing import Any, Dict, List

from roentgen import ui
from roentgen.constructor import (
    Constructor, Figure, Building, Segment)
from roentgen.point import Point, Occupied
from roentgen.flinger import Flinger
from roentgen.grid import draw_all_icons
from roentgen.icon import Icon, IconExtractor
from roentgen.osm_getter import get_osm
from roentgen.osm_reader import Map, OSMReader, OverpassReader
from roentgen.scheme import Scheme
from roentgen.direction import DirectionSet, Sector
from roentgen.util import MinMax

ICONS_FILE_NAME: str = "icons/icons.svg"
TAGS_FILE_NAME: str = "data/tags.yml"
MISSING_TAGS_FILE_NAME: str = "missing_tags.yml"

AUTHOR_MODE = "user-coloring"
CREATION_TIME_MODE = "time"


class Painter:
    """
    Map drawing.
    """

    def __init__(
            self, show_missing_tags: bool, overlap: int, draw_nodes: bool,
            mode: str, draw_captions: str, map_: Map, flinger: Flinger,
            svg: svgwrite.Drawing, icon_extractor: IconExtractor,
            scheme: Scheme):

        self.show_missing_tags: bool = show_missing_tags
        self.overlap: int = overlap
        self.draw_nodes: bool = draw_nodes
        self.mode: str = mode
        self.draw_captions: str = draw_captions

        self.map_: Map = map_
        self.flinger: Flinger = flinger
        self.svg: svgwrite.Drawing = svg
        self.icon_extractor = icon_extractor
        self.scheme: Scheme = scheme

    def draw(self, constructor: Constructor):
        """
        Draw map.
        """
        ways = sorted(constructor.figures, key=lambda x: x.line_style.priority)
        ways_length: int = len(ways)
        for index, way in enumerate(ways):  # type: Figure
            ui.progress_bar(index, ways_length, step=10, text="Drawing ways")
            path_commands: str = way.get_path(self.flinger)
            if path_commands:
                path = Path(d=path_commands)
                path.update(way.line_style.style)
                self.svg.add(path)
        ui.progress_bar(-1, 0, text="Drawing ways")

        # Trees

        for node in constructor.nodes:
            if not (node.get_tag("natural") == "tree" and
                    ("diameter_crown" in node.tags or
                     "circumference" in node.tags)):
                continue
            if "circumference" in node.tags:
                if "diameter_crown" in node.tags:
                    opacity = 0.7
                    radius = float(node.tags["diameter_crown"]) / 2
                else:
                    opacity = 0.3
                    radius = 2
                self.svg.add(self.svg.circle(
                    node.point,
                    radius * self.flinger.get_scale(node.coordinates),
                    fill=self.scheme.get_color("evergreen_color"),
                    opacity=opacity))
                self.svg.add(self.svg.circle(
                    node.point,
                    float(node.tags["circumference"]) / 2 / np.pi *
                    self.flinger.get_scale(node.coordinates),
                    fill="#B89A74"))

        # Draw building shade.

        building_shade: Group = Group(opacity=0.1)
        length: float = self.flinger.get_scale()

        for way in constructor.buildings:  # type: Building
            shift = np.array((length * way.get_levels(), 0))
            for nodes11 in way.inners + way.outers:
                for i in range(len(nodes11) - 1):  # type: int
                    flung_1 = self.flinger.fling(nodes11[i].coordinates)
                    flung_2 = self.flinger.fling(nodes11[i + 1].coordinates)
                    building_shade.add(Path(
                        ("M", flung_1, "L", flung_2, np.add(flung_2, shift),
                         np.add(flung_1, shift), "Z"),
                        fill="#000000", stroke="#000000", stroke_width=1))

        self.svg.add(building_shade)

        # Draw buildings.

        previous_level: float = 0
        level_height: float = self.flinger.get_scale()
        level_count: int = len(constructor.levels)

        for index, level in enumerate(sorted(constructor.levels)):
            ui.progress_bar(
                index, level_count, step=1, text="Drawing buildings")
            fill: Color()
            for way in constructor.buildings:  # type: Building
                if way.get_levels() < level:
                    continue
                shift_1 = [0, -previous_level * level_height]
                shift_2 = [0, -level * level_height]
                for segment in way.parts:  # type: Segment
                    if level == 0.5:
                        fill = Color("#AAAAAA")
                    elif level == 1:
                        fill = Color("#C3C3C3")
                    else:
                        color_part: float = 0.8 + segment.angle * 0.2
                        fill = Color(rgb=(color_part, color_part, color_part))

                    self.svg.add(self.svg.path(
                        d=("M", segment.point_1 + shift_1, "L",
                           segment.point_2 + shift_1,
                           segment.point_2 + shift_2,
                           segment.point_1 + shift_2,
                           segment.point_1 + shift_1, "Z"),
                        fill=fill.hex, stroke=fill.hex, stroke_width=1,
                        stroke_linejoin="round"))

            # Draw building roofs.

            for way in constructor.buildings:  # type: Building
                if way.get_levels() == level:
                    shift = np.array([0, -way.get_levels() * level_height])
                    path_commands: str = way.get_path(self.flinger, shift)
                    path = Path(d=path_commands, opacity=1)
                    path.update(way.line_style.style)
                    path.update({"stroke-linejoin": "round"})
                    self.svg.add(path)

            previous_level = level

        ui.progress_bar(-1, level_count, step=1, text="Drawing buildings")

        # Directions

        for node in constructor.nodes:  # type: Point

            angle = None
            is_revert_gradient: bool = False

            if node.get_tag("man_made") == "surveillance":
                direction = node.get_tag("camera:direction")
                if "camera:angle" in node.tags:
                    angle = float(node.get_tag("camera:angle"))
                if "angle" in node.tags:
                    angle = float(node.get_tag("angle"))
                direction_radius: float = (
                    25 * self.flinger.get_scale(node.coordinates))
                direction_color: Color = (
                    self.scheme.get_color("direction_camera_color"))
            elif node.get_tag("traffic_sign") == "stop":
                direction = node.get_tag("direction")
                direction_radius: float = (
                    25 * self.flinger.get_scale(node.coordinates))
                direction_color: Color = Color("red")
            else:
                direction = node.get_tag("direction")
                direction_radius: float = (
                    50 * self.flinger.get_scale(node.coordinates))
                direction_color: Color = (
                    self.scheme.get_color("direction_view_color"))
                is_revert_gradient = True

            if not direction:
                continue

            point = (node.point.astype(int)).astype(float)

            if angle:
                paths = [Sector(direction, angle).draw(point, direction_radius)]
            else:
                paths = DirectionSet(direction).draw(point, direction_radius)

            for path in paths:
                gradient = self.svg.defs.add(self.svg.radialGradient(
                    center=point, r=direction_radius,
                    gradientUnits="userSpaceOnUse"))
                if is_revert_gradient:
                    gradient \
                        .add_stop_color(0, direction_color.hex, opacity=0) \
                        .add_stop_color(1, direction_color.hex, opacity=0.7)
                else:
                    gradient \
                        .add_stop_color(0, direction_color.hex, opacity=0.4) \
                        .add_stop_color(1, direction_color.hex, opacity=0)
                self.svg.add(self.svg.path(
                    d=["M", point] + path + ["L", point, "Z"],
                    fill=gradient.get_paint_server()))

        # All other points

        if self.overlap == 0:
            occupied = None
        else:
            occupied = Occupied(
                self.flinger.size[0], self.flinger.size[1], self.overlap)

        nodes = sorted(constructor.nodes, key=lambda x: -x.priority)
        for index, node in enumerate(nodes):  # type: int, Point
            if (node.get_tag("natural") == "tree" and
                    ("diameter_crown" in node.tags or
                     "circumference" in node.tags)):
                continue
            ui.progress_bar(index, len(nodes), step=10, text="Drawing nodes")
            node.draw_shapes(self.svg, occupied)
        ui.progress_bar(-1, len(nodes), step=10, text="Drawing nodes")

        if self.draw_captions == "no":
            return

        for node in nodes:  # type: Point
            if self.mode not in [CREATION_TIME_MODE, AUTHOR_MODE]:
                node.draw_texts(
                    self.svg, self.scheme, occupied, self.draw_captions)


def check_level_number(tags: Dict[str, Any], level: float):
    """
    Check if element described by tags is no the specified level.
    """
    if "level" in tags:
        levels = map(float, tags["level"].replace(",", ".").split(";"))
        if level not in levels:
            return False
    else:
        return False
    return True


def check_level_overground(tags: Dict[str, Any]) -> bool:
    """
    Check if element described by tags is overground.
    """
    if "level" in tags:
        try:
            levels = map(float, tags["level"].replace(",", ".").split(";"))
            for level in levels:
                if level <= 0:
                    return False
        except ValueError:
            pass
    if "layer" in tags:
        try:
            levels = map(float, tags["layer"].replace(",", ".").split(";"))
            for level in levels:
                if level <= 0:
                    return False
        except ValueError:
            pass
    if "parking" in tags and tags["parking"] == "underground":
        return False
    return True


def main(argv) -> None:
    """
    R??ntgen entry point.

    :param argv: command-line arguments
    """
    if len(argv) == 2:
        if argv[1] == "grid":
            draw_all_icons("icon_grid.svg")
        return

    options: argparse.Namespace = ui.parse_options(argv)

    if not options:
        sys.exit(1)

    background_color: Color = Color("#EEEEEE")
    if options.mode in [AUTHOR_MODE, CREATION_TIME_MODE]:
        background_color: Color = Color("#111111")

    if options.input_file_name:
        input_file_name = options.input_file_name
    else:
        content = get_osm(options.boundary_box)
        if not content:
            ui.error("cannot download OSM data")
        input_file_name = [os.path.join("map", options.boundary_box + ".osm")]

    scheme: Scheme = Scheme(TAGS_FILE_NAME)

    if input_file_name[0].endswith(".json"):
        reader: OverpassReader = OverpassReader()
        reader.parse_json_file(input_file_name[0])
        map_ = reader.map_
        min1 = np.array((map_.boundary_box[0].min_, map_.boundary_box[1].min_))
        max1 = np.array((map_.boundary_box[0].max_, map_.boundary_box[1].max_))
    else:

        boundary_box = list(map(
            lambda x: float(x.replace('m', '-')), options.boundary_box.split(',')))

        full = False  # Full keys getting

        if options.mode in [AUTHOR_MODE, CREATION_TIME_MODE]:
            full = True

        osm_reader = OSMReader()

        for file_name in input_file_name:
            if not os.path.isfile(file_name):
                print("Fatal: no such file: " + file_name + ".")
                sys.exit(1)

            osm_reader.parse_osm_file(
                file_name, parse_ways=options.draw_ways,
                parse_relations=options.draw_ways, full=full)

        map_: Map = osm_reader.map_

        min1: np.array = np.array((boundary_box[1], boundary_box[0]))
        max1: np.array = np.array((boundary_box[3], boundary_box[2]))

    flinger: Flinger = Flinger(MinMax(min1, max1), options.scale)
    size: np.array = flinger.size

    svg: svgwrite.Drawing = (
        svgwrite.Drawing(options.output_file_name, size=size))
    svg.add(Rect((0, 0), size, fill=background_color))

    icon_extractor: IconExtractor = IconExtractor(ICONS_FILE_NAME)

    def check_level(x) -> bool:
        """ Draw objects on all levels. """
        return True

    if options.level:
        if options.level == "overground":
            check_level = check_level_overground
        elif options.level == "underground":
            def check_level(x) -> bool:
                """ Draw underground objects. """
                return not check_level_overground(x)
        else:
            def check_level(x) -> bool:
                """ Draw objects on the specified level. """
                return not check_level_number(x, float(options.level))

    constructor: Constructor = Constructor(
        check_level, options.mode, options.seed, map_, flinger, scheme,
        icon_extractor)
    if options.draw_ways:
        constructor.construct_ways()
        constructor.construct_relations()
    if options.mode not in [AUTHOR_MODE, CREATION_TIME_MODE]:
        constructor.construct_nodes()

    painter: Painter = Painter(
        show_missing_tags=options.show_missing_tags, overlap=options.overlap,
        draw_nodes=options.draw_nodes, mode=options.mode,
        draw_captions=options.draw_captions,
        map_=map_, flinger=flinger, svg=svg, icon_extractor=icon_extractor,
        scheme=scheme)

    painter.draw(constructor)

    print("Writing output SVG...")
    svg.write(open(options.output_file_name, "w"))
    print("Done.")
