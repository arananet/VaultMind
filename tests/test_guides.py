"""Tests for knowledge guide indexer and search."""

from pathlib import Path

from vaultmind.services.guides import (
    GUIDE_DOMAINS,
    get_guide_content,
    list_domains,
    load_guides,
)


def test_guide_domains_defined():
    """All 10 survival domains should be defined."""
    assert len(GUIDE_DOMAINS) == 10
    expected = {
        "medicine", "chemistry", "energy", "agriculture", "water",
        "construction", "communications", "metalworking", "navigation", "security",
    }
    assert set(GUIDE_DOMAINS.keys()) == expected


def test_load_guides_from_data_dir():
    """Loading guides from the project data directory should find files."""
    guides = load_guides("data/guides")
    assert len(guides) >= 10  # At least one file per domain
    for doc in guides:
        assert doc.metadata["source_type"] == "guide"
        assert doc.metadata["domain"] in GUIDE_DOMAINS


def test_load_guides_missing_dir():
    """Loading from nonexistent directory returns empty list."""
    guides = load_guides("/nonexistent/path")
    assert guides == []


def test_list_domains():
    """list_domains should return all 10 domains with availability status."""
    domains = list_domains("data/guides")
    assert len(domains) == 10
    for domain, info in domains.items():
        assert "topics" in info
        assert "files" in info
        assert "available" in info


def test_get_guide_content():
    """Getting content for a valid domain should return text."""
    content = get_guide_content("medicine", "data/guides")
    assert content is not None
    assert "Wound Care" in content or "wound" in content.lower()


def test_get_guide_content_missing_domain():
    """Getting content for an invalid domain should return None."""
    content = get_guide_content("nonexistent_domain", "data/guides")
    assert content is None


def test_guide_content_has_warnings():
    """All guides should contain safety warnings."""
    guides = load_guides("data/guides")
    for doc in guides:
        content = doc.page_content
        assert "WARNING" in content or "CRITICAL" in content or "Risk" in content, (
            f"Guide {doc.metadata.get('source_file')} missing safety warnings"
        )
