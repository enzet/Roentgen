from pathlib import Path

from generator.icon_collection import draw_icons


def main(root_path, icons_path, icons_config_path, output_path):
    draw_icons(root_path, icons_path, icons_config_path, output_path)


if __name__ == "__main__":
    main(
        Path("."),
        Path("data") / "icons.svg",
        Path("data") / "config.json",
        Path("."),
    )
