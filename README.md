# Röntgen

Röntgen is a set of monochrome 14 × 14 px pixel-aligned icons. All icons are
under the [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) license. You
can use them freely, but please give the appropriate credit.

Röntgen was created for the [Map Machine](http://github.com/enzet/map-machine)
project to represent different map features from the OpenStreetMap database.
However, it can be easily used for any map project or even for non-map-related
projects. Some icons can also be used as emoji symbols. Version 0.1 of Röntgen
is used in [iD editor](https://github.com/openstreetmap/iD) for OpenStreetMap.

To use the icons, you can
  - browse and download them from the
    [Röntgen website](https://enzet.ru/roentgen),
  - [use](#npm-package) the npm package
    [@enzet/roentgen](https://www.npmjs.com/package/@enzet/roentgen):
    `npm i @enzet/roentgen`,
  - [use](#pypi-package) the PyPI package
    [roentgen-icons](https://pypi.org/project/roentgen-icons/):
    `pip install roentgen-icons`,
  - download them from the [`icons`](icons) directory,
  - download the release ZIP file from
    [GitHub Releases](https://github.com/enzet/Roentgen/releases).

All icons are stored as optimized SVG files. The majority of them contain only
one path element with a minimal number of points. File sizes range from 207
bytes to 4 KB, with mean and median sizes of about 1 KB.

<picture>
    <source
        media="(prefers-color-scheme: dark)"
        srcset="https://raw.githubusercontent.com/enzet/Roentgen/main/doc/grid_white.svg">
    <img
        src="https://raw.githubusercontent.com/enzet/Roentgen/main/doc/grid_black.svg"
        alt="Röntgen icons">
</picture>

All icons tend to follow a common design style, which is heavily inspired by
[Maki](https://github.com/mapbox/maki),
[Osmic](https://github.com/gmgeo/osmic), and
[Temaki](https://github.com/ideditor/temaki).

Feel free to request new icons via issues on GitHub.

## Installation

### npm Package

Röntgen is available as an npm package:

```bash
npm install @enzet/roentgen
```

After installation, you can use SVG files directly:

```javascript
import treeIcon from '@enzet/roentgen/icons/tree.svg';
```

Or use them in HTML:

```html
<img src="node_modules/@enzet/roentgen/icons/tree.svg" alt="Tree icon" />
```

### PyPI Package

Röntgen is available as a PyPI package:

```bash
pip install roentgen-icons
```

After installation, you can use the icons in your Python code:

```python
from roentgen import get_roentgen, Roentgen
from svgwrite.path import Path

instance: Roentgen = get_roentgen()

shape: Shape | None = instance.get_shape("tree")
if shape is not None:
    svg_path: Path = shape.get_svg_path()
    path_commands: str = shape.get_path_commands()
```

## Design Principles

### Requirements

- Icons must be __monochrome__, meaning they cannot have parts in different
  colors. This ensures they can be recolored without losing their meaning.
- Icons must be __14 × 14 px__ in size (equivalent to 16 × 16 px with one pixel
  padding).

### Recommendations

- Icon parts should be __pixel-aligned__ for better rendering, when possible.
- Lines should have __rounded caps__ if it doesn't affect shape recognition.

## Icon Generation

The `icons` directory contains generated and optimized SVG icons.
Some of the icons are described with
[iconscript](https://github.com/enzet/iconscript) files in the
[`iconscript`](iconscript) directory. Others are generated from sketch SVG files
in the [`data`](data) directory by Python scripts. This hugely simplifies the
process of creating new icons.

To regenerate icons, run

```shell
roentgen icons
```

## OpenStreetMap Tags

Röntgen was created for the [Map Machine](http://github.com/enzet/map-machine),
a rendering engine for OpenStreetMap data, and its primary purpose is to
represent tags of objects from the OpenStreetMap database.

The `data/tags.json` file contains a _possible_ mapping from OpenStreetMap tags
to Röntgen icons.

## License

All Röntgen icons are licensed under the
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). This means you can
use them for any purpose, but please give the appropriate credit, e.g.:
> Röntgen icons by Sergey Vartanov (CC BY 4.0)
