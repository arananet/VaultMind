"""PDF ingestion and chunking for the VaultMind RAG pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def load_pdf(path: Path) -> list:
    """Load a single PDF and return LangChain Document objects."""
    loader = PyMuPDFLoader(str(path))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source_file"] = path.name
    return docs


def load_pdf_directory(pdf_dir: Path) -> list:
    """Load all PDFs from a directory."""
    pdf_dir = Path(pdf_dir)
    if not pdf_dir.is_dir():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    all_docs = []
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found in %s", pdf_dir)
        return all_docs

    for pdf_path in pdf_files:
        logger.info("Loading: %s", pdf_path.name)
        try:
            docs = load_pdf(pdf_path)
            all_docs.extend(docs)
            logger.info("  -> %d pages loaded", len(docs))
        except Exception:
            logger.exception("Failed to load %s", pdf_path.name)

    logger.info("Total documents loaded: %d", len(all_docs))
    return all_docs


def chunk_documents(
    documents: list,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info("Split %d documents into %d chunks", len(documents), len(chunks))
    return chunks
