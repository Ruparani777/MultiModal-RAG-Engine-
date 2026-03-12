#!/usr/bin/env python3
"""
ingest.py — CLI script to ingest documents into the knowledge base.

Usage:
    python scripts/ingest.py path/to/file.pdf
    python scripts/ingest.py path/to/docs/folder/
    python scripts/ingest.py file1.pdf file2.png file3.txt
"""
import sys
from pathlib import Path

# Make src importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table
from src.ingestion.pipeline import ingest_directory, ingest_document

console = Console()


def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python scripts/ingest.py <file_or_folder> [...]")
        sys.exit(1)

    results = []

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            console.print(f"[red]Not found:[/] {arg}")
            continue

        if path.is_dir():
            console.print(f"\n[bold blue]Ingesting directory:[/] {path}")
            dir_results = ingest_directory(path)
            results.extend(dir_results)
        else:
            console.print(f"\n[bold blue]Ingesting file:[/] {path.name}")
            try:
                result = ingest_document(path)
                results.append(result)
            except Exception as e:
                console.print(f"[red]Error:[/] {e}")

    if results:
        table = Table(title="Ingestion Summary", show_header=True, header_style="bold magenta")
        table.add_column("Document", style="cyan")
        table.add_column("Type")
        table.add_column("Text Chunks", justify="right")
        table.add_column("Image Chunks", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Time (s)", justify="right")

        for r in results:
            table.add_row(
                r.doc_name,
                r.doc_type.value,
                str(r.text_chunks),
                str(r.image_chunks),
                str(r.total_chunks),
                f"{r.processing_time_sec:.2f}",
            )

        console.print(table)
        console.print(f"\n[bold green]✓ Ingested {len(results)} document(s) successfully[/]")


if __name__ == "__main__":
    main()
