"""Röntgen icons package.

This package provides access to Röntgen SVG icons.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from xml.etree import ElementTree as ET

__version__ = "0.9.0"


class Icons:
    """Container for all Röntgen icons.

    Icons are loaded once on initialization. Each icon has an identifier (name)
    and SVG path commands.
    """

    def __init__(self) -> None:
        """Initialize and load all icons."""
        self._icons_path: Path = self._get_icons_path()
        self._identifiers: list[str] = []
        self._path_commands: dict[str, str] = {}
        self._load_icons()

    def _get_icons_path(self) -> Path:
        """Get the path to the icons directory.

        :returns: path to the icons directory where SVG files are located
        """
        try:
            icons_reference: Path = resources.files("roentgen") / "icons"
            if icons_reference.is_dir():
                return Path(str(icons_reference))
        except (ModuleNotFoundError, TypeError):
            pass
        return Path(__file__).parent.parent.parent / "icons"

    def _load_icons(self) -> None:
        """Load all icons from the icons directory."""
        if not self._icons_path.exists():
            return

        for icon_file in sorted(self._icons_path.glob("*.svg")):
            if not icon_file.is_file():
                continue

            icon_name: str = icon_file.stem
            self._identifiers.append(icon_name)

            try:
                path_commands: str = self._extract_path_commands(icon_file)
                self._path_commands[icon_name] = path_commands
            except Exception:  # noqa: BLE001
                # Skip icons that can't be parsed.
                self._path_commands[icon_name] = ""

    def _extract_path_commands(self, svg_file: Path) -> str:
        """Extract path commands from SVG file.

        :param svg_file: path to SVG file
        :returns: path commands (d attribute value)
        """
        tree: ET.ElementTree = ET.parse(svg_file)  # noqa: S314
        root: ET.Element = tree.getroot()

        # Find all path elements and concatenate their d attributes
        path_commands: list[str] = []
        for path_element in root.findall(".//{http://www.w3.org/2000/svg}path"):
            d_attribute: str | None = path_element.get("d")
            if d_attribute:
                path_commands.append(d_attribute)

        # Also check for path elements without namespace
        for path_element in root.findall(".//path"):
            d_attribute: str | None = path_element.get("d")
            if d_attribute:
                path_commands.append(d_attribute)

        return " ".join(path_commands)

    def get_path_commands(self, icon_name: str) -> str:
        """Get SVG path commands for an icon.

        :param icon_name: name of the icon (without .svg extension)
        :returns: SVG path commands (d attribute value)
        :raises KeyError: if the icon does not exist
        """
        if icon_name not in self._path_commands:
            message: str = f"Icon `{icon_name}` not found."
            raise KeyError(message)
        return self._path_commands[icon_name]

    def get_icon_path(self, icon_name: str) -> Path:
        """Get the path to a specific icon file.

        :param icon_name: name of the icon (without .svg extension)
        :returns: path to the icon SVG file
        :raises FileNotFoundError: if the icon file does not exist
        """
        icon_path: Path = self._icons_path / f"{icon_name}.svg"
        if not icon_path.exists():
            message: str = (
                f"Icon `{icon_name}` not found in `{self._icons_path}`."
            )
            raise FileNotFoundError(message)
        return icon_path

    @property
    def identifiers(self) -> list[str]:
        """Get all icon identifiers.

        :returns: list of icon identifiers
        """
        return self._identifiers.copy()

    @property
    def path_commands(self) -> dict[str, str]:
        """Get all icon path commands.

        :returns: dictionary mapping icon identifiers to SVG path commands
        """
        return self._path_commands.copy()


# Create a global instance
_icons_instance: Icons | None = None


def get_icons() -> Icons:
    """Get the global Icons instance.

    :returns: Icons instance with all icons loaded
    """
    global _icons_instance  # noqa: PLW0603
    if _icons_instance is None:
        _icons_instance = Icons()
    return _icons_instance
