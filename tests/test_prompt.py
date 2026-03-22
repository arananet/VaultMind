"""Tests for the Protocol Zero system prompt."""

from vaultmind.core.prompt import SYSTEM_PROMPT, format_rag_prompt


def test_system_prompt_contains_star_method():
    assert "S.T.A.R." in SYSTEM_PROMPT
    assert "Situation" in SYSTEM_PROMPT
    assert "Tools" in SYSTEM_PROMPT
    assert "Action" in SYSTEM_PROMPT
    assert "Risk" in SYSTEM_PROMPT


def test_system_prompt_contains_safety_constraint():
    assert "Data Not Found in Vault" in SYSTEM_PROMPT
    assert "No Hallucinations" in SYSTEM_PROMPT


def test_system_prompt_contains_all_domains():
    """System prompt should list all 15 survival domains."""
    domains = [
        "Field Medicine", "Pharmacology", "Chemistry", "Energy & Fuel",
        "Agriculture", "Foraging & Botany", "Water Systems",
        "Construction & Engineering", "Radio Communications",
        "Mesh Networking", "Metalworking", "Vehicle Repair",
        "Navigation", "Security & Defense", "Food Preservation",
    ]
    for domain in domains:
        assert domain in SYSTEM_PROMPT, f"Missing domain: {domain}"


def test_system_prompt_contains_safety_rules():
    """Prompt should include domain-specific safety rules."""
    assert "MEDICAL" in SYSTEM_PROMPT
    assert "CHEMISTRY" in SYSTEM_PROMPT
    assert "ENERGY" in SYSTEM_PROMPT
    assert "FORAGING" in SYSTEM_PROMPT
    assert "CONSTRUCTION" in SYSTEM_PROMPT


def test_format_rag_prompt():
    result = format_rag_prompt("How to purify water?", "Boil water for 1 minute.")
    assert "How to purify water?" in result
    assert "Boil water for 1 minute." in result
    assert "VAULT CONTEXT" in result
