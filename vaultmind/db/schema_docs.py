"""Schema documentation and introspection for VaultMind database.

Provides human-readable descriptions of the data model to facilitate
upgrades, migrations, and understanding by future maintainers.
"""

from __future__ import annotations

from vaultmind.db.models import Base

SCHEMA_VERSION = "1.0"

TABLE_DESCRIPTIONS = {
    "documents": {
        "purpose": "Source documents (PDFs, guides, ZIM extracts) indexed into the knowledge vault",
        "key_columns": {
            "filename": "Original filename of the source document",
            "domain": "Knowledge domain (medicine, energy, agriculture, etc.)",
            "doc_type": "Type: 'pdf', 'guide', or 'zim'",
            "file_hash": "SHA-256 hash for deduplication and integrity checking",
            "indexed": "Whether this document has been chunked and embedded",
        },
        "relationships": "Has many Chunks (one-to-many, cascade delete)",
        "indexes": "domain + doc_type composite index for filtered queries",
    },
    "chunks": {
        "purpose": "Text chunks from documents, ready for vector embedding and retrieval",
        "key_columns": {
            "document_id": "Foreign key to parent document",
            "content": "The actual text content of this chunk",
            "chunk_index": "Sequential position within the document",
            "page_number": "Source page number (for PDFs)",
            "embedding_id": "Reference to position in FAISS vector index",
        },
        "relationships": "Belongs to Document (many-to-one)",
        "indexes": "document_id + chunk_index composite for ordered retrieval",
    },
    "query_logs": {
        "purpose": "Audit log of all queries for analytics, debugging, and usage patterns",
        "key_columns": {
            "query_text": "The user's original query",
            "service_used": "Which service answered: 'rag', 'kiwix', 'guides', 'llm'",
            "latency_ms": "Response time in milliseconds",
            "model_used": "LLM model name used for inference",
        },
        "relationships": "None (standalone log table)",
        "indexes": "created_at for time-range queries; service_used for analytics",
    },
    "guide_entries": {
        "purpose": "Structured knowledge guide entries with versioning for updates",
        "key_columns": {
            "domain": "Survival domain (medicine, energy, etc.)",
            "title": "Guide entry title",
            "content": "Full Markdown content",
            "version": "Version number for tracking updates",
            "active": "Soft delete flag",
        },
        "relationships": "None",
        "indexes": "domain + active composite for filtered listing",
    },
    "sensor_logs": {
        "purpose": "Time-series data from connected sensors (temperature, voltage, etc.)",
        "key_columns": {
            "sensor_id": "Unique identifier for the sensor",
            "sensor_type": "Type: 'temperature', 'humidity', 'voltage', 'motion', 'light'",
            "value": "Numeric reading value",
            "unit": "Unit of measurement (°C, V, %, lux)",
        },
        "relationships": "None (time-series append-only)",
        "indexes": "sensor_id + recorded_at composite for time-range queries per sensor",
    },
    "mesh_messages": {
        "purpose": "Messages received via Meshtastic LoRa mesh network",
        "key_columns": {
            "sender": "Sender node ID or name",
            "text": "Message content",
            "snr": "Signal-to-noise ratio (link quality indicator)",
            "rssi": "Received signal strength indicator",
        },
        "relationships": "None",
        "indexes": "received_at for chronological listing",
    },
    "automation_rules": {
        "purpose": "Domotics automation rules for hardware control",
        "key_columns": {
            "trigger_condition": "e.g., 'temperature > 30' or 'time == 06:00'",
            "action_type": "'gpio', 'relay', or 'alert'",
            "action_target": "Pin or relay number",
            "enabled": "Whether the rule is active",
        },
        "relationships": "None",
        "indexes": "name unique constraint",
    },
    "tts_cache": {
        "purpose": "Cache of synthesized TTS audio to avoid recomputation",
        "key_columns": {
            "text_hash": "SHA-256 hash of input text for lookup",
            "backend": "TTS backend used (piper, chatterbox, kokoro, espeak)",
            "audio_data": "Binary WAV audio data",
            "duration_ms": "Audio duration in milliseconds",
        },
        "relationships": "None",
        "indexes": "text_hash unique index for cache lookup",
    },
}


def explain_schema() -> str:
    """Generate a human-readable schema explanation."""
    lines = [
        f"VaultMind Database Schema v{SCHEMA_VERSION}",
        "=" * 50,
        "",
    ]

    for table_name, info in TABLE_DESCRIPTIONS.items():
        lines.append(f"Table: {table_name}")
        lines.append(f"  Purpose: {info['purpose']}")
        lines.append("  Columns:")
        for col, desc in info["key_columns"].items():
            lines.append(f"    - {col}: {desc}")
        lines.append(f"  Relationships: {info['relationships']}")
        lines.append(f"  Indexes: {info['indexes']}")
        lines.append("")

    return "\n".join(lines)


def get_table_stats(session) -> dict[str, int]:
    """Get row counts for all tables."""
    from sqlalchemy import inspect, text

    inspector = inspect(session.bind)
    stats = {}
    for table_name in inspector.get_table_names():
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        stats[table_name] = result.scalar()
    return stats
