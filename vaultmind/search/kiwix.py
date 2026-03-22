"""Kiwix .zim file search integration for offline Wikipedia/StackExchange access."""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

DEFAULT_KIWIX_URL = "http://localhost:8888"


@dataclass
class KiwixResult:
    """A single search result from Kiwix."""

    title: str
    url: str
    snippet: str


class KiwixClient:
    """Client for searching a local Kiwix server."""

    def __init__(self, base_url: str = DEFAULT_KIWIX_URL):
        self.base_url = base_url.rstrip("/")

    def is_available(self) -> bool:
        """Check if the Kiwix server is reachable."""
        try:
            resp = requests.get(f"{self.base_url}/", timeout=2)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    def search(self, query: str, limit: int = 5) -> list[KiwixResult]:
        """Search the Kiwix server for articles matching the query."""
        params = {
            "pattern": query,
            "pageLength": limit,
        }
        try:
            resp = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException:
            logger.exception("Kiwix search failed for query: %s", query)
            return []

        return self._parse_results(resp.text, query)

    def get_article(self, path: str) -> str | None:
        """Fetch the full text of a Kiwix article by path."""
        try:
            resp = requests.get(
                f"{self.base_url}/{path.lstrip('/')}",
                timeout=10,
            )
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            logger.exception("Failed to fetch article: %s", path)
            return None

    def _parse_results(self, html: str, query: str) -> list[KiwixResult]:
        """Parse Kiwix search result HTML into structured results.

        This is a simplified parser. Kiwix search returns HTML pages;
        we extract article links and titles from the response.
        """
        results = []
        # Kiwix search results contain links in <a> tags with article paths
        # Simple extraction without heavy HTML parsing dependencies
        import re

        pattern = re.compile(
            r'<a[^>]+href="(/[^"]+)"[^>]*>\s*<span[^>]*>([^<]+)</span>',
            re.IGNORECASE,
        )
        for match in pattern.finditer(html):
            url_path = match.group(1)
            title = match.group(2).strip()
            if title and not url_path.startswith("/search"):
                results.append(
                    KiwixResult(
                        title=title,
                        url=f"{self.base_url}{url_path}",
                        snippet="",
                    )
                )
            if len(results) >= 5:
                break

        return results


def search_kiwix(
    query: str,
    base_url: str = DEFAULT_KIWIX_URL,
    limit: int = 5,
) -> list[KiwixResult]:
    """Convenience function to search a local Kiwix server."""
    client = KiwixClient(base_url)
    if not client.is_available():
        logger.warning("Kiwix server not available at %s", base_url)
        return []
    return client.search(query, limit=limit)
