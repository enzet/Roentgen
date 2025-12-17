"""Build hook to copy icons into the package before building."""  # noqa: INP001

import shutil
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Copy icons from parent directory to package directory during build."""

    def initialize(self, _version: str, _build_data: dict) -> None:
        """Copy icons directory into the package before building.

        This ensures icons are included as package-internal data.
        """
        source_directory: Path = Path(self.root)
        icons_source: Path = source_directory.parent / "icons"
        icons_destination: Path = source_directory / "roentgen" / "icons"

        if icons_source.exists() and icons_source.is_dir():
            if icons_destination.exists():
                shutil.rmtree(icons_destination)
            shutil.copytree(icons_source, icons_destination)
