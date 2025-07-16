"""Collections to HTML converter.

This script processes the collections.json file and generates HTML tables with
icons for specified rows and columns, similar to the taginfo.py functionality.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lxml import etree, html

logger = logging.getLogger(__name__)


@dataclass
class CollectionItem:
    """A single collection item."""

    name: str | None
    page: str | None
    id: str | None
    tags: dict[str, str]
    row_key: str | None = None
    row_values: list[str] | None = None
    column_key: str | None = None
    column_values: list[str] | None = None
    row_tags: list[dict[str, str]] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CollectionItem:
        """Create a CollectionItem from a dictionary."""
        return cls(
            name=data.get("name"),
            page=data.get("page"),
            id=data.get("id"),
            tags=data.get("tags", {}),
            row_key=data.get("row_key"),
            row_values=data.get("row_values"),
            column_key=data.get("column_key"),
            column_values=data.get("column_values"),
            row_tags=data.get("row_tags"),
        )

    def get_table_data(
        self,
    ) -> tuple[list[str], list[str], list[list[dict[str, str]]]]:
        """Get table data for 2D tables (with both row and column keys)."""
        if not (
            self.row_key
            and self.row_values
            and self.column_key
            and self.column_values
        ):
            return [], [], []

        rows = self.row_values
        columns = self.column_values
        table_data = []

        for row_value in rows:
            row_data = []
            for col_value in columns:
                combination = self.tags.copy()
                combination[self.row_key] = row_value
                combination[self.column_key] = col_value
                row_data.append(combination)
            table_data.append(row_data)

        return rows, columns, table_data


def descriptor_to_tags(descriptor: str) -> dict[str, str]:
    """Convert a descriptor string to a dictionary of tags."""
    raw_parts: list[str] = descriptor.split(";")
    parts: list[str] = []
    for raw_part in raw_parts:
        if "=" in raw_part:
            parts.append(raw_part)
        else:
            parts[-1] += f";{raw_part}"

    return {part.split("=")[0]: part.split("=")[1] for part in parts}


def match_tags(pattern: str, tags: dict[str, str]) -> bool:
    """Check if a pattern matches a dictionary of tags."""

    pattern_tags: dict[str, str] = descriptor_to_tags(pattern)

    for key, value in pattern_tags.items():
        if key not in tags or tags[key] != value:
            return False

    return True


def get_shapes(tags_data: dict[str, Any], tags: dict[str, str]) -> list[str]:
    """Get the shapes for a given set of tags."""

    result = {}

    for pattern, data in tags_data.items():
        if pattern.startswith("__"):
            continue
        if match_tags(pattern, tags):
            result[pattern] = data.get("shapes", [])

    return result[sorted(result.keys(), key=len)[-1]]


def tags_to_descriptor(tags: dict[str, str]) -> str:
    """Convert a dictionary of tags to a descriptor string."""
    return ";".join(f"{k}={v}" for k, v in tags.items() if v)


def create_tag_cell(tags: dict[str, str]) -> html.Element:
    """Create a cell displaying tags with links."""
    tag_cell = html.Element("td")
    tag_cell.set("class", "tag")

    for key, value in sorted(tags.items()):
        if not key or not value:
            continue

        a_key = html.Element("a")
        a_key.set("href", f"https://wiki.openstreetmap.org/wiki/Key:{key}")
        a_key.text = key

        a_value = html.Element("a")
        a_value.set(
            "href", f"https://wiki.openstreetmap.org/wiki/Tag:{key}={value}"
        )
        a_value.text = value

        tag_cell.append(a_key)
        wbr = html.Element("wbr")
        equal_sign = html.Element("span")
        equal_sign.text = "="
        br = html.Element("br")
        tag_cell.append(wbr)
        tag_cell.append(equal_sign)
        tag_cell.append(wbr)
        tag_cell.append(a_value)
        tag_cell.append(br)

    return tag_cell


def draw_row(
    tbody: html.Element,
    tags_data: dict[str, Any],
    collection: CollectionItem,
    row_tag: dict[str, str],
    text: str,
) -> None:
    """Draw a row of the table."""
    row = html.Element("tr")
    tbody.append(row)

    tag_cell = html.Element("td")
    tag_cell.text = text
    tag_cell.set("class", "tag")
    row.append(tag_cell)

    roentgen_cell = html.Element("td")
    roentgen_cell.set("class", "imgs")

    roentgen_shapes = tags_data.get(
        tags_to_descriptor(collection.tags | row_tag), {}
    ).get("shapes", [])

    if not roentgen_shapes:
        txt_element = html.Element("span")
        txt_element.text = str(tags_to_descriptor(collection.tags | row_tag))
        roentgen_cell.append(txt_element)
    else:
        for shape in roentgen_shapes:
            img_element = html.Element("img")
            if Path("icons", f"{shape}.svg").exists():
                img_element.set("src", f"../icons/{shape}.svg")
            elif Path("icons_sketches", f"{shape}.svg").exists():
                img_element.set("src", f"../icons_sketches/{shape}.svg")
                img_element.set("class", "sketch")
            roentgen_cell.append(img_element)

    row.append(roentgen_cell)


def add_simple_table(
    container: html.Element,
    collection: CollectionItem,
    tags_data: dict[str, Any],
) -> None:
    """Add a simple table (1D) to the container."""

    if collection.name:
        h2 = html.Element("h2")
        h2.text = collection.name
        container.append(h2)
    elif collection.page:
        h2 = html.Element("h2")
        h2.text = collection.page
        container.append(h2)

    table = html.Element("table")
    container.append(table)

    thead = html.Element("thead")
    table.append(thead)
    header_row = html.Element("tr")
    thead.append(header_row)

    for header_text in ["", ""]:
        th = html.Element("th")
        th.text = header_text
        header_row.append(th)

    tbody = html.Element("tbody")
    table.append(tbody)

    if collection.row_tags:
        for row_tag in collection.row_tags:
            draw_row(
                tbody,
                tags_data,
                collection,
                row_tag,
                "\n".join(f"{k}={v}" for k, v in row_tag.items()),
            )

    elif collection.row_key and collection.row_values:
        for row_value in collection.row_values:
            draw_row(
                tbody,
                tags_data,
                collection,
                {collection.row_key: row_value},
                row_value,
            )


def add_2d_table(
    container: html.Element,
    collection: CollectionItem,
    tags_data: dict[str, Any],
) -> None:
    """Add a 2D table to the container."""

    if collection.name:
        h2 = html.Element("h2")
        h2.text = collection.name
        container.append(h2)
    elif collection.page:
        h2 = html.Element("h2")
        h2.text = collection.page
        container.append(h2)

    rows, columns, table_data = collection.get_table_data()
    if not table_data:
        return

    table = html.Element("table")
    container.append(table)

    thead = html.Element("thead")
    table.append(thead)
    header_row = html.Element("tr")
    thead.append(header_row)

    empty_th = html.Element("th")
    header_row.append(empty_th)

    for col_value in columns:
        th = html.Element("th")
        th.set("class", "vertical")
        th.text = col_value if col_value else ""
        header_row.append(th)

    tbody = html.Element("tbody")
    table.append(tbody)

    for i, row_value in enumerate(rows):
        row = html.Element("tr")
        tbody.append(row)

        row_th = html.Element("th")
        row_th.text = row_value if row_value else ""
        row.append(row_th)

        for _j, tags in enumerate(table_data[i]):
            cell = html.Element("td")
            cell.set("class", "cell")

            roentgen_shapes = get_shapes(tags_data, tags)
            for shape in roentgen_shapes:
                img_element = html.Element("img")
                if Path("icons", f"{shape}.svg").exists():
                    img_element.set("src", f"../icons/{shape}.svg")
                elif Path("icons_sketches", f"{shape}.svg").exists():
                    img_element.set("src", f"../icons_sketches/{shape}.svg")
                    img_element.set("class", "sketch")
                cell.append(img_element)

            row.append(cell)


def write_html_document(output_path: Path, container: html.Element) -> None:
    """Write an HTML document with a container element."""
    doc = html.HtmlElement()
    doc.set("lang", "en")

    head = html.Element("head")
    doc.append(head)

    meta_charset = html.Element("meta")
    meta_charset.set("charset", "UTF-8")
    head.append(meta_charset)

    meta_viewport = html.Element("meta")
    meta_viewport.set("name", "viewport")
    meta_viewport.set("content", "width=device-width, initial-scale=1.0")
    head.append(meta_viewport)

    link = html.Element("link")
    link.set("rel", "stylesheet")
    link.set("href", "style.css")
    head.append(link)

    body = html.Element("body")
    doc.append(body)

    body.append(container)

    html_content = etree.tostring(
        doc,
        doctype="<!DOCTYPE html>",
        encoding="utf-8",
        pretty_print=True,
        method="html",
    )
    with output_path.open("wb") as output_file:
        output_file.write(html_content)


def main(output_directory: Path) -> None:
    """Run the script."""

    collections_path: Path = Path("data/collections.json")
    output_path: Path = output_directory / "collections.html"
    tags_path: Path = Path("data/tags.json")

    output_path.parent.mkdir(exist_ok=True)

    with collections_path.open(encoding="utf-8") as collections_file:
        collections_data = json.load(collections_file)

    collections: list[CollectionItem] = [
        CollectionItem.from_dict(item) for item in collections_data
    ]

    with tags_path.open(encoding="utf-8") as tags_file:
        tags_data = json.load(tags_file)

    container = html.Element("div")
    container.set("class", "container")

    h1 = html.Element("h1")
    h1.text = "Collections"
    container.append(h1)

    for collection in collections:
        if collection.row_key and collection.column_key:
            add_2d_table(container, collection, tags_data)
        else:
            add_simple_table(container, collection, tags_data)

    write_html_document(output_path, container)
    logger.info("HTML document saved to %s", output_path)
