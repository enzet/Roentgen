"""Tag info API.

This module provides a class for interacting with the Taginfo API to get the
most used tags in OpenStreetMap.

The API is documented at https://taginfo.openstreetmap.org/api/4.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

import requests
import yaml
from lxml import etree, html

from roentgen.collection import tags_to_descriptor

logger = logging.getLogger(__name__)

MIN_FREQUENCY_TO_DOWNLOAD: Final[int] = 100
PER_PAGE: Final[int] = 100
PLACEHOLDER_COLOR = "#FFEEFF"
REPEATED_COLOR = "#FFFFDD"
CANDIDATE_COLOR = "#DDDDFF"


@dataclass
class TagInfo:
    """Tag information."""

    descriptor: str
    total_count: int = 0
    fraction: float = 0.0
    count_nodes: int = 0
    count_ways: int = 0
    count_relations: int = 0

    def __hash__(self) -> int:
        return hash(self.descriptor)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, TagInfo) and self.descriptor == other.descriptor
        )

    def get_key(self) -> str:
        """Get the key of the tag."""
        if "=" in self.descriptor and self.descriptor.count("=") == 1:
            key, _value = self.descriptor.split("=")
            return key
        return self.descriptor

    def get_value(self) -> str | None:
        """Get the value of the tag."""
        if self.descriptor.count("=") == 1:
            _key, value = self.descriptor.split("=")
            return value
        return None


class TagInfoAPI:
    """Tag info API."""

    BASE_URL: Final[str] = "https://taginfo.openstreetmap.org/api/4"
    CACHE_DIR: Final[Path] = Path("cache")
    CACHE_EXPIRATION_TIME: Final[int] = 86400 * 365  # 1 year.

    def __init__(self, rate_limit: float = 1.0) -> None:
        """Initialize the API client with rate limiting.

        :param rate_limit: minimum time between requests in seconds
        """
        self.rate_limit: float = rate_limit
        self.last_request_time: float = 0.0
        self.session: requests.Session = requests.Session()

        self.CACHE_DIR.mkdir(exist_ok=True)

    def _get_cache_path(
        self, endpoint: str, params: dict[str, Any] | None
    ) -> Path:
        """Get the cache file path for a request.

        :param endpoint: API endpoint
        :param params: query parameters

        :returns: path to the cache file
        """
        # Create a unique key for the request.
        cache_key: str = (
            f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        )
        # Create a hash of the key to use as filename.
        cache_hash: str = hashlib.md5(  # noqa: S324
            cache_key.encode()
        ).hexdigest()
        return self.CACHE_DIR / f"{cache_hash}.json"

    def _load_from_cache(self, cache_path: Path) -> dict[str, Any] | None:
        """Load response from cache if available and not expired.

        :param cache_path: path to the cache file

        :returns: cached response if available and not expired, None otherwise
        """
        if not cache_path.exists():
            return None

        try:
            with cache_path.open(encoding="utf-8") as input_file:
                data: dict[str, Any] = json.load(input_file)
                cache_time: datetime = datetime.fromisoformat(data["timestamp"])
                if (
                    datetime.now(timezone.utc) - cache_time
                ).total_seconds() > self.CACHE_EXPIRATION_TIME:
                    logger.debug("Cache expired for %s", cache_path)
                    return None
                return data["response"]
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            logger.warning(
                "Failed to load cache from %s: %s", cache_path, error
            )
            return None

    def _save_to_cache(
        self, cache_path: Path, response: dict[str, Any]
    ) -> None:
        """Save response to cache.

        :param cache_path: path to the cache file
        :param response: API response to cache
        """
        data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response": response,
        }
        with cache_path.open("w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=2, ensure_ascii=False)

    def _make_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a request to the taginfo API with rate limiting.

        :param endpoint: API endpoint to call
        :param params: query parameters for the request

        :returns: JSON response from the API

        :raises requests.exceptions.RequestException: if the request fails
        """
        cache_path: Path = self._get_cache_path(endpoint, params)
        cached_response: dict[str, Any] | None = self._load_from_cache(
            cache_path
        )
        if cached_response is not None:
            logger.debug("Using cached response for %s", endpoint)
            return cached_response

        current_time: float = time.time()
        time_since_last_request: float = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last_request)

        url: str = f"{self.BASE_URL}/{endpoint}"
        response: requests.Response = self.session.get(url, params=params or {})
        response.raise_for_status()

        self.last_request_time = float(time.time())
        json_response = response.json()

        self._save_to_cache(cache_path, json_response)

        return json_response

    def get_most_used_tags(
        self, page: int = 1, per_page: int = 100
    ) -> list[TagInfo]:
        """Get the most used tags in OpenStreetMap.

        :param page: page number to fetch (1-based)
        :param per_page: number of tags per page

        :returns: list of TagInfo objects sorted by total usage
        """
        params: dict[str, Any] = {
            "sortname": "count_all",
            "sortorder": "desc",
            "page": page,
            "rp": per_page,
            "filter": "all",
            "lang": "en",
        }

        try:
            data: dict[str, Any] = self._make_request("tags/popular", params)
            tags: list[TagInfo] = []

            for item in data.get("data", []):
                tag = TagInfo(
                    descriptor=f"{item['key']}={item['value']}",
                    count_nodes=item["count_nodes"],
                    count_ways=item["count_ways"],
                    count_relations=item["count_relations"],
                    total_count=item["count_all"],
                )
                tags.append(tag)
        except requests.exceptions.RequestException:
            return []
        else:
            return tags

    def get_most_used_keys(
        self, page: int = 1, per_page: int = 100
    ) -> list[TagInfo]:
        """Get the most used keys in OpenStreetMap.

        :param page: page number to fetch (1-based)
        :param per_page: number of keys per page

        :returns: list of keys
        """
        params: dict[str, Any] = {
            "sortname": "count_all",
            "sortorder": "desc",
            "page": page,
            "rp": per_page,
            "filter": "all",
            "lang": "en",
        }
        data: dict[str, Any] = self._make_request("keys/all", params)
        return [
            TagInfo(
                descriptor=item["key"],
                count_nodes=item["count_nodes"],
                count_ways=item["count_ways"],
                count_relations=item["count_relations"],
                total_count=item["count_all"],
            )
            for item in data.get("data", [])
        ]

    def get_key_values(
        self, key: TagInfo, page: int = 1, per_page: int = 100
    ) -> list[TagInfo]:
        """Get the most used values for a key in OpenStreetMap.

        :param key: key to get values for
        :param page: page number to fetch (1-based)
        :param per_page: number of values per page

        :returns: list of TagInfo objects sorted by total usage
        """
        params: dict[str, Any] = {
            "key": key.get_key(),
            "page": page,
            "rp": per_page,
            "sortname": "count_all",
            "sortorder": "desc",
            "filter": "all",
            "lang": "en",
        }
        data: dict[str, Any] = self._make_request("key/values", params)
        return [
            TagInfo(
                descriptor=f"{key.get_key()}={item['value']}",
                total_count=item["count"],
                fraction=item["fraction"],
            )
            for item in data.get("data", [])
        ]


def load_existing_tags(output_path: Path) -> dict[str, Any]:
    """Load existing tags from JSON file.

    :param output_path: path to the JSON file

    :returns: dictionary containing existing tags data
    """
    try:
        with output_path.open(encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "tags": []}


def save_tags_to_json(
    tags: list[TagInfo], output_path: Path, *, append: bool = True
) -> None:
    """Save tags to a JSON file with timestamp.

    :param tags: list of TagInfo objects to save
    :param output_path: output path
    :param append: whether to append to existing tags or overwrite
    """
    if append:
        existing_data: dict[str, Any] = load_existing_tags(output_path)
        existing_tags: dict[str, Any] = {
            f"{tag['key']}={tag['value']}": tag for tag in existing_data["tags"]
        }

        # Update or add new tags.
        for tag in tags:
            existing_tags[tag.descriptor] = {
                "key": tag.get_key(),
                "value": tag.get_value(),
                "count_nodes": tag.count_nodes,
                "count_ways": tag.count_ways,
                "count_relations": tag.count_relations,
                "total_count": tag.total_count,
            }

        data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tags": list(existing_tags.values()),
        }
    else:
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tags": [
                {
                    "key": tag.get_key(),
                    "value": tag.get_value(),
                    "count_nodes": tag.count_nodes,
                    "count_ways": tag.count_ways,
                    "count_relations": tag.count_relations,
                    "total_count": tag.total_count,
                }
                for tag in tags
            ],
        }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check_descriptor(tag: TagInfo, descriptor: str) -> bool:
    """Check if a tag matches a descriptor."""

    for part in tag.descriptor.split(";"):
        if part == descriptor:
            return True
        for pair in tag.descriptor.split("="):
            if descriptor.endswith(":") and pair.startswith(descriptor):
                return True
            if descriptor == pair:
                return True
    return False


def construct_table(
    tags: list[TagInfo],
    roentgen_scheme: RoentgenScheme,
    map_machine_scheme: MapMachineScheme,
    id_scheme: IdScheme,
) -> list[Element]:
    """Construct a table from tags.

    :param tags: list of TagInfo objects
    :param scheme: scheme to use

    :returns: list of tuples containing tag, shapes, and count
    """

    result: list[Element] = []

    for tag in tags:
        if (
            roentgen_scheme.is_ignored(tag)
            or map_machine_scheme.is_ignored(tag)
            or id_scheme.is_ignored(tag)
        ):
            continue

        roentgen_icons: list[str] = roentgen_scheme.icons.get(
            tag.descriptor, []
        )
        map_machine_icons: list[str] = map_machine_scheme.icons.get(
            tag.descriptor, []
        )
        map_machine_added_icons: list[str] = map_machine_scheme.added_icons.get(
            tag.descriptor, []
        )
        id_tagging_icon: str | None = id_scheme.icons.get(tag.descriptor, None)

        element: Element = Element(
            tag=tag.descriptor,
            roentgen_icons=roentgen_icons,
            map_machine_icons=map_machine_icons,
            map_machine_added_icons=map_machine_added_icons,
            id_tagging_icon=id_tagging_icon,
            total_count=tag.total_count,
        )
        result.append(element)

    return result


def write_html_document(output_path: Path, container: etree._Element) -> None:
    """Write an HTML document with a container element.

    :param output_path: path to the output file
    :param container: container element to add to the document
    """
    (doc := html.HtmlElement()).set("lang", "en")

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

    script = html.Element("script")
    script.set("src", "script.js")
    head.append(script)

    body = html.Element("body")
    doc.append(body)

    body.append(container)

    html_content: bytes = etree.tostring(
        doc,
        doctype="<!DOCTYPE html>",
        encoding="utf-8",
        pretty_print=True,
        method="html",
    )
    with output_path.open("wb") as output_file:
        output_file.write(html_content)


@dataclass
class Element:
    """OpenStreetMap tag."""

    tag: str
    roentgen_icons: list[str]
    map_machine_icons: list[str]
    map_machine_added_icons: list[str]
    id_tagging_icon: str | None
    total_count: int


def add_table(
    container: etree._Element,
    elements: list[Element],
    id_path: Path | None,
    maki_path: Path | None,
    temaki_path: Path | None,
    statistics: dict[str, Any],
) -> None:
    """Save tags to an HTML file with a styled table.

    :param container: container element to add the table to
    :param elements: list of tuples containing tag, shapes, and count
    """

    table = html.Element("table")
    container.append(table)

    thead = html.Element("thead")
    table.append(thead)
    header_row = html.Element("tr")
    thead.append(header_row)

    for header_text in ["Tags", "Rö", "MM", "iD", "Count"]:
        th = html.Element("th")
        th.text = header_text
        header_row.append(th)

    tbody = html.Element("tbody")
    table.append(tbody)

    for element in elements:
        row = html.Element("tr")

        is_id_placeholder = False
        is_id_repeated = False
        is_map_machine_placeholder = False
        is_map_machine_repeated = False
        for other_element in elements:
            if other_element == element:
                continue
            if (
                element.id_tagging_icon
                and element.id_tagging_icon == other_element.id_tagging_icon
            ):
                is_id_repeated = True
                if element.tag.startswith(other_element.tag.replace("*", "")):
                    is_id_placeholder = True
            if (
                element.map_machine_icons
                and other_element.map_machine_icons
                and element.map_machine_icons[0]
                == other_element.map_machine_icons[0]
            ):
                is_map_machine_repeated = True
                if element.tag.startswith(other_element.tag.replace("*", "")):
                    is_map_machine_placeholder = True

        if not is_map_machine_placeholder:
            statistics["map_machine_usages"] += int(
                bool(element.map_machine_icons)
                or bool(element.map_machine_added_icons)
            )
        if not is_id_placeholder:
            statistics["id_usages"] += int(bool(element.id_tagging_icon))

        tbody.append(row)

        pairs = element.tag.split(";")

        tag_cell = html.Element("td")
        tag_cell.set("class", "tag")

        for pair in pairs:
            if "=" not in pair or pair.count("=") > 1:
                continue

            key, value = pair.split("=")
            a_key = html.Element("a")
            a_key.set("href", f"https://wiki.openstreetmap.org/wiki/Key:{key}")
            a_key.text = key
            a_value = html.Element("a")
            a_value.set(
                "href", f"https://wiki.openstreetmap.org/wiki/Tag:{pair}"
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

        row.append(tag_cell)

        imgs_cell = html.Element("td")
        imgs_cell.set("class", "imgs")
        row.append(imgs_cell)

        for img in element.roentgen_icons:
            img_element = html.Element("img")
            img_element.set("class", "lazy-svg")
            for suffix in ("", "_v999", "_v0", "_v1", "_v2"):
                if Path("shapes", "x1", f"{img}{suffix}.svg").exists():
                    img_element.set(
                        "data-src", f"../shapes/x1/{img}{suffix}.svg"
                    )
                    img_element.set("title", f"{img}{suffix}")
                    break
            imgs_cell.append(img_element)
        imgs_cell = html.Element("td")
        imgs_cell.set("class", "imgs")
        row.append(imgs_cell)

        def add_map_machine_icon(
            img: str, prefix: str, imgs_cell: etree._Element = imgs_cell
        ) -> bool:
            if prefix:
                span = html.Element("span")
                span.text = prefix
                imgs_cell.append(span)
            img_element = html.Element("img")
            img_element.set("class", "lazy-svg")
            found: bool = False
            for suffix in ("", "_v999", "_v0", "_v1", "_v2"):
                if Path("shapes", "x1", f"{img}{suffix}.svg").exists():
                    img_element.set(
                        "data-src", f"../shapes/x1/{img}{suffix}.svg"
                    )
                    img_element.set("title", f"{img}{suffix}")
                    found = True
                    break
            if found:
                imgs_cell.append(img_element)
            else:
                span = html.Element("code")
                span.text = img
                imgs_cell.append(span)
            return found

        has_map_machine_icon: bool = False
        for img in element.map_machine_icons:
            has_map_machine_icon |= add_map_machine_icon(img, "")
        for img in element.map_machine_added_icons:
            add_map_machine_icon(img, " + ")

        if is_map_machine_repeated:
            imgs_cell.set("style", f"background-color: {REPEATED_COLOR};")
        if is_map_machine_placeholder:
            imgs_cell.set("style", f"background-color: {PLACEHOLDER_COLOR};")

        id_imgs_cell = html.Element("td")
        id_imgs_cell.set("class", "imgs")
        row.append(id_imgs_cell)

        file_name: str
        img_element = html.Element("img")
        img_element.set("class", "lazy-svg")

        if element.id_tagging_icon and element.id_tagging_icon[0].startswith(
            "roentgen-"
        ):
            file_name = (
                f"{element.id_tagging_icon[0].removeprefix('roentgen-')}.svg"
            )
            img_element.set("data-src", f"../icons/{file_name}")
            id_imgs_cell.append(img_element)
        elif (
            element.id_tagging_icon
            and temaki_path is not None
            and element.id_tagging_icon[0].startswith("temaki-")
        ):
            file_name = (
                f"{element.id_tagging_icon[0].removeprefix('temaki-')}.svg"
            )
            img_element.set("data-src", str(temaki_path / "icons" / file_name))
            id_imgs_cell.append(img_element)
        elif (
            element.id_tagging_icon
            and id_path is not None
            and (
                element.id_tagging_icon[0].startswith("far-")
                or element.id_tagging_icon[0].startswith("fas-")
            )
        ):
            file_name = f"{element.id_tagging_icon[0]}.svg"
            img_element.set(
                "data-src", str(id_path / "svg" / "fontawesome" / file_name)
            )
            id_imgs_cell.append(img_element)
        elif (
            element.id_tagging_icon
            and id_path is not None
            and (element.id_tagging_icon[0].startswith("iD-"))
        ):
            file_name = f"{element.id_tagging_icon[0][3:]}.svg"
            img_element.set(
                "data-src",
                str(id_path / "svg" / "iD-sprite" / "presets" / file_name),
            )
            id_imgs_cell.append(img_element)
        elif (
            element.id_tagging_icon
            and maki_path is not None
            and element.id_tagging_icon[0].startswith("maki-")
        ):
            file_name = (
                f"{element.id_tagging_icon[0].removeprefix('maki-')}.svg"
            )
            img_element.set("data-src", str(maki_path / "icons" / file_name))
            id_imgs_cell.append(img_element)

        if is_id_repeated:
            id_imgs_cell.set("style", f"background-color: {REPEATED_COLOR};")
        if is_id_placeholder:
            id_imgs_cell.set("style", f"background-color: {PLACEHOLDER_COLOR};")
        if (
            (not element.id_tagging_icon or is_id_placeholder)
            and has_map_machine_icon
            and not is_map_machine_placeholder
            and not is_map_machine_repeated
        ):
            imgs_cell.set("style", f"background-color: {CANDIDATE_COLOR};")

        id_code = html.Element("code")
        if element.id_tagging_icon:
            text = element.id_tagging_icon[0]
            id_code.text = text.split("-")[0]
        id_code.set("style", "padding-left: 10px;")
        id_imgs_cell.append(id_code)

        count_cell = html.Element("td")
        count_cell.set("class", "count")
        count_cell.text = f"{element.total_count / 1000:.0f} K"
        row.append(count_cell)


def json_to_taginfo(item: dict[str, Any]) -> TagInfo:
    """Convert a JSON object from the Taginfo API to a TagInfo instance."""
    return TagInfo(
        descriptor=f"{item['key']}={item['value']}",
        count_nodes=item["count_nodes"],
        count_ways=item["count_ways"],
        count_relations=item["count_relations"],
        total_count=item["total_count"],
    )


def load_all_tags(
    cache_json: Path, api: TagInfoAPI, min_frequency: int
) -> list[TagInfo]:
    """Load most popular tags.

    :param cache_json: path to the JSON file
    :param api: API client

    :returns: dictionary containing all tags
    """
    if cache_json.exists():
        with cache_json.open(encoding="utf-8") as input_file:
            return [
                json_to_taginfo(item) for item in json.load(input_file)["tags"]
            ]

    all_tags: list[TagInfo] = []
    for page in range(1, 500):
        cache_page_json = cache_json.parent / f"most_used_tags_p{page}.json"
        if cache_page_json.exists():
            with cache_page_json.open(encoding="utf-8") as input_file:
                page_tags = [
                    json_to_taginfo(item)
                    for item in json.load(input_file)["tags"]
                ]
        else:
            logger.info("Fetching page %d...", page)
            page_tags = api.get_most_used_tags(page=page, per_page=PER_PAGE)

        if not page_tags:
            logger.error("Failed to fetch page %d.", page)
            break

        all_tags.extend(page_tags)
        logger.info("Found %d tags on page %d.", len(page_tags), page)

        # Save after each page to preserve progress.
        save_tags_to_json(all_tags, cache_json, append=False)
        save_tags_to_json(page_tags, cache_page_json, append=False)

    logger.info("Total tags collected: %d.", len(all_tags))
    logger.info("Results saved to %s.", cache_json)

    return [tag for tag in all_tags if tag.total_count >= min_frequency]


def load_all_keys(cache_json: Path, api: TagInfoAPI) -> list[TagInfo]:
    """Load all keys.

    :param cache_json: path to the JSON file
    :param api: API client

    :returns: dictionary containing all keys
    """
    if cache_json.exists():
        with cache_json.open(encoding="utf-8") as input_file:
            return [
                TagInfo(
                    descriptor=item["key"],
                    count_nodes=item["count_nodes"],
                    count_ways=item["count_ways"],
                    count_relations=item["count_relations"],
                    total_count=item["total_count"],
                )
                for item in json.load(input_file)["tags"]
            ]

    # Fetch the most used keys.
    all_keys: list[TagInfo] = []
    for page in range(1, 10):
        logger.info("Fetching page %d...", page)
        page_keys = api.get_most_used_keys(page=page, per_page=PER_PAGE)

        if not page_keys:
            logger.error("Failed to fetch page %d.", page)
            break

        all_keys.extend(page_keys)
        logger.info("Found %d keys on page %d.", len(page_keys), page)

        # Save after each page to preserve progress.
        save_tags_to_json(all_keys, cache_json, append=False)

    logger.info("Total keys collected: %d.", len(all_keys))
    logger.info("Results saved to %s.", cache_json)

    return all_keys


def load_key_values(
    cache_json: Path, key: TagInfo, api: TagInfoAPI
) -> list[TagInfo]:
    """Load key values.

    :param cache_json: path to the JSON file
    :param key: key to load
    :param api: API client

    :returns: dictionary containing all key values
    """
    if cache_json.exists():
        with cache_json.open(encoding="utf-8") as input_file:
            return [
                TagInfo(
                    descriptor=f"{item['key']}={item['value']}",
                    count_nodes=item["count_nodes"],
                    count_ways=item["count_ways"],
                    count_relations=item["count_relations"],
                    total_count=item["total_count"],
                )
                for item in json.load(input_file)["tags"]
            ]

    all_key_values: list[TagInfo] = []
    for page in range(1, 10):
        logger.info("Fetching page %d...", page)
        page_key_values = api.get_key_values(
            key=key, page=page, per_page=PER_PAGE
        )
        if not page_key_values:
            logger.error("Failed to fetch page %d.", page)
            break

        all_key_values.extend(page_key_values)
        logger.info(
            "Found %d key values on page %d.", len(page_key_values), page
        )

        # Save after each page to preserve progress.
        save_tags_to_json(all_key_values, cache_json, append=False)

        if all_key_values[-1].total_count < MIN_FREQUENCY_TO_DOWNLOAD:
            break

    logger.info("Total key values collected: %d.", len(all_key_values))
    logger.info("Results saved to %s.", cache_json)

    return all_key_values


@dataclass
class Scheme:
    """Tagging scheme."""

    icons: dict[str, list[str]]
    added_icons: dict[str, list[str]]

    def has(self, descriptor: str) -> bool:
        """Check if a descriptor has icon."""
        return descriptor in self.icons or descriptor in self.added_icons


@dataclass
class RoentgenScheme(Scheme):
    """Roentgen scheme."""

    ignored: list[str]
    only_ways: list[str]

    @classmethod
    def from_dict(cls, scheme: dict[str, Any]) -> RoentgenScheme:
        """Create a RoentgenScheme from a dictionary."""
        return cls(
            {
                key: value["icons"]
                for key, value in scheme.items()
                if key not in ("__ignore", "__only_ways")
            },
            {},
            scheme["__ignore"],
            scheme["__only_ways"],
        )

    def is_ignored(self, tag: TagInfo) -> bool:
        """Check if a tag is ignored."""
        for descriptor in self.ignored + self.only_ways:
            if check_descriptor(tag, descriptor):
                return True
        return False

    def get_tags(self) -> list[TagInfo]:
        """Get all tags."""
        return [TagInfo(descriptor=key, total_count=0) for key in self.icons]


@dataclass
class MapMachineScheme(Scheme):
    """Map Machine scheme."""

    ignored: list[str]

    @classmethod
    def from_yaml(
        cls, scheme: dict[str, Any], keys: dict[str, list[str]]
    ) -> MapMachineScheme:
        """Parse scheme from YAML file."""
        icons: dict[str, list[str]] = {}
        added_icons: dict[str, list[str]] = {}

        for group in scheme["nodes"]:
            for definition in group["tags"]:
                descriptor = tags_to_descriptor(definition["tags"])
                shapes = []
                added_shapes = []
                for shape in definition.get("shapes", []):
                    if isinstance(shape, str):
                        shapes.append(shape)
                    elif "shape" in shape:
                        shapes.append(shape["shape"])
                for shape in definition.get("add_shapes", []):
                    if isinstance(shape, str):
                        added_shapes.append(shape)
                    elif "shape" in shape:
                        added_shapes.append(shape["shape"])
                icons[descriptor] = shapes
                added_icons[descriptor] = added_shapes

        ignored = [*keys["keys_to_write"], *keys["keys_to_skip"]] + [
            f"{x}:" for x in [*keys["prefix_to_write"], *keys["prefix_to_skip"]]
        ]
        return cls(icons, added_icons, ignored)

    def is_ignored(self, tag: TagInfo) -> bool:
        """Check if a tag is ignored."""
        for descriptor in self.ignored:
            if check_descriptor(tag, descriptor):
                return True
        return False

    def get_tags(self) -> list[TagInfo]:
        """Get all tags."""
        return [TagInfo(descriptor=key, total_count=0) for key in self.icons]


@dataclass
class IdScheme(Scheme):
    """iD scheme."""

    discarded: list[str] = field(default_factory=list)

    @classmethod
    def from_directory(cls, path: Path) -> IdScheme:
        """Create an IdScheme from a directory."""
        with (path / "data" / "discarded.json").open(
            encoding="utf-8"
        ) as input_file:
            discarded: list[str] = list(json.load(input_file).keys())

        icons: dict[str, list[str]] = {}
        for file in (path / "data" / "presets").rglob("*.json"):
            with file.open(encoding="utf-8") as input_file:
                data: dict[str, Any] = json.load(input_file)
                if "tags" not in data or "icon" not in data:
                    continue
                id_ = ";".join(f"{k}={v}" for k, v in data["tags"].items())
                icons[id_] = [data["icon"]]

        for file in (path / "data" / "fields").rglob("*.json"):
            with file.open(encoding="utf-8") as input_file:
                data = json.load(input_file)
                if "key" not in data or "icons" not in data:
                    continue
                for value, icon in data["icons"].items():
                    icons[f"{data['key']}={value}"] = [icon]

        return cls(icons, {}, discarded)

    def is_ignored(self, tag: TagInfo) -> bool:
        """Check if a tag is ignored."""
        for descriptor in self.discarded:
            if check_descriptor(tag, descriptor):
                return True
        return False

    def get_tags(self) -> list[TagInfo]:
        """Get all tags."""
        return [TagInfo(descriptor=key, total_count=0) for key in self.icons]


def main(
    roentgen_scheme_path: Path,
    map_machine_scheme_path: Path | None,
    id_tagging_schema_path: Path | None,
    id_path: Path | None,
    maki_path: Path | None,
    temaki_path: Path | None,
    min_frequency: int,
    *,
    show_grouped_tags: bool = False,
    show_all_tags: bool = False,
    show_defined_tags: bool = False,
) -> None:
    """Get the most used tags and save them to a JSON file.

    :param scheme_path: how to draw the tags
    """

    output_directory: Path = Path("out")
    output_directory.mkdir(exist_ok=True)

    # Initialize the API client with a 1-second rate limit.
    api: TagInfoAPI = TagInfoAPI(rate_limit=1.0)

    with roentgen_scheme_path.open(encoding="utf-8") as input_file:
        roentgen_scheme: RoentgenScheme = RoentgenScheme.from_dict(
            json.load(input_file)
        )

    map_machine_scheme: MapMachineScheme = MapMachineScheme({}, {}, [])
    if map_machine_scheme_path is not None:
        with (
            (map_machine_scheme_path / "nodes.yml").open() as nodes_file,
            (map_machine_scheme_path / "keys.yml").open() as keys_file,
        ):
            map_machine_scheme: MapMachineScheme = MapMachineScheme.from_yaml(
                yaml.safe_load(nodes_file), yaml.safe_load(keys_file)
            )
    else:
        logger.warning("Map Machine scheme not found.")

    id_scheme: IdScheme = IdScheme({}, {})
    if id_tagging_schema_path is not None:
        discarded_path: Path = (
            id_tagging_schema_path / "data" / "discarded.json"
        )
        if discarded_path.exists():
            id_scheme = IdScheme.from_directory(id_tagging_schema_path)
    else:
        logger.warning("iD scheme not found.")

    statistics = {"map_machine_usages": 0, "id_usages": 0}

    # Construct the HTML document.
    container = html.Element("div")
    container.set("class", "container")

    if show_grouped_tags:
        all_keys: list[TagInfo] = load_all_keys(
            output_directory / "most_used_keys.json", api
        )
        for key in all_keys:
            if roentgen_scheme.is_ignored(key) or id_scheme.is_ignored(key):
                continue

            if key.total_count < min_frequency:
                break

            if not (output_directory / f"{key.get_key()}_values.json").exists():
                logger.info("Total count: %d.", key.total_count)
                answer: str = input(f"Continue with {key.get_key()}=*? (y/N) ")
                if answer != "y":
                    break

            values: list[TagInfo] = load_key_values(
                output_directory / f"{key.get_key()}_values.json", key, api
            )
            values_to_display: list[TagInfo] = [
                value
                for value in values
                if (
                    value.total_count >= min_frequency
                    or id_scheme.has(value.descriptor)
                    or roentgen_scheme.has(value.descriptor)
                    or map_machine_scheme.has(value.descriptor)
                )
                and not roentgen_scheme.is_ignored(value)
                and not map_machine_scheme.is_ignored(value)
                and not id_scheme.is_ignored(value)
            ]
            if len(values_to_display) > 0:
                (h1 := html.Element("h1")).text = f"{key.get_key()}=*"
                container.append(h1)
                span = html.Element("span")
                span.text = f"Total count: {key.total_count}."
                container.append(span)
                add_table(
                    container,
                    construct_table(
                        values_to_display,
                        roentgen_scheme,
                        map_machine_scheme,
                        id_scheme,
                    ),
                    id_path,
                    maki_path,
                    temaki_path,
                    statistics,
                )

    if show_all_tags:
        all_tags: list[TagInfo] = load_all_tags(
            output_directory / "most_used_tags.json", api, min_frequency
        )
        (h1 := html.Element("h1")).text = "All tags"
        container.append(h1)
        add_table(
            container,
            construct_table(
                all_tags, roentgen_scheme, map_machine_scheme, id_scheme
            ),
            id_path,
            maki_path,
            temaki_path,
            statistics,
        )

    if show_defined_tags:
        all_tags: list[TagInfo] = load_all_tags(
            output_directory / "most_used_tags.json", api, min_frequency
        )
        all_tags_dict = {tag.descriptor: tag for tag in all_tags}
        defined_tags: set[TagInfo] = (
            set(all_tags)
            | set(roentgen_scheme.get_tags())
            | set(map_machine_scheme.get_tags())
            | set(id_scheme.get_tags())
        )
        defined_tags_list: list = [
            x for x in defined_tags if ("maxspeed" not in x.descriptor)
        ]
        for tag in defined_tags_list:
            if tag.descriptor in all_tags_dict:
                tag.total_count = all_tags_dict[tag.descriptor].total_count

        defined_tags_list.sort(key=lambda x: (-x.total_count, x.descriptor))
        (h1 := html.Element("h1")).text = "Defined tags"
        container.append(h1)
        statistics = {"map_machine_usages": 0, "id_usages": 0}
        add_table(
            container,
            construct_table(
                defined_tags_list,
                roentgen_scheme,
                map_machine_scheme,
                id_scheme,
            ),
            id_path,
            maki_path,
            temaki_path,
            statistics,
        )

    logger.info(
        "iD: %d, MM: %d, diff: %d",
        statistics["id_usages"],
        statistics["map_machine_usages"],
        statistics["id_usages"] - statistics["map_machine_usages"],
    )
    shutil.copy(Path("data") / "tags.css", output_directory / "style.css")
    shutil.copy(Path("data") / "tags.js", output_directory / "script.js")

    output_html: Path = output_directory / "output.html"
    write_html_document(output_html, container)
    logger.info("HTML table saved to %s.", output_html)
