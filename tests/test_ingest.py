"""Tests for PDF ingestion and chunking."""

from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

from vaultmind.rag.ingest import chunk_documents, load_pdf_directory


def test_load_pdf_directory_not_found():
    with pytest.raises(FileNotFoundError):
        load_pdf_directory(Path("/nonexistent/dir"))


def test_load_pdf_directory_empty(tmp_path):
    docs = load_pdf_directory(tmp_path)
    assert docs == []


def test_chunk_documents():
    """Test that chunking splits documents correctly."""
    from langchain.schema import Document

    docs = [Document(page_content="word " * 500, metadata={"source": "test.pdf"})]
    chunks = chunk_documents(docs, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 250  # chunk_size + some tolerance
