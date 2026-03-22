"""Query router - dispatches queries to the appropriate VaultMind service."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Unified result from any VaultMind service."""

    answer: str
    sources: list[str]
    service: str  # "rag", "kiwix", "llm", "gis"


def route_query(
    query: str,
    index_dir: str = "data/vault_index",
    model: str = "llama3.1:8b-instruct-q4_K_M",
    kiwix_url: str = "http://localhost:8888",
    use_rag: bool = True,
    use_kiwix: bool = True,
) -> QueryResult:
    """Route a user query through available VaultMind services.

    Priority order:
    1. RAG (PDF vault) - for survival manuals and technical references
    2. Kiwix (Wikipedia/SE) - for encyclopedic knowledge
    3. Direct LLM - fallback using model weights only
    """
    # Try RAG first
    if use_rag:
        try:
            from vaultmind.rag.engine import query as rag_query

            answer = rag_query(query, index_dir=index_dir, model=model)
            return QueryResult(answer=answer, sources=["Local PDF Vault"], service="rag")
        except FileNotFoundError:
            logger.info("No RAG index found, skipping RAG search")
        except Exception:
            logger.exception("RAG query failed")

    # Try Kiwix
    if use_kiwix:
        try:
            from vaultmind.search.kiwix import KiwixClient

            client = KiwixClient(kiwix_url)
            if client.is_available():
                results = client.search(query, limit=3)
                if results:
                    # Fetch the top article and use it as context
                    from vaultmind.core.prompt import SYSTEM_PROMPT, format_rag_prompt

                    import ollama as ollama_client

                    article = client.get_article(
                        results[0].url.replace(kiwix_url, "")
                    )
                    if article:
                        # Strip HTML tags for context (basic)
                        import re

                        clean = re.sub(r"<[^>]+>", "", article)[:3000]
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
