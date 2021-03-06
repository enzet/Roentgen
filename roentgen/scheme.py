"""
Röntgen drawing scheme.

Author: Sergey Vartanov (me@enzet.ru).
"""
import copy
import yaml

from colour import Color
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union, Tuple

from roentgen.icon import DEFAULT_SHAPE_ID, IconExtractor, Icon

DEFAULT_COLOR: Color = Color("#444444")


@dataclass
class IconSet:
    """
    Node representation: icons and color.
    """
    main_icon: List[Icon]  # list of icons
    extra_icons: List[List[Icon]]  # list of lists of icons
    color: Color  # fill color of all icons
    # tag keys that were processed to create icon set (other
    # tag keys should be displayed by text or ignored)
    processed: Set[str]
    is_default: bool


@dataclass
class LineStyle:
    style: Dict[str, Union[int, float, str]]
    priority: float = 0.0


def is_matched_tag(
        matcher_tag_key: str, matcher_tag_value: str,
        tags: Dict[str, str]) -> bool:
    """
    Check whether element tags contradict tag matcher.

    :param matcher_tag_key: tag key
    :param matcher_tag_value: tag value, tag value list, or "*"
    :param tags: element tags to check
    """
    return (
        matcher_tag_key in tags and
        (matcher_tag_value == "*" or
         isinstance(matcher_tag_value, str) and
         tags[matcher_tag_key] == matcher_tag_value or
         isinstance(matcher_tag_value, list) and
         tags[matcher_tag_key] in matcher_tag_value))


def is_matched(matcher: Dict[str, Any], tags: Dict[str, str]) -> bool:
    """
    Check whether element tags matches tag matcher.

    :param matcher: dictionary with tag keys and values, value lists, or "*"
    :param tags: element tags to match
    """
    matched: bool = True

    for config_tag_key in matcher["tags"]:  # type: str
        tag_matcher = matcher["tags"][config_tag_key]
        if not is_matched_tag(config_tag_key, tag_matcher, tags):
            matched = False
            break

    if "no_tags" in matcher:
        for config_tag_key in matcher["no_tags"]:  # type: str
            tag_matcher = matcher["no_tags"][config_tag_key]
            if is_matched_tag(config_tag_key, tag_matcher, tags):
                matched = False
                break

    return matched


class Scheme:
    """
    Map style.

    Specifies map colors and rules to draw icons for OpenStreetMap tags.
    """
    def __init__(self, file_name: str):
        """
        :param file_name: scheme file name with tags, colors, and tag key
            specification
        """
        with open(file_name) as input_file:
            content: Dict[str, Any] = yaml.load(
                input_file.read(), Loader=yaml.FullLoader)

        self.icons: List[Dict[str, Any]] = content["node_icons"]
        self.ways: List[Dict[str, Any]] = content["ways"]

        self.colors: Dict[str, str] = content["colors"]

        self.area_tags: List[Dict[str, str]] = content["area_tags"]

        self.tags_to_write: List[str] = content["tags_to_write"]
        self.prefix_to_write: List[str] = content["prefix_to_write"]
        self.tags_to_skip: List[str] = content["tags_to_skip"]
        self.prefix_to_skip: List[str] = content["prefix_to_skip"]

        # Storage for created icon sets.
        self.cache: Dict[str, Tuple[IconSet, int]] = {}

    def get_color(self, color: str) -> Color:
        """
        Return color if the color is in scheme, otherwise return default color.

        :param color: input color string representation
        :return: 6-digit color specification with "#"
        """
        if color in self.colors:
            return Color(self.colors[color])
        if color.lower() in self.colors:
            return Color(self.colors[color.lower()])
        try:
            return Color(color)
        except ValueError:
            pass

        return DEFAULT_COLOR

    def is_no_drawable(self, key: str) -> bool:
        """
        Return true if key is specified as no drawable (should not be
        represented on the map as icon set or as text) by the scheme.

        :param key: OpenStreetMap tag key
        """
        if key in self.tags_to_write or key in self.tags_to_skip:
            return True
        for prefix in self.prefix_to_write + self.prefix_to_skip:  # type: str
            if key[:len(prefix) + 1] == f"{prefix}:":
                return True
        return False

    def is_writable(self, key: str) -> bool:
        """
        Return true if key is specified as writable (should be represented on
        the map as text) by the scheme.

        :param key: OpenStreetMap tag key
        """
        if key in self.tags_to_skip:  # type: str
            return False
        if key in self.tags_to_write:  # type: str
            return True
        for prefix in self.prefix_to_write:  # type: str
            if key[:len(prefix) + 1] == f"{prefix}:":
                return True
        return False

    def get_icon(
            self, icon_extractor: IconExtractor, tags: Dict[str, Any],
            for_: str = "node") -> Tuple[IconSet, int]:
        """
        Construct icon set.

        :param tags: OpenStreetMap element tags dictionary
        """
        tags_hash: str = (
            ",".join(tags.keys()) + ":" + ",".join(map(str, tags.values())))

        if tags_hash in self.cache:
            return self.cache[tags_hash]

        main_icon_id: Optional[List[str]] = None
        extra_icon_ids: List[List[str]] = []
        processed: Set[str] = set()
        fill: Color = DEFAULT_COLOR
        priority: int = 0

        for index, matcher in enumerate(self.icons):
            # type: (int, Dict[str, Any])
            matched: bool = is_matched(matcher, tags)
            if not matched:
                continue
            priority = len(self.icons) - index
            if "draw" in matcher and not matcher["draw"]:
                processed |= set(matcher["tags"].keys())
            if "icon" in matcher:
                main_icon_id = copy.deepcopy(matcher["icon"])
                processed |= set(matcher["tags"].keys())
            if "over_icon" in matcher:
                if main_icon_id:  # TODO: check main icon in under icons
                    main_icon_id += matcher["over_icon"]
                    for key in matcher["tags"].keys():
                        processed.add(key)
            if "add_icon" in matcher:
                extra_icon_ids += [matcher["add_icon"]]
                for key in matcher["tags"].keys():
                    processed.add(key)
            if "color" in matcher:
                fill = self.get_color(matcher["color"])
                for key in matcher["tags"].keys():
                    processed.add(key)

        for tag_key in tags:  # type: str
            if (tag_key.endswith(":color") or
                    tag_key.endswith(":colour")):
                fill = self.get_color(tags[tag_key])
                processed.add(tag_key)

        for tag_key in tags:  # type: str
            if tag_key in ["color", "colour"]:
                fill = self.get_color(tags[tag_key])
                processed.add(tag_key)

        keys_left = list(filter(
            lambda x: x not in processed and
            not self.is_no_drawable(x), tags.keys()))

        is_default: bool = False
        if not main_icon_id and not extra_icon_ids and keys_left:
            main_icon_id = [DEFAULT_SHAPE_ID]
            is_default = True

        main_icon: List[Icon] = []
        if main_icon_id:
            main_icon = list(map(
                lambda x: icon_extractor.get_path(x)[0], main_icon_id))

        extra_icons: List[List[Icon]] = []
        for icon_id in extra_icon_ids:
            extra_icons.append(list(map(
                lambda x: icon_extractor.get_path(x)[0], icon_id)))

        returned: IconSet = IconSet(
            main_icon, extra_icons, fill, processed, is_default)

        self.cache[tags_hash] = returned, priority

        return returned, priority

    def get_style(self, tags: Dict[str, Any], scale):

        line_styles = []

        for element in self.ways:  # type: Dict[str, Any]
            priority = 0
            matched: bool = is_matched(element, tags)
            if not matched:
                continue
            style: Dict[str, Any] = {"fill": "none"}
            if "priority" in element:
                priority = element["priority"]
            for key in element:  # type: str
                if key not in [
                        "tags", "no_tags", "priority", "level", "icon",
                        "r", "r2"]:
                    value = element[key]
                    if isinstance(value, str) and value.endswith("_color"):
                        value = self.get_color(value)
                    style[key] = value
            if "r" in element:
                style["stroke-width"] = (element["r"] * scale)
            if "r2" in element:
                style["stroke-width"] = (element["r2"] * scale + 2)

            line_styles.append(LineStyle(style, priority))

        return line_styles

    def is_area(self, tags: Dict[str, str]) -> bool:
        for matcher in self.area_tags:
            if is_matched(matcher, tags):
                return True
        return False
