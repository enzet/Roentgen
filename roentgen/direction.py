"""
Direction tag support.

Author: Sergey Vartanov (me@enzet.ru).
"""
from typing import Iterator, List, Optional, Union

import numpy as np
from portolan import middle

Path = Union[float, str, np.array]

SHIFT: float = -np.pi / 2
SMALLEST_ANGLE: float = np.pi / 15
DEFAULT_ANGLE: float = np.pi / 30


def degree_to_radian(degree: float) -> float:
    """ Convert value in degrees to radians. """
    return degree / 180 * np.pi


def parse_vector(text: str) -> Optional[np.array]:
    """
    Parse vector from text representation: compass points or 360-degree
    notation.  E.g. "NW", "270".

    :param text: vector text representation
    :return: parsed normalized vector
    """
    try:
        radians: float = degree_to_radian(float(text)) + SHIFT
        return np.array((np.cos(radians), np.sin(radians)))
    except ValueError:
        pass

    try:
        radians: float = degree_to_radian(middle(text)) + SHIFT
        return np.array((np.cos(radians), np.sin(radians)))
    except KeyError:
        pass

    return None


def rotation_matrix(angle) -> np.array:
    """
    Get a matrix to rotate 2D vector by the angle.

    :param angle: angle in radians
    """
    return np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]])


class Sector:
    """
    Sector described by two vectors.
    """

    def __init__(self, text: str, angle: Optional[float] = None):
        """
        :param text: sector text representation.  E.g. "70-210", "N-NW"
        :param angle: angle in degrees
        """
        self.start: Optional[np.array] = None
        self.end: Optional[np.array] = None

        if "-" in text:
            parts: List[str] = text.split("-")
            self.start = parse_vector(parts[0])
            self.end = parse_vector(parts[1])
        else:
            if angle is None:
                angle = DEFAULT_ANGLE
            else:
                angle = degree_to_radian(angle) / 2
                angle = max(SMALLEST_ANGLE, angle)

            vector: Optional[np.array] = parse_vector(text)

            if vector is not None:
                self.start = np.dot(rotation_matrix(angle), vector)
                self.end = np.dot(rotation_matrix(-angle), vector)

    def draw(self, center: np.array, radius: float) -> Optional[List[Path]]:
        """
        Construct SVG path commands for arc element.

        :param center: arc center point
        :param radius: arc radius
        :return: SVG path commands
        """
        if self.start is None or self.end is None:
            return None

        start: np.array = center + radius * self.end
        end: np.array = center + radius * self.start

        return ["L", start, "A", radius, radius, 0, "0", 0, end]

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"


class DirectionSet:
    """
    Describes direction, set of directions.
    """

    def __init__(self, text: str):
        """
        :param text: direction tag value
        """
        self.sectors: Iterator[Optional[Sector]] = map(Sector, text.split(";"))

    def __str__(self) -> str:
        return ", ".join(map(str, self.sectors))

    def draw(self, center: np.array, radius: float) -> Iterator[List[Path]]:
        """
        Construct SVG "d" for arc elements.

        :param center: center point of all arcs
        :param radius: radius of all arcs
        :return: list of "d" values
        """
        return filter(
            lambda x: x is not None,
            map(lambda x: x.draw(center, radius), self.sectors))
