"""VaultMind REST API blueprint.

All endpoints follow REST conventions:
- POST /api/query    — Query the knowledge vault
- GET  /api/guides   — List knowledge guide domains
- GET  /api/guides/<domain> — Get guide content
- GET  /api/status   — System diagnostics
- POST /api/tts      — Text-to-speech synthesis
- GET  /api/schema   — Database schema documentation
- GET  /api/db/stats  — Database table statistics
"""

from __future__ import annotations

import hashlib
import time

from flask import Blueprint, current_app, jsonify, request, Response

api_bp = Blueprint("api", __name__)


@api_bp.route("/query", methods=["POST"])
def query():
    """Query the VaultMind knowledge base."""
    from vaultmind.core.router import route_query

    data = request.get_json()
    if not data or not data.get("query"):
        return jsonify({"error": "No query provided"}), 400

    start = time.monotonic()

    result = route_query(
        query=data["query"],
        index_dir=current_app.config["VAULTMIND_INDEX_DIR"],
        model=current_app.config["VAULTMIND_MODEL"],
        kiwix_url=current_app.config["VAULTMIND_KIWIX_URL"],
        guides_dir=current_app.config["VAULTMIND_GUIDES_DIR"],
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    # Log query to database (best-effort, don't fail the response)
    try:
        _log_query(data["query"], result, latency_ms)
    except Exception:
        pass

    return jsonify({
        "answer": result.answer,
        "sources": result.sources,
        "service": result.service,
        "latency_ms": latency_ms,
    })


@api_bp.route("/guides")
def list_guides():
    """List available knowledge guide domains."""
    from vaultmind.services.guides import list_domains

    guides_dir = current_app.config["VAULTMIND_GUIDES_DIR"]
    return jsonify(list_domains(guides_dir))


@api_bp.route("/guides/<domain>")
def guide_content(domain: str):
    """Get the full content of a knowledge guide domain."""
    from vaultmind.services.guides import get_guide_content

    guides_dir = current_app.config["VAULTMIND_GUIDES_DIR"]
    content = get_guide_content(domain, guides_dir)
    if content is None:
        return jsonify({"error": f"Domain '{domain}' not found"}), 404
    return jsonify({"domain": domain, "content": content})


@api_bp.route("/status")
def diagnostics():
    """Run system diagnostics and return results."""
    from vaultmind.services.diagnostics import run_all_diagnostics

    results = run_all_diagnostics(
        index_dir=current_app.config["VAULTMIND_INDEX_DIR"],
        model=current_app.config["VAULTMIND_MODEL"],
        kiwix_url=current_app.config["VAULTMIND_KIWIX_URL"],
        guides_dir=current_app.config["VAULTMIND_GUIDES_DIR"],
    )
    return jsonify({
        "diagnostics": [
            {"name": r.name, "status": r.status, "message": r.message}
            for r in results
        ]
    })


@api_bp.route("/tts", methods=["POST"])
def text_to_speech():
    """Synthesize text to speech and return WAV audio."""
    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "No text provided"}), 400

    try:
        from vaultmind.tts.engine import synthesize

        audio_bytes = synthesize(data["text"])
        return Response(
            audio_bytes,
            mimetype="audio/wav",
            headers={"Content-Disposition": "inline; filename=speech.wav"},
        )
    except Exception as e:
        return jsonify({"error": f"TTS failed: {e}"}), 503


@api_bp.route("/schema")
def schema_docs():
    """Return database schema documentation."""
    from vaultmind.db.schema_docs import explain_schema, SCHEMA_VERSION

    return jsonify({
        "version": SCHEMA_VERSION,
        "schema": explain_schema(),
    })


@api_bp.route("/db/stats")
def db_stats():
    """Return database table statistics."""
    try:
        from vaultmind.db.session import get_db
        from vaultmind.db.schema_docs import get_table_stats

        with get_db() as session:
            stats = get_table_stats(session)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _log_query(query_text: str, result, latency_ms: int):
    """Log a query to the database for analytics."""
    import json
    from vaultmind.db.session import get_db
    from vaultmind.db.models import QueryLog

    with get_db() as session:
        log = QueryLog(
            query_text=query_text,
            service_used=result.service,
            response_text=result.answer[:2000] if result.answer else None,
            sources_json=json.dumps(result.sources) if result.sources else None,
            model_used=current_app.config["VAULTMIND_MODEL"],
            latency_ms=latency_ms,
        )
        session.add(log)
