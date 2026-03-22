"""FAISS-based vector store for offline RAG retrieval."""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_INDEX_DIR = "data/vault_index"


def get_embeddings(model_name: str = DEFAULT_EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    """Create a HuggingFace embedding model (runs 100% offline after first download)."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_index(chunks: list, index_dir: str = DEFAULT_INDEX_DIR) -> FAISS:
    """Build a FAISS index from document chunks and persist to disk."""
    embeddings = get_embeddings()
    logger.info("Building FAISS index from %d chunks...", len(chunks))
    vectorstore = FAISS.from_documents(chunks, embeddings)

    index_path = Path(index_dir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_path))
    logger.info("Index saved to %s", index_path)

    return vectorstore


def load_index(index_dir: str = DEFAULT_INDEX_DIR) -> FAISS:
    """Load a persisted FAISS index from disk."""
    index_path = Path(index_dir)
    if not index_path.exists():
        raise FileNotFoundError(
            f"No vault index found at {index_path}. Run 'vaultmind index' first."
        )

    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        str(index_path), embeddings, allow_dangerous_deserialization=True
    )
    logger.info("Loaded index from %s", index_path)
    return vectorstore


def search(vectorstore: FAISS, query: str, k: int = 4) -> list:
    """Search the vector store and return top-k relevant chunks."""
    results = vectorstore.similarity_search(query, k=k)
    return results
