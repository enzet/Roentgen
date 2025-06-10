"""Tag info API.

This module provides a class for interacting with the Taginfo API to get the
most used tags in OpenStreetMap.

The API is documented at https://taginfo.openstreetmap.org/api/4.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

import requests
from lxml import etree, html

logger = logging.getLogger(__name__)

PER_PAGE: Final[int] = 100

MIN_FREQUENCY_TO_DOWNLOAD: Final[int] = 100
MIN_FREQUENCY_TO_DISPLAY: Final[int] = 100_000


@dataclass
class TagInfo:
    """Tag information."""

    key: str
    value: str | None
    total_count: int = 0
    fraction: float = 0.0
    count_nodes: int = 0
    count_ways: int = 0
    count_relations: int = 0


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
                    key=item["key"],
                    value=item["value"],
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
                key=item["key"],
                value=None,
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
            "key": key.key,
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
                key=key.key,
                value=item["value"],
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
            tag_key: str = f"{tag.key}={tag.value}"
            existing_tags[tag_key] = {
                "key": tag.key,
                "value": tag.value,
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
                    "key": tag.key,
                    "value": tag.value,
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
    if descriptor.endswith(":"):
        return tag.key.startswith(descriptor)
    if "=" in descriptor:
        return descriptor == f"{tag.key}={tag.value}"
    return tag.key == descriptor


def construct_table(
    tags: list[TagInfo], scheme: dict[str, Any]
) -> list[tuple[str, list[str], int]]:
    """Construct a table from tags.

    :param tags: list of TagInfo objects
    :param scheme: scheme to use

    :returns: list of tuples containing tag, shapes, and count
    """

    result: list[tuple[str, list[str], int]] = []

    for tag in tags:
        to_continue: bool = False
        for descriptor in scheme.get("__ignore", []) + scheme.get(
            "__only_ways", []
        ):
            if check_descriptor(tag, descriptor):
                to_continue = True
                break
        if to_continue:
            continue

        id_: str = f"{tag.key}={tag.value}"

        shapes: list[str] = []
        if id_ in scheme and "shapes" in scheme[id_]:
            shapes = scheme[id_]["shapes"]

        result.append((id_, shapes, tag.total_count))

    return result


def write_html_document(output_path: Path, container: html.Element) -> None:
    """Write an HTML document with a container element.

    :param output_path: path to the output file
    :param container: container element to add to the document
    """
    (doc := html.HtmlElement()).set("lang", "en")

    head: html.Element = html.Element("head")
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

    html_content: bytes = etree.tostring(
        doc,
        doctype="<!DOCTYPE html>",
        encoding="utf-8",
        pretty_print=True,
        method="html",
    )
    with output_path.open("wb") as output_file:
        output_file.write(html_content)


def add_table(
    container: html.Element,
    elements: list[tuple[str, list[str], int]],
) -> None:
    """Save tags to an HTML file with a styled table.

    :param elements: list of tuples containing tag, shapes, and count
    :param output_path: output path
    """

    table = html.Element("table")
    container.append(table)

    thead = html.Element("thead")
    table.append(thead)
    header_row = html.Element("tr")
    thead.append(header_row)

    for header_text in ["Tags", "", "Count"]:
        th = html.Element("th")
        th.text = header_text
        header_row.append(th)

    tbody = html.Element("tbody")
    table.append(tbody)

    for id_, imgs, count in elements:
        row = html.Element("tr")
        tbody.append(row)

        key, value = id_.split("=")

        tag_cell = html.Element("td")
        tag_cell.set("class", "tag")
        a_key = html.Element("a")
        a_key.set("href", f"https://wiki.openstreetmap.org/wiki/Key:{key}")
        a_key.text = key
        a_value = html.Element("a")
        a_value.set("href", f"https://wiki.openstreetmap.org/wiki/Tag:{id_}")
        a_value.text = value
        tag_cell.append(a_key)
        wbr = html.Element("wbr")
        equal_sign = html.Element("span")
        equal_sign.text = "="
        tag_cell.append(wbr)
        tag_cell.append(equal_sign)
        tag_cell.append(wbr)
        tag_cell.append(a_value)

        row.append(tag_cell)

        imgs_cell = html.Element("td")
        imgs_cell.set("class", "imgs")
        row.append(imgs_cell)

        for img in imgs:
            img_element = html.Element("img")
            img_element.set("src", f"../icons/{img}.svg")
            imgs_cell.append(img_element)

        count_cell = html.Element("td")
        count_cell.set("class", "count")
        count_cell.text = f"{count / 1000:.0f} K"
        row.append(count_cell)


def load_all_tags(cache_json: Path, api: TagInfoAPI) -> list[TagInfo]:
    """Load most popular tags.

    :param cache_json: path to the JSON file
    :param api: API client

    :returns: dictionary containing all tags
    """
    if cache_json.exists():
        with cache_json.open(encoding="utf-8") as input_file:
            return [
                TagInfo(
                    key=item["key"],
                    value=item["value"],
                    count_nodes=item["count_nodes"],
                    count_ways=item["count_ways"],
                    count_relations=item["count_relations"],
                    total_count=item["total_count"],
                )
                for item in json.load(input_file)["tags"]
            ]

    all_tags: list[TagInfo] = []
    for page in range(1, 100):
        logger.info("Fetching page %d...", page)
        page_tags = api.get_most_used_tags(page=page, per_page=PER_PAGE)

        if not page_tags:
            logger.error("Failed to fetch page %d.", page)
            break

        all_tags.extend(page_tags)
        logger.info("Found %d tags on page %d.", len(page_tags), page)

        # Save after each page to preserve progress.
        save_tags_to_json(all_tags, cache_json, append=False)

    logger.info("Total tags collected: %d.", len(all_tags))
    logger.info("Results saved to %s.", cache_json)

    return all_tags


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
                    key=item["key"],
                    value=None,
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
                    key=item["key"],
                    value=item["value"],
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


def main(scheme_path: Path) -> None:
    """Get the most used tags and save them to a JSON file.

    :param scheme_path: how to draw the tags
    :param osm_path: external information about the tags
    :param total_pages: total number of pages to fetch
    """

    output_directory: Path = Path("out")
    output_directory.mkdir(exist_ok=True)

    # Initialize the API client with a 1-second rate limit.
    api: TagInfoAPI = TagInfoAPI(rate_limit=1.0)

    # Load the scheme.
    with scheme_path.open(encoding="utf-8") as input_file:
        scheme: dict[str, Any] = json.load(input_file)

    drawing: dict[str, Any] = {}

    for group in scheme.get("node_icons", []):
        for rule in group.get("tags", []):
            tags: dict[str, str] = rule["tags"]
            shapes: list[str | dict[str, str]] = rule.get("shapes", [])
            add_shapes: list[str] = rule.get("add_shapes", [])

            id_: str = ";".join(f"{k}={v}" for k, v in tags.items())
            if id_ in drawing:
                continue

            drawing[id_] = {
                "shapes": shapes,
                "add_shapes": add_shapes,
            }

    # Construct the HTML document.
    container: html.Element = html.Element("div")
    container.set("class", "container")

    all_keys: list[TagInfo] = load_all_keys(
        output_directory / "most_used_keys.json", api
    )
    for key in all_keys:
        to_continue: bool = False
        for descriptor in scheme.get("__ignore", []) + scheme.get(
            "__only_ways", []
        ):
            if check_descriptor(key, descriptor):
                to_continue = True
                break
        if to_continue:
            continue

        if not (output_directory / f"{key.key}_values.json").exists():
            answer: str = input(f"Continue with {key.key}? (y/N) ")
            if answer != "y":
                break

        values: list[TagInfo] = load_key_values(
            output_directory / f"{key.key}_values.json", key, api
        )
        values_to_display: list[TagInfo] = [
            value
            for value in values
            if value.total_count >= MIN_FREQUENCY_TO_DISPLAY
        ]
        (h1 := html.Element("h1")).text = f"{key.key}=*"
        container.append(h1)
        add_table(container, construct_table(values_to_display, scheme))

    all_tags: list[TagInfo] = load_all_tags(
        output_directory / "most_used_tags.json", api
    )
    (h1 := html.Element("h1")).text = "All tags"
    container.append(h1)
    add_table(container, construct_table(all_tags, scheme))

    output_html: Path = output_directory / "output.html"
    write_html_document(output_html, container)
    logger.info("HTML table saved to %s.", output_html)
