"""Tests for the query router."""

from vaultmind.core.router import QueryResult


def test_query_result_defaults():
    """QueryResult should have sensible defaults."""
    result = QueryResult(answer="test")
    assert result.answer == "test"
    assert result.sources == []
    assert result.service == "unknown"


def test_query_result_with_sources():
    """QueryResult should accept sources and service."""
    result = QueryResult(
        answer="Boil water for 1 minute",
        sources=["Guide: water/water_systems.md"],
        service="guides",
    )
    assert len(result.sources) == 1
    assert result.service == "guides"
