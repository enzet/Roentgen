# Röntgen

Röntgen is a set of monochrome 14 × 14 px pixel-aligned icons. All icons are
under the [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) license. So,
do whatever you want, but please give the appropriate credit.

Röntgen was created for the [Map Machine](http://github.com/enzet/map-machine)
project to represent different map features from the OpenStreetMap database.
However, it can be easily used for any map project or even for non-map-related
projects. Also, some icons can be used as emoji symbols.

All icons can be found in the [`icons`](icons) directory, where they are stored
as optimized SVG files. We distinguish between _shape_ and _icon_. Most icons
are single-shaped (e.g. `tree.svg`), some are combinations of multiple shapes
(e.g. `volcanic_cone___lava.svg`, where shape identifiers are separated by
`___`).

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

- Icon parts should be __pixel-aligned__ for better rendering.
- Icons should __avoid perspective__ when possible.
- Lines should have __rounded caps__ if it doesn't affect shape recognition.

Individual icons should be in the form of a single SVG `path` element. Icon
combinations are combinations of individual icons.

## Generation

Röntgen icons may be drawn by hand in a vector editor and stored as optimized
SVG files, but the project also has one more option for icon extraction.

### Extraction from the Monolith SVG File

To generate icons, run

```shell
roentgen generate
```

It may be useful to have one SVG file for a set of SVG icons along with sketches
and components that the icons consist of.

In the Röntgen project, these files are located in the [`data`](data) directory.
