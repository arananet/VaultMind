"""VaultMind CLI - the command-line interface for the air-gapped knowledge vault."""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool):
    """VaultMind - Air-gapped knowledge appliance for Scenario Zero."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )


@main.command()
@click.option("--pdf-dir", default="data/pdfs", help="Directory containing PDF files")
@click.option("--index-dir", default="data/vault_index", help="Output index directory")
@click.option("--include-guides", is_flag=True, default=False,
              help="Include bundled knowledge guides in the index")
@click.option("--guides-dir", default="data/guides", help="Knowledge guides directory")
def index(pdf_dir: str, index_dir: str, include_guides: bool, guides_dir: str):
    """Ingest PDFs and knowledge guides into the FAISS vector index."""
    from vaultmind.rag.engine import index_pdfs

    sources = []
    if pdf_dir:
        sources.append(f"PDFs from [bold]{pdf_dir}[/bold]")
    if include_guides:
        sources.append(f"Guides from [bold]{guides_dir}[/bold]")

    console.print(
        Panel(
            f"Indexing: {', '.join(sources)}",
            title="VaultMind Indexer",
            border_style="green",
        )
    )

    chunk_count = index_pdfs(
        pdf_dir, index_dir,
        include_guides=include_guides,
        guides_dir=guides_dir,
    )
    if chunk_count:
        console.print(
            f"[green]Index built successfully: {chunk_count} chunks stored in {index_dir}[/green]"
        )
    else:
        console.print(
            "[yellow]No content found to index. "
            "Add PDFs to data/pdfs/ or use --include-guides.[/yellow]"
        )


@main.command()
@click.argument("user_query")
@click.option("--model", default="llama3.1:8b-instruct-q4_K_M", help="Ollama model name")
@click.option("--index-dir", default="data/vault_index", help="FAISS index directory")
@click.option("--kiwix-url", default="http://localhost:8888", help="Kiwix server URL")
@click.option("--no-rag", is_flag=True, help="Skip RAG and query LLM directly")
@click.option("--no-kiwix", is_flag=True, help="Skip Kiwix search")
@click.option("--no-guides", is_flag=True, help="Skip knowledge guide search")
def query(
    user_query: str,
    model: str,
    index_dir: str,
    kiwix_url: str,
    no_rag: bool,
    no_kiwix: bool,
    no_guides: bool,
):
    """Query the VaultMind knowledge base."""
    from vaultmind.core.router import route_query

    console.print(
        Panel(
            f"[bold]Query:[/bold] {user_query}",
            title="VaultMind",
            border_style="blue",
        )
    )

    result = route_query(
        query=user_query,
        index_dir=index_dir,
        model=model,
        kiwix_url=kiwix_url,
        use_rag=not no_rag,
        use_kiwix=not no_kiwix,
        use_guides=not no_guides,
    )

    # Display the answer
    console.print(Markdown(result.answer))

    # Display source info
    if result.sources:
        source_text = "\n".join(f"  - {s}" for s in result.sources)
        console.print(
            Panel(
                f"[dim]Service: {result.service}\nSources:\n{source_text}[/dim]",
                title="Vault Sources",
                border_style="dim",
            )
        )


@main.command()
@click.option("--model", default="llama3.1:8b-instruct-q4_K_M", help="Ollama model name")
@click.option("--index-dir", default="data/vault_index", help="FAISS index directory")
@click.option("--kiwix-url", default="http://localhost:8888", help="Kiwix server URL")
def chat(model: str, index_dir: str, kiwix_url: str):
    """Start an interactive chat session with VaultMind."""
    from vaultmind.core.router import route_query

    console.print(
        Panel(
            "[bold]VaultMind Interactive Mode[/bold]\n"
            "Type your query and press Enter. Type 'exit' or Ctrl+C to quit.\n"
            "Type 'guides' to list available knowledge domains.",
            title="Protocol Zero",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = console.input("[bold green]vault>[/bold green] ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]VaultMind shutting down.[/dim]")
            break

        if user_input.strip().lower() in ("exit", "quit", "q"):
            console.print("[dim]VaultMind shutting down.[/dim]")
            break

        if user_input.strip().lower() == "guides":
            _show_guides()
            continue

        if not user_input.strip():
            continue

        result = route_query(
            query=user_input,
            index_dir=index_dir,
            model=model,
            kiwix_url=kiwix_url,
        )

        console.print()
        console.print(Markdown(result.answer))

        if result.sources:
            source_text = ", ".join(result.sources)
            console.print(f"\n[dim]({result.service}: {source_text})[/dim]\n")


@main.command()
def guides():
    """List available knowledge guide domains and topics."""
    _show_guides()


def _show_guides():
    """Display knowledge guide domains in a table."""
    from vaultmind.services.guides import list_domains

    domains = list_domains()
    table = Table(title="VaultMind Knowledge Guides", border_style="green")
    table.add_column("Domain", style="bold green")
    table.add_column("Topics")
    table.add_column("Status")

    for domain, info in sorted(domains.items()):
        status = "[green]Available[/green]" if info["available"] else "[dim]Missing[/dim]"
        table.add_row(domain.title(), info["topics"], status)

    console.print(table)


@main.command()
@click.option("--index-dir", default="data/vault_index", help="FAISS index directory")
@click.option("--kiwix-url", default="http://localhost:8888", help="Kiwix server URL")
@click.option("--model", default="llama3.1:8b-instruct-q4_K_M", help="Ollama model name")
def diagnostics(index_dir: str, kiwix_url: str, model: str):
    """Run pre-flight diagnostics on all VaultMind services."""
    from vaultmind.services.diagnostics import run_all_diagnostics

    console.print(
        Panel(
            "[bold]Running VaultMind Diagnostics...[/bold]",
            title="System Check",
            border_style="blue",
        )
    )

    results = run_all_diagnostics(
        index_dir=index_dir,
        kiwix_url=kiwix_url,
        model=model,
    )

    table = Table(border_style="blue")
    table.add_column("Service", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    status_icons = {
        "ok": "[green]OK[/green]",
        "warn": "[yellow]WARN[/yellow]",
        "fail": "[red]FAIL[/red]",
    }

    ok_count = 0
    warn_count = 0
    fail_count = 0

    for r in results:
        icon = status_icons.get(r.status, r.status)
        table.add_row(r.name, icon, r.message)
        if r.status == "ok":
            ok_count += 1
        elif r.status == "warn":
            warn_count += 1
        else:
            fail_count += 1

    console.print(table)

    summary_parts = [f"[green]{ok_count} OK[/green]"]
    if warn_count:
        summary_parts.append(f"[yellow]{warn_count} WARN[/yellow]")
    if fail_count:
        summary_parts.append(f"[red]{fail_count} FAIL[/red]")
    console.print(f"\nSummary: {' | '.join(summary_parts)}")

    if fail_count:
        console.print("[red]Critical services unavailable. VaultMind may not function correctly.[/red]")
    elif warn_count:
        console.print("[yellow]Some services unavailable. Core functionality should work.[/yellow]")
    else:
        console.print("[green]All systems operational. VaultMind is ready.[/green]")


@main.command()
@click.option("--port", default=8080, help="Port to serve on")
@click.option("--mbtiles", default=None, help="Path to MBTiles file for map tiles")
@click.option("--index-dir", default="data/vault_index", help="FAISS index directory")
@click.option("--model", default="llama3.1:8b-instruct-q4_K_M", help="Ollama model name")
def serve(port: int, mbtiles: str, index_dir: str, model: str):
    """Start the VaultMind web server."""
    from flask import Flask, jsonify, request

    app = Flask(__name__)

    @app.route("/")
    def home():
        return """<!DOCTYPE html>
<html><head><title>VaultMind</title>
<style>
    body { font-family: monospace; background: #0a0a0a; color: #00ff41; max-width: 800px; margin: 50px auto; padding: 20px; }
    h1 { border-bottom: 1px solid #00ff41; padding-bottom: 10px; }
    textarea { width: 100%; height: 80px; background: #111; color: #00ff41; border: 1px solid #00ff41; padding: 10px; font-family: monospace; }
    button { background: #00ff41; color: #0a0a0a; border: none; padding: 10px 20px; cursor: pointer; font-family: monospace; font-weight: bold; margin: 5px; }
    button:hover { background: #00cc33; }
    #result { white-space: pre-wrap; margin-top: 20px; padding: 20px; border: 1px solid #333; min-height: 100px; }
    .status { color: #666; font-size: 0.8em; margin-top: 10px; }
    .domains { display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0; }
    .domain { background: #1a1a1a; border: 1px solid #333; padding: 3px 8px; font-size: 0.8em; cursor: pointer; }
    .domain:hover { border-color: #00ff41; }
</style></head><body>
<h1>VAULTMIND // PROTOCOL ZERO</h1>
<p>Air-gapped knowledge appliance. All processing is local. Zero telemetry.</p>
<div class="domains">
    <span class="domain" onclick="setQuery('medicine')">Medicine</span>
    <span class="domain" onclick="setQuery('chemistry')">Chemistry</span>
    <span class="domain" onclick="setQuery('energy fuel')">Energy</span>
    <span class="domain" onclick="setQuery('agriculture')">Agriculture</span>
    <span class="domain" onclick="setQuery('water purification')">Water</span>
    <span class="domain" onclick="setQuery('construction')">Construction</span>
    <span class="domain" onclick="setQuery('radio communications')">Comms</span>
    <span class="domain" onclick="setQuery('metalworking')">Metalwork</span>
    <span class="domain" onclick="setQuery('navigation')">Navigation</span>
    <span class="domain" onclick="setQuery('security defense')">Security</span>
</div>
<textarea id="q" placeholder="Enter your survival query..."></textarea><br>
<button onclick="ask()">QUERY VAULT</button>
<button onclick="getDiag()">DIAGNOSTICS</button>
<div id="result"></div>
<div class="status" id="status"></div>
<script>
function setQuery(domain) {
    document.getElementById('q').value = 'What are the key procedures for ' + domain + '?';
    document.getElementById('q').focus();
}
async function ask() {
    const q = document.getElementById('q').value;
    if (!q) return;
    document.getElementById('result').textContent = 'Searching vault...';
    document.getElementById('status').textContent = '';
    try {
        const r = await fetch('/api/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:q})});
        const d = await r.json();
        document.getElementById('result').textContent = d.answer;
        document.getElementById('status').textContent = 'Service: ' + d.service + ' | Sources: ' + (d.sources||[]).join(', ');
    } catch(e) {
        document.getElementById('result').textContent = 'Error: ' + e.message;
    }
}
async function getDiag() {
    document.getElementById('result').textContent = 'Running diagnostics...';
    try {
        const r = await fetch('/api/status');
        const d = await r.json();
        let text = 'VAULTMIND SYSTEM STATUS\\n' + '='.repeat(40) + '\\n\\n';
        for (const check of d.diagnostics || []) {
            const icon = check.status === 'ok' ? '[OK]' : check.status === 'warn' ? '[WARN]' : '[FAIL]';
            text += icon + ' ' + check.name + ': ' + check.message + '\\n';
        }
        document.getElementById('result').textContent = text;
    } catch(e) {
        document.getElementById('result').textContent = 'Diagnostics error: ' + e.message;
    }
}
document.getElementById('q').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); }
});
</script></body></html>"""

    @app.route("/api/query", methods=["POST"])
    def api_query():
        from vaultmind.core.router import route_query

        data = request.get_json()
        user_query = data.get("query", "")
        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        result = route_query(query=user_query, index_dir=index_dir, model=model)
        return jsonify(
            {
                "answer": result.answer,
                "sources": result.sources,
                "service": result.service,
            }
        )

    @app.route("/api/guides")
    def api_guides():
        from vaultmind.services.guides import list_domains

        return jsonify(list_domains())

    @app.route("/api/guides/<domain>")
    def api_guide_content(domain: str):
        from vaultmind.services.guides import get_guide_content

        content = get_guide_content(domain)
        if content is None:
            return jsonify({"error": f"Domain '{domain}' not found"}), 404
        return jsonify({"domain": domain, "content": content})

    @app.route("/api/status")
    def api_status():
        from vaultmind.services.diagnostics import run_all_diagnostics

        results = run_all_diagnostics(index_dir=index_dir, model=model)
        return jsonify({
            "diagnostics": [
                {"name": r.name, "status": r.status, "message": r.message}
                for r in results
            ]
        })

    # Mount tile server if MBTiles provided
    if mbtiles:
        from vaultmind.gis.tiles import MBTilesReader

        reader = MBTilesReader(mbtiles)
        console.print(f"[green]Map tiles loaded from {mbtiles}[/green]")

    console.print(
        Panel(
            f"[bold]VaultMind Web Server[/bold]\nListening on http://0.0.0.0:{port}",
            title="Protocol Zero",
            border_style="green",
        )
    )
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
