"""Tests for Kiwix search client."""

from unittest.mock import patch, MagicMock

from vaultmind.search.kiwix import KiwixClient, KiwixResult


def test_kiwix_not_available():
    client = KiwixClient("http://localhost:99999")
    assert client.is_available() is False


def test_kiwix_search_when_unavailable():
    client = KiwixClient("http://localhost:99999")
    results = client.search("water purification")
    assert results == []


def test_kiwix_result_dataclass():
    result = KiwixResult(title="Water", url="/wiki/Water", snippet="H2O")
    assert result.title == "Water"
    assert result.url == "/wiki/Water"
