#!/usr/bin/env python3
"""
query.py — CLI script to query the knowledge base.

Usage:
    python scripts/query.py "What is the main topic of the documents?"
    python scripts/query.py "Describe the charts in the report" --top-k 8
    python scripts/query.py "Summarize key findings" --no-images
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.generation.generator import generate
from src.retrieval.retriever import retrieve

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Query the MultiModal RAG knowledge base")
    parser.add_argument("query", help="Your question")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve")
    parser.add_argument("--no-images", action="store_true", help="Exclude image context")
    args = parser.parse_args()

    console.print(f"\n[bold cyan]Query:[/] {args.query}")
    console.print(f"[dim]Retrieving top-{args.top_k} chunks…[/]\n")

    chunks = retrieve(
        query=args.query,
        top_k=args.top_k,
        include_images=not args.no_images,
    )

    if not chunks:
        console.print("[yellow]No relevant chunks found. Have you ingested any documents?[/]")
        return

    # Show retrieved sources
    table = Table(title="Retrieved Context", show_header=True, header_style="bold blue")
    table.add_column("#", width=3)
    table.add_column("Source", style="cyan")
    table.add_column("Type")
    table.add_column("Page")
    table.add_column("Score", justify="right")

    for i, chunk in enumerate(chunks, 1):
        table.add_row(
            str(i),
            chunk.doc_name,
            chunk.chunk_type.value,
            str(chunk.page_number) if chunk.page_number else "—",
            f"{chunk.score:.3f}",
        )
    console.print(table)
    console.print()

    # Generate answer
    console.print("[dim]Generating answer…[/]\n")
    response = generate(args.query, chunks)

    console.print(
        Panel(
            response.answer,
            title="[bold green]Answer[/]",
            border_style="green",
        )
    )
    console.print(f"\n[dim]Model: {response.model_used} | Time: {response.processing_time_sec:.2f}s[/]")


if __name__ == "__main__":
    main()
