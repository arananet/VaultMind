"""RAG engine - ties together ingestion, vector search, and LLM inference."""

from __future__ import annotations

import logging
from pathlib import Path

from vaultmind.core.prompt import SYSTEM_PROMPT, format_rag_prompt
from vaultmind.rag.ingest import chunk_documents, load_pdf_directory
from vaultmind.rag.vectorstore import build_index, load_index, search

logger = logging.getLogger(__name__)

DEFAULT_INDEX_DIR = "data/vault_index"
DEFAULT_MODEL = "llama3.1:8b-instruct-q4_K_M"


def index_pdfs(
    pdf_dir: str,
    index_dir: str = DEFAULT_INDEX_DIR,
    include_guides: bool = False,
    guides_dir: str = "data/guides",
) -> int:
    """Ingest PDFs (and optionally knowledge guides) and build the FAISS index.

    Returns the total chunk count.
    """
    all_docs = []

    # Load PDFs if directory exists and has files
    pdf_path = Path(pdf_dir)
    if pdf_path.is_dir():
        docs = load_pdf_directory(pdf_path)
        all_docs.extend(docs)
    else:
        logger.info("PDF directory not found: %s (skipping)", pdf_dir)

    # Load bundled knowledge guides
    if include_guides:
        from vaultmind.services.guides import load_guides

        guide_docs = load_guides(guides_dir)
        all_docs.extend(guide_docs)
        logger.info("Loaded %d knowledge guide documents", len(guide_docs))

    if not all_docs:
        return 0

    chunks = chunk_documents(all_docs)
    build_index(chunks, index_dir)
    return len(chunks)


def query(
    user_query: str,
    index_dir: str = DEFAULT_INDEX_DIR,
    model: str = DEFAULT_MODEL,
    top_k: int = 4,
) -> str:
    """Run a RAG-augmented query against the local vault and LLM."""
    import ollama as ollama_client

    # Retrieve relevant context
    vectorstore = load_index(index_dir)
    results = search(vectorstore, user_query, k=top_k)

    context_parts = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source_file", "unknown")
        page = doc.metadata.get("page", "?")
        domain = doc.metadata.get("domain", "")
        source_type = doc.metadata.get("source_type", "pdf")

        if source_type == "guide":
            context_parts.append(
                f"[Source {i}: Guide — {domain}/{source}]\n{doc.page_content}"
            )
        else:
            context_parts.append(
                f"[Source {i}: {source}, p.{page}]\n{doc.page_content}"
            )

    context = "\n\n".join(context_parts)
    prompt = format_rag_prompt(user_query, context)

    # Call local LLM via Ollama
    response = ollama_client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return response["message"]["content"]


def query_without_rag(user_query: str, model: str = DEFAULT_MODEL) -> str:
    """Query the LLM directly without RAG context (fallback mode)."""
    import ollama as ollama_client

    response = ollama_client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
    )

    return response["message"]["content"]
