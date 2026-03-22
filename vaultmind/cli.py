"""VaultMind CLI - the command-line interface for the air-gapped knowledge vault."""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

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
def index(pdf_dir: str, index_dir: str):
    """Ingest PDFs and build the local FAISS vector index."""
    from vaultmind.rag.engine import index_pdfs

    console.print(
        Panel(
            f"Indexing PDFs from [bold]{pdf_dir}[/bold]...",
            title="VaultMind Indexer",
            border_style="green",
        )
    )

    chunk_count = index_pdfs(pdf_dir, index_dir)
    if chunk_count:
        console.print(
            f"[green]Index built successfully: {chunk_count} chunks stored in {index_dir}[/green]"
        )
    else:
        console.print("[yellow]No PDFs found. Add PDF files to the data/pdfs/ directory.[/yellow]")


@main.command()
@click.argument("user_query")
@click.option("--model", default="llama3.1:8b-instruct-q4_K_M", help="Ollama model name")
@click.option("--index-dir", default="data/vault_index", help="FAISS index directory")
@click.option("--kiwix-url", default="http://localhost:8888", help="Kiwix server URL")
@click.option("--no-rag", is_flag=True, help="Skip RAG and query LLM directly")
@click.option("--no-kiwix", is_flag=True, help="Skip Kiwix search")
def query(
    user_query: str,
    model: str,
    index_dir: str,
    kiwix_url: str,
    no_rag: bool,
    no_kiwix: bool,
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
            "Type your query and press Enter. Type 'exit' or Ctrl+C to quit.",
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
    button { background: #00ff41; color: #0a0a0a; border: none; padding: 10px 20px; cursor: pointer; font-family: monospace; font-weight: bold; }
    #result { white-space: pre-wrap; margin-top: 20px; padding: 20px; border: 1px solid #333; }
</style></head><body>
<h1>VAULTMIND // PROTOCOL ZERO</h1>
<p>Air-gapped knowledge appliance. All processing is local.</p>
<textarea id="q" placeholder="Enter your query..."></textarea><br><br>
<button onclick="ask()">QUERY VAULT</button>
<div id="result"></div>
<script>
async function ask() {
    const q = document.getElementById('q').value;
    document.getElementById('result').textContent = 'Searching vault...';
    const r = await fetch('/api/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:q})});
    const d = await r.json();
    document.getElementById('result').textContent = d.answer + '\\n\\n--- Sources: ' + (d.sources||[]).join(', ');
}
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
