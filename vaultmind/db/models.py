"""VaultMind database models — PostgreSQL via SQLAlchemy.

Data Model v1.0 — Scalable Schema Design
=========================================

The schema is designed for extensibility and offline operation. All tables
include created_at/updated_at timestamps and soft-delete support.

Entity Relationship:
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│   Document   │────<│    Chunk     │     │  QueryLog      │
│              │     │              │     │                │
│ id           │     │ id           │     │ id             │
│ filename     │     │ document_id  │     │ query_text     │
│ domain       │     │ content      │     │ service_used   │
│ doc_type     │     │ embedding    │     │ response_text  │
│ metadata_json│     │ chunk_index  │     │ sources_json   │
│ file_hash    │     │ page_number  │     │ latency_ms     │
└──────────────┘     └──────────────┘     └────────────────┘

┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│  GuideEntry  │     │ SensorLog    │     │ AutomationRule │
│              │     │              │     │                │
│ id           │     │ id           │     │ id             │
│ domain       │     │ sensor_id    │     │ name           │
│ title        │     │ sensor_type  │     │ trigger_type   │
│ content      │     │ value        │     │ trigger_cond   │
│ tags_json    │     │ unit         │     │ action_type    │
│ version      │     │ recorded_at  │     │ enabled        │
└──────────────┘     └──────────────┘     └────────────────┘

┌──────────────┐     ┌──────────────┐
│  MeshMessage │     │ TTSCache     │
│              │     │              │
│ id           │     │ id           │
│ sender       │     │ text_hash    │
│ text         │     │ backend      │
│ snr          │     │ audio_data   │
│ rssi         │     │ voice        │
│ received_at  │     │ duration_ms  │
└──────────────┘     └──────────────┘

Migration Strategy:
- Alembic manages all schema changes
- Run: alembic upgrade head
- Downgrade: alembic downgrade -1
- New migrations: alembic revision --autogenerate -m "description"
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all VaultMind models."""
    pass


class Document(Base):
    """A source document (PDF, guide, or other reference material)."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False)
    domain = Column(String(100), nullable=True, index=True)
    doc_type = Column(String(50), nullable=False, default="pdf")  # pdf, guide, zim
    file_hash = Column(String(64), nullable=True, unique=True)
    file_size_bytes = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)
    indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_documents_domain_type", "domain", "doc_type"),
    )


class Chunk(Base):
    """A text chunk from a document, ready for embedding/retrieval."""

    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    char_count = Column(Integer, nullable=True)
    embedding_id = Column(String(100), nullable=True)  # reference to FAISS index position
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunks_document", "document_id", "chunk_index"),
    )


class QueryLog(Base):
    """Log of all queries made to VaultMind for analytics and improvement."""

    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    service_used = Column(String(50), nullable=False)  # rag, kiwix, guides, llm
    response_text = Column(Text, nullable=True)
    sources_json = Column(Text, nullable=True)
    model_used = Column(String(200), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_query_logs_created", "created_at"),
        Index("idx_query_logs_service", "service_used"),
    )


class GuideEntry(Base):
    """Structured knowledge guide entry with version tracking."""

    __tablename__ = "guide_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags_json = Column(Text, nullable=True)  # JSON array of tags
    version = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_guides_domain_active", "domain", "active"),
    )


class SensorLog(Base):
    """Time-series log of sensor readings from connected hardware."""

    __tablename__ = "sensor_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False)  # temperature, humidity, voltage, motion
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("idx_sensor_logs_sensor_time", "sensor_id", "recorded_at"),
    )


class MeshMessage(Base):
    """Messages received via Meshtastic mesh network."""

    __tablename__ = "mesh_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String(200), nullable=False)
    text = Column(Text, nullable=False)
    snr = Column(Float, nullable=True)
    rssi = Column(Integer, nullable=True)
    channel = Column(String(100), nullable=True)
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class AutomationRuleModel(Base):
    """Persisted automation rules for hardware/domotics control."""

    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)
    trigger_type = Column(String(50), nullable=False)
    trigger_condition = Column(String(500), nullable=False)
    action_type = Column(String(50), nullable=False)
    action_target = Column(Integer, nullable=False)
    action_state = Column(Boolean, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TTSCache(Base):
    """Cache of previously synthesized TTS audio to avoid recomputation."""

    __tablename__ = "tts_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text_hash = Column(String(64), nullable=False, unique=True, index=True)
    backend = Column(String(50), nullable=False)
    voice = Column(String(100), nullable=True)
    audio_data = Column(LargeBinary, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
