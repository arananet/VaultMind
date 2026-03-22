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


def index_pdfs(pdf_dir: str, index_dir: str = DEFAULT_INDEX_DIR) -> int:
    """Ingest PDFs and build the FAISS index. Returns chunk count."""
    docs = load_pdf_directory(Path(pdf_dir))
    if not docs:
        return 0
    chunks = chunk_documents(docs)
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
        context_parts.append(f"[Source {i}: {source}, p.{page}]\n{doc.page_content}")

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
