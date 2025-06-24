# Röntgen

Röntgen is a set of monochrome 14 × 14 px pixel-aligned icons. All icons are
under the [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) license. So,
do whatever you want, but please give the appropriate credit.

Röntgen was created for the [Map Machine](http://github.com/enzet/map-machine)
project to represent different map features from the OpenStreetMap database.
However, it can be easily used for any map project or even for non-map-related
projects. Also, some icons can be used as emoji symbols. Version 0.1 of Röntgen
is used in [iD editor](https://github.com/openstreetmap/iD) for OpenStreetMap.

All icons can be found in the [`icons`](icons) directory, where they are stored
as optimized SVG files. Every icon file is less than 3 KB in size.

<picture>
    <source
        media="(prefers-color-scheme: dark)"
        srcset="https://raw.githubusercontent.com/enzet/Roentgen/main/doc/grid_white.svg">
    <img
        src="https://raw.githubusercontent.com/enzet/Roentgen/main/doc/grid_black.svg"
        alt="Röntgen icons">
</picture>

All icons tend to support a common design style, which is heavily inspired by
[Maki](https://github.com/mapbox/maki),
[Osmic](https://github.com/gmgeo/osmic), and
[Temaki](https://github.com/ideditor/temaki).

Feel free to request new icons via issues on GitHub.

## Design Principles

### Requirements

- Icons must be __monochrome__, meaning they cannot have parts in different
  colors. This ensures they can be recolored without losing their meaning.
- Icons must be __14 × 14 px__ in size (equivalent to 16 × 16 px with one pixel
  padding).

### Recommendations

- Icon parts should be __pixel-aligned__ for better rendering, when it is
  possible.
- Lines should have __rounded caps__ if it doesn't affect shape recognition.

## Icon Generation

The `icons` directory contains generated and optimized SVG icons. They are
generated from sketch SVG files in the [`data`](data) directory by Python
scripts. It is hugely simplifies the process of creating new icons.

To regenerate icons, run

```shell
roentgen icons
```

## OpenStreetMap Tags

Röntgen was created for the [Map Machine](http://github.com/enzet/map-machine),
a rendering engine for OpenStreetMap data and it's primary purpose is to
represent tags of objects from the OpenStreetMap database.

The `data/tags.json` file contains a _possible_ mapping from OpenStreetMap tags
to Röntgen icons.

## License

All Röntgen icons are licensed under the
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). This means, you can
use them for any purpose, but please give the appropriate credit, e.g.:
> Röntgen icons by Sergey Vartanov (CC BY 4.0)
