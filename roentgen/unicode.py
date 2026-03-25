"""Generate HTML table of Unicode symbols mapped to Röntgen icons."""

from __future__ import annotations

import json
import logging
import unicodedata
from pathlib import Path

from roentgen.icon import get_icon_specifications

logger: logging.Logger = logging.getLogger(__name__)

# Emoji codepoint ranges from Unicode 15.1 emoji data
# (https://unicode.org/Public/emoji/15.1/emoji-data.txt)
_EMOJI_RANGES: list[tuple[int, int]] = [
    (0x00A9, 0x00A9),
    (0x00AE, 0x00AE),
    (0x203C, 0x203C),
    (0x2049, 0x2049),
    (0x2122, 0x2122),
    (0x2139, 0x2139),
    (0x2194, 0x2199),
    (0x21A9, 0x21AA),
    (0x231A, 0x231B),
    (0x2328, 0x2328),
    (0x23CF, 0x23CF),
    (0x23E9, 0x23F3),
    (0x23F8, 0x23FA),
    (0x24C2, 0x24C2),
    (0x25AA, 0x25AB),
    (0x25B6, 0x25B6),
    (0x25C0, 0x25C0),
    (0x25FB, 0x25FE),
    (0x2600, 0x2604),
    (0x260E, 0x260E),
    (0x2611, 0x2611),
    (0x2614, 0x2615),
    (0x2618, 0x2618),
    (0x261D, 0x261D),
    (0x2620, 0x2620),
    (0x2622, 0x2623),
    (0x2626, 0x2626),
    (0x262A, 0x262A),
    (0x262E, 0x262F),
    (0x2638, 0x263A),
    (0x2640, 0x2640),
    (0x2642, 0x2642),
    (0x2648, 0x2653),
    (0x265F, 0x2660),
    (0x2663, 0x2663),
    (0x2665, 0x2666),
    (0x2668, 0x2668),
    (0x267B, 0x267B),
    (0x267E, 0x267F),
    (0x2692, 0x2697),
    (0x2699, 0x2699),
    (0x269B, 0x269C),
    (0x26A0, 0x26A1),
    (0x26A7, 0x26A7),
    (0x26AA, 0x26AB),
    (0x26B0, 0x26B1),
    (0x26BD, 0x26BE),
    (0x26C4, 0x26C5),
    (0x26CE, 0x26CF),
    (0x26D1, 0x26D1),
    (0x26D3, 0x26D4),
    (0x26E9, 0x26EA),
    (0x26F0, 0x26F5),
    (0x26F7, 0x26FA),
    (0x26FD, 0x26FD),
    (0x2702, 0x2702),
    (0x2705, 0x2705),
    (0x2708, 0x270D),
    (0x270F, 0x270F),
    (0x2712, 0x2712),
    (0x2714, 0x2714),
    (0x2716, 0x2716),
    (0x271D, 0x271D),
    (0x2721, 0x2721),
    (0x2728, 0x2728),
    (0x2733, 0x2734),
    (0x2744, 0x2744),
    (0x2747, 0x2747),
    (0x274C, 0x274C),
    (0x274E, 0x274E),
    (0x2753, 0x2755),
    (0x2757, 0x2757),
    (0x2763, 0x2764),
    (0x2795, 0x2797),
    (0x27A1, 0x27A1),
    (0x27B0, 0x27B0),
    (0x27BF, 0x27BF),
    (0x2934, 0x2935),
    (0x2B05, 0x2B07),
    (0x2B1B, 0x2B1C),
    (0x2B50, 0x2B50),
    (0x2B55, 0x2B55),
    (0x3030, 0x3030),
    (0x303D, 0x303D),
    (0x3297, 0x3297),
    (0x3299, 0x3299),
    (0x1F004, 0x1F004),
    (0x1F0CF, 0x1F0CF),
    (0x1F170, 0x1F171),
    (0x1F17E, 0x1F17F),
    (0x1F18E, 0x1F18E),
    (0x1F191, 0x1F19A),
    (0x1F201, 0x1F202),
    (0x1F21A, 0x1F21A),
    (0x1F22F, 0x1F22F),
    (0x1F232, 0x1F23A),
    (0x1F250, 0x1F251),
    (0x1F300, 0x1F321),
    (0x1F324, 0x1F393),
    (0x1F396, 0x1F397),
    (0x1F399, 0x1F39B),
    (0x1F39E, 0x1F3F0),
    (0x1F3F3, 0x1F3F5),
    (0x1F3F7, 0x1F4FD),
    (0x1F4FF, 0x1F53D),
    (0x1F549, 0x1F54E),
    (0x1F550, 0x1F567),
    (0x1F56F, 0x1F570),
    (0x1F573, 0x1F57A),
    (0x1F587, 0x1F587),
    (0x1F58A, 0x1F58D),
    (0x1F590, 0x1F590),
    (0x1F595, 0x1F596),
    (0x1F5A4, 0x1F5A5),
    (0x1F5A8, 0x1F5A8),
    (0x1F5B1, 0x1F5B2),
    (0x1F5BC, 0x1F5BC),
    (0x1F5C2, 0x1F5C4),
    (0x1F5D1, 0x1F5D3),
    (0x1F5DC, 0x1F5DE),
    (0x1F5E1, 0x1F5E1),
    (0x1F5E3, 0x1F5E3),
    (0x1F5E8, 0x1F5E8),
    (0x1F5EF, 0x1F5EF),
    (0x1F5F3, 0x1F5F3),
    (0x1F5FA, 0x1F64F),
    (0x1F680, 0x1F6C5),
    (0x1F6CB, 0x1F6D2),
    (0x1F6D5, 0x1F6D7),
    (0x1F6DC, 0x1F6E5),
    (0x1F6E9, 0x1F6E9),
    (0x1F6EB, 0x1F6EC),
    (0x1F6F0, 0x1F6F0),
    (0x1F6F3, 0x1F6FC),
    (0x1F7E0, 0x1F7EB),
    (0x1F7F0, 0x1F7F0),
    (0x1F90C, 0x1F93A),
    (0x1F93C, 0x1F945),
    (0x1F947, 0x1F9FF),
    (0x1FA70, 0x1FA7C),
    (0x1FA80, 0x1FA88),
    (0x1FA90, 0x1FABD),
    (0x1FABF, 0x1FAC5),
    (0x1FACE, 0x1FADB),
]


def _all_emoji_codepoints() -> set[int]:
    """Return the set of all emoji codepoints per the Unicode standard."""
    result: set[int] = set()
    for start, end in _EMOJI_RANGES:
        result.update(range(start, end + 1))
    return result


def get_base_codepoint(char: str) -> int:
    """Return the first codepoint of a (possibly multi-codepoint) character."""
    return ord(char[0])


def generate_unicode_table(
    config_path: Path = Path("data/config.json"),
    icons_dir: Path = Path("icons"),
    icons_sketches_dir: Path = Path("icons_sketches"),
    output_path: Path = Path("out/unicode.html"),
) -> None:
    """Generate an HTML table of Unicode emoji with Röntgen icon overlays.

    All emoji codepoints are shown; rows with no emoji are omitted.  Cells
    that have a matching Röntgen icon also show the icon image.
    """
    with config_path.open(encoding="utf-8") as f:
        config = json.load(f)

    icon_specifications = get_icon_specifications(config)

    # Map row → col → list of (icon_id, icon_name, original unicode char)
    icon_cells: dict[int, dict[int, list[tuple[str, str, str]]]] = {}

    for specification in icon_specifications:
        for char in specification.unicode:
            codepoint = get_base_codepoint(char)
            row, column = codepoint >> 4, codepoint & 0xF
            icon_cells.setdefault(row, {}).setdefault(column, []).append(
                (specification.icon_id, specification.name, char)
            )

    # Build the set of rows that contain at least one emoji codepoint
    all_emoji = _all_emoji_codepoints()
    emoji_rows: set[int] = {cp >> 4 for cp in all_emoji}

    rows_sorted = sorted(emoji_rows)

    lines: list[str] = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '  <meta charset="utf-8">',
        "  <title>Röntgen Unicode table</title>",
        '  <link rel="stylesheet" href="../data/unicode.css">',
        "</head>",
        "<body>",
        "<table>",
        "  <thead>",
        "    <tr>",
        "      <th></th>",
    ]
    lines += [f"      <th>x{col:X}</th>" for col in range(16)]
    lines += ["    </tr>", "  </thead>", "  <tbody>"]

    for row in rows_sorted:
        lines.append("    <tr>")
        lines.append(f"      <td>U+{row:04X}x</td>")
        for col in range(16):
            cp = (row << 4) | col
            char = chr(cp)
            # Check character is assigned
            try:
                unicodedata.name(char)
            except ValueError:
                lines.append("      <td></td>")
                continue

            if cp not in all_emoji:
                lines.append("      <td></td>")
                continue

            icon_entries = icon_cells.get(row, {}).get(col, [])
            parts: list[str] = ['<div class="cell">']

            if icon_entries:
                for icon_id, icon_name, original_char in icon_entries:
                    unicode_name = unicodedata.name(original_char[0], "")
                    parts.append(
                        f'  <span class="symbol" title="{unicode_name}">'
                        f"{original_char}</span>"
                    )
                    svg_path = icons_dir / f"{icon_id}.svg"
                    sketch_path = icons_sketches_dir / f"{icon_id}.svg"
                    if svg_path.exists():
                        parts.append(
                            f'  <img src="../{svg_path}" alt="{icon_id}"'
                            f' title="{icon_name}">'
                        )
                    elif sketch_path.exists():
                        parts.append(
                            f'  <img src="../{sketch_path}" alt="{icon_id}"'
                            f' title="{icon_name} (sketch)">'
                        )
            else:
                unicode_name = unicodedata.name(char, "")
                parts.append(
                    f'  <span class="no-icon" title="{unicode_name}">'
                    f"{char}</span>"
                )

            parts.append("</div>")
            lines.append(f"      <td>{''.join(parts)}</td>")

        lines.append("    </tr>")

    lines += ["  </tbody>", "</table>", "</body>", "</html>"]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Written %s.", output_path)


if __name__ == "__main__":
    generate_unicode_table()
