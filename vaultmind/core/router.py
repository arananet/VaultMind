"""Query router - dispatches queries to the appropriate VaultMind service."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Unified result from any VaultMind service."""

    answer: str
    sources: list[str] = field(default_factory=list)
    service: str = "unknown"  # "rag", "kiwix", "guides", "llm", "error"


def route_query(
    query: str,
    index_dir: str = "data/vault_index",
    model: str = "qwen3:8b",
    kiwix_url: str = "http://localhost:8888",
    guides_dir: str = "data/guides",
    use_rag: bool = True,
    use_kiwix: bool = True,
    use_guides: bool = True,
) -> QueryResult:
    """Route a user query through available VaultMind services.

    Priority order:
    1. RAG (PDF vault + indexed guides) — for survival manuals and technical references
    2. Knowledge Guides (direct search) — for bundled survival domain guides
    3. Kiwix (Wikipedia/SE) — for encyclopedic knowledge
    4. Direct LLM — fallback using model weights only
    """
    # Try RAG first (includes indexed guides if they were indexed)
    if use_rag:
        try:
            from vaultmind.rag.engine import query as rag_query

            answer = rag_query(query, index_dir=index_dir, model=model)
            return QueryResult(answer=answer, sources=["Local PDF Vault"], service="rag")
        except FileNotFoundError:
            logger.info("No RAG index found, skipping RAG search")
        except Exception:
            logger.exception("RAG query failed")

    # Try direct guide search (un-indexed, keyword matching)
    if use_guides:
        try:
            result = _search_guides_direct(query, guides_dir, model)
            if result:
                return result
        except Exception:
            logger.exception("Guide search failed")

    # Try Kiwix
    if use_kiwix:
        try:
            result = _search_kiwix(query, kiwix_url, model)
            if result:
                return result
        except Exception:
            logger.exception("Kiwix query failed")

    # Fallback to direct LLM
    try:
        from vaultmind.rag.engine import query_without_rag

        answer = query_without_rag(query, model=model)
        return QueryResult(
            answer=answer,
            sources=["LLM weights only (no vault context)"],
            service="llm",
        )
    except Exception:
        logger.exception("LLM query failed")
        return QueryResult(
            answer="Error: All VaultMind services are unavailable. Check that Ollama is running.",
            sources=[],
            service="error",
        )


def _search_guides_direct(
    query: str, guides_dir: str, model: str
) -> QueryResult | None:
    """Search bundled guides directly (without FAISS index)."""
    from vaultmind.services.guides import load_guides

    guides = load_guides(guides_dir)
    if not guides:
        return None

    # Simple keyword matching: find guides with most query term overlap
    query_terms = set(query.lower().split())
    scored = []
    for doc in guides:
        content_lower = doc.page_content.lower()
        score = sum(1 for term in query_terms if term in content_lower)
        if score > 0:
            scored.append((score, doc))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]

    # Use the guide content as RAG context
    context = best.page_content[:4000]
    from vaultmind.core.prompt import SYSTEM_PROMPT, format_rag_prompt

    import ollama as ollama_client

    prompt = format_rag_prompt(query, context)
    response = ollama_client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    domain = best.metadata.get("domain", "unknown")
    source_file = best.metadata.get("source_file", "unknown")
    return QueryResult(
        answer=response["message"]["content"],
        sources=[f"VaultMind Guide: {domain}/{source_file}"],
        service="guides",
    )


def _search_kiwix(
    query: str, kiwix_url: str, model: str
) -> QueryResult | None:
    """Search Kiwix and use results as LLM context."""
    import re

    from vaultmind.search.kiwix import KiwixClient

    client = KiwixClient(kiwix_url)
    if not client.is_available():
        return None

    results = client.search(query, limit=3)
    if not results:
        return None

    article = client.get_article(results[0].url.replace(kiwix_url, ""))
    if not article:
        return None

    clean = re.sub(r"<[^>]+>", "", article)[:3000]
    from vaultmind.core.prompt import SYSTEM_PROMPT, format_rag_prompt

    import ollama as ollama_client

    prompt = format_rag_prompt(query, clean)
    response = ollama_client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return QueryResult(
        answer=response["message"]["content"],
        sources=[r.title for r in results],
        service="kiwix",
    )
