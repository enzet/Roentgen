"""Build hook to copy data files into the package before building."""

import shutil
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Copy data files from root directory to package directory during build."""

    def initialize(self, _version: str, _build_data: dict) -> None:
        """Copy data/config.json and shapes.json into package before building.

        This ensures these files are included as package-internal data.
        """
        source_directory: Path = Path(self.root)
        package_directory: Path = source_directory / "roentgen"

        shutil.copy2(
            source_directory / "shapes.json", package_directory / "shapes.json"
        )
        shutil.copy2(
            source_directory / "data" / "config.json",
            package_directory / "config.json",
        )
