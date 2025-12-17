# Röntgen Python Package

Python package __roentgen-icons__ providing access to
[Röntgen](https://enzet.ru/roentgen) SVG icons. Source code is available on
[GitHub](https://github.com/enzet/Roentgen).

Röntgen is a set of monochrome 14 × 14 px pixel-aligned map icons. All icons are
under the [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) license.

## Installation

```bash
pip install roentgen-icons
```

## Usage Example

```python
from roentgen import get_icons, Icons
from pathlib import Path

icons: Icons = get_icons()

icon_identifiers: list[str] = icons.identifiers
path_commands: str = icons.get_path_commands("tree")

icon_path: Path = icons.get_icon_path("tree")
with icon_path.open() as input_file:
    svg_content = input_file.read()
```

## License

All Röntgen icons are licensed under the
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). This means you can
use them for any purpose, but please give the appropriate credit, e.g.:
> Röntgen icons by Sergey Vartanov (CC BY 4.0)
