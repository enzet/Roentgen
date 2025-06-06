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

logger = logging.getLogger(__name__)


@dataclass
class TagInfo:
    """Tag information."""

    key: str
    value: str
    count_nodes: int
    count_ways: int
    count_relations: int
    total_count: int


class TagInfoAPI:
    """Tag info API."""

    BASE_URL: Final[str] = "https://taginfo.openstreetmap.org/api/4"
    CACHE_DIR: Final[Path] = Path("cache")
    CACHE_EXPIRATION_TIME: Final[int] = 86400  # 24 hours.

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
        cache_hash: str = hashlib.md5(cache_key.encode()).hexdigest()  # noqa: S324
        return self.CACHE_DIR / f"{cache_hash}.json"

    def _load_from_cache(self, cache_path: Path) -> dict[str, Any] | None:
        """Load response from cache if available and not expired.

        :param cache_path: path to the cache file

        :returns: cached response if available and not expired, None otherwise
        """
        if not cache_path.exists():
            return None

        try:
            with cache_path.open("r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                cache_time: datetime = datetime.fromisoformat(data["timestamp"])
                if (
                    datetime.now(timezone.utc) - cache_time
                ).total_seconds() > self.CACHE_EXPIRATION_TIME:
                    logger.debug("Cache expired for %s", cache_path)
                    return None
                return data["response"]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Failed to load cache from %s: %s", cache_path, e)
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
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

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
            "sortname": "count_nodes",
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

    def get_total_pages(self, per_page: int = 100) -> int:
        """Get the total number of pages available.

        :param per_page: number of tags per page

        :returns: total number of pages
        """
        try:
            data = self._make_request("tags/popular", {"rp": per_page})
            return (data.get("total", 0) + per_page - 1) // per_page
        except requests.exceptions.RequestException:
            return 0


def load_existing_tags(filename: str) -> dict[str, Any]:
    """Load existing tags from JSON file.

    :param filename: path to the JSON file

    :returns: dictionary containing existing tags data
    """
    try:
        with Path(filename).open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "tags": []}


def save_tags_to_json(
    tags: list[TagInfo], filename: str, *, append: bool = True
) -> None:
    """Save tags to a JSON file with timestamp.

    :param tags: list of TagInfo objects to save
    :param filename: output filename
    :param append: whether to append to existing tags or overwrite
    """
    if append:
        existing_data: dict[str, Any] = load_existing_tags(filename)
        existing_tags: dict[str, Any] = {
            f"{tag['key']}={tag['value']}": tag for tag in existing_data["tags"]
        }

        # Update or add new tags
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

    with Path(filename).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Get the most used tags and save them to a JSON file."""
    output_file: str = "most_used_tags.json"
    per_page: int = 100

    # Initialize the API client with a 1-second rate limit.
    api: TagInfoAPI = TagInfoAPI(rate_limit=1.0)

    # Total number of pages. Hardcoded. Use `api.get_total_pages(per_page)` to
    # get the actual number.
    total_pages: int = 10

    logger.info("Found %d pages of tags.", total_pages)
    all_tags: list[TagInfo] = []

    # Fetch all pages.
    for page in range(1, total_pages + 1):
        logger.info("Fetching page %d/%d...", page, total_pages)
        tags: list[TagInfo] = api.get_most_used_tags(
            page=page, per_page=per_page
        )

        if not tags:
            logger.error("Failed to fetch page %d.", page)
            continue

        all_tags.extend(tags)
        logger.info("Found %d tags on page %d.", len(tags), page)

        # Save after each page to preserve progress.
        save_tags_to_json(all_tags, output_file, append=False)

    logger.info("Total tags collected: %d.", len(all_tags))
    logger.info("Results saved to %s.", output_file)

    # Print summary of top 10 tags.
    logger.info("Top most used tags:")
    for index, tag in enumerate(all_tags, 1):
        logger.info(
            "%d. %s=%s. (%d)", index, tag.key, tag.value, tag.count_nodes
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
