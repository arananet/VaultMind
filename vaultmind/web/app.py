"""Flask application factory for VaultMind web server.

Follows the Flask app factory pattern for testability and configuration
management. Blueprints separate API routes by concern.
"""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from vaultmind.web.api import api_bp


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration overrides.
    """
    # Determine static folder — use built React frontend if available
    static_dir = Path(__file__).parent.parent / "static"
    if not static_dir.is_dir():
        static_dir = None

    app = Flask(
        __name__,
        static_folder=str(static_dir) if static_dir else None,
        static_url_path="" if static_dir else None,
    )

    # Default config
    app.config.update(
        VAULTMIND_INDEX_DIR=os.environ.get("VAULTMIND_INDEX_DIR", "data/vault_index"),
        VAULTMIND_MODEL=os.environ.get("VAULTMIND_MODEL", "qwen3:8b"),
        VAULTMIND_KIWIX_URL=os.environ.get("VAULTMIND_KIWIX_URL", "http://localhost:8888"),
        VAULTMIND_GUIDES_DIR=os.environ.get("VAULTMIND_GUIDES_DIR", "data/guides"),
        VAULTMIND_DATABASE_URL=os.environ.get("VAULTMIND_DATABASE_URL", "sqlite:///data/vaultmind.db"),
    )

    if config:
        app.config.update(config)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    # Serve React frontend for non-API routes
    if static_dir and static_dir.is_dir():
        @app.route("/")
        @app.route("/<path:path>")
        def serve_frontend(path=""):
            index = static_dir / "index.html"
            static_file = static_dir / path
            if static_file.is_file() and path:
                return app.send_static_file(path)
            if index.is_file():
                return app.send_static_file("index.html")
            return _fallback_ui()
    else:
        @app.route("/")
        def index():
            return _fallback_ui()

    return app


def _fallback_ui() -> str:
    """Minimal fallback UI when React build is not available."""
    return """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VaultMind</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'JetBrains Mono',monospace;background:#0a0a0a;color:#e0e0e0;max-width:800px;margin:0 auto;padding:24px}
h1{color:#00e639;font-size:1.25rem;border-bottom:1px solid #2a2a2a;padding-bottom:12px;margin-bottom:24px}
textarea{width:100%;height:80px;background:#111;color:#e0e0e0;border:1px solid #2a2a2a;padding:12px;font-family:inherit;font-size:.875rem;border-radius:8px;resize:vertical}
textarea:focus{border-color:#00e639;outline:none}
button{background:#00e639;color:#0a0a0a;border:none;padding:8px 20px;border-radius:4px;font-family:inherit;font-weight:600;cursor:pointer;margin:8px 4px 8px 0}
button:hover{background:#00b82e}
#result{white-space:pre-wrap;margin-top:16px;padding:16px;border:1px solid #2a2a2a;border-radius:8px;min-height:100px;line-height:1.6}
.meta{font-size:.75rem;color:#666;margin-top:8px}
</style></head><body>
<h1>VAULTMIND // PROTOCOL ZERO</h1>
<p style="color:#999;margin-bottom:16px">Air-gapped knowledge appliance. All processing is local.</p>
<textarea id="q" placeholder="Enter your survival query..."></textarea><br>
<button onclick="ask()">QUERY VAULT</button>
<button onclick="getDiag()">DIAGNOSTICS</button>
<div id="result"></div>
<div class="meta" id="meta"></div>
<script>
async function ask(){const q=document.getElementById('q').value;if(!q)return;document.getElementById('result').textContent='Searching vault...';document.getElementById('meta').textContent='';try{const r=await fetch('/api/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q})});const d=await r.json();document.getElementById('result').textContent=d.answer;document.getElementById('meta').textContent='Service: '+d.service+' | Sources: '+(d.sources||[]).join(', ');}catch(e){document.getElementById('result').textContent='Error: '+e.message;}}
async function getDiag(){document.getElementById('result').textContent='Running...';try{const r=await fetch('/api/status');const d=await r.json();let t='SYSTEM STATUS\\n'+'='.repeat(40)+'\\n';for(const c of d.diagnostics||[]){t+=(c.status==='ok'?'[OK]':c.status==='warn'?'[WARN]':'[FAIL]')+' '+c.name+': '+c.message+'\\n';}document.getElementById('result').textContent=t;}catch(e){document.getElementById('result').textContent='Error: '+e.message;}}
document.getElementById('q').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();ask();}});
</script></body></html>"""
