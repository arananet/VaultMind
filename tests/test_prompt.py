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


def test_format_rag_prompt():
    result = format_rag_prompt("How to purify water?", "Boil water for 1 minute.")
    assert "How to purify water?" in result
    assert "Boil water for 1 minute." in result
    assert "VAULT CONTEXT" in result
