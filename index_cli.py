# index_repo.py
from __future__ import annotations

import argparse
import os
import glob
from pathlib import Path
from typing import List, Dict, Any

import lancedb
import ollama

# Default Ollama model for embeddings
OLLAMA_MODEL = "nomic-embed-text"

# Directories to ignore
IGNORE_DIRS = {".git", "node_modules", "vendor", "__pycache__", "venv", ".venv"}

# Max file size (1 MB)
MAX_FILE_SIZE = 1024 * 1024

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings from local Ollama."""
    embeddings = []
    for text in texts:
        resp = ollama.embed(model=OLLAMA_MODEL, input=[text])
        embeddings.extend(resp["embeddings"])
    return embeddings

def chunk_code_file(path: Path) -> List[Dict[str, Any]]:
    """
    Simple chunking: one chunk per function/class, plus a whole-file chunk.
    For now, we just use whole-file chunks split by lines.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return []

    if len(content) > MAX_FILE_SIZE:
        return []

    lines = content.splitlines()
    chunks = []

    # Whole file as one chunk
    chunks.append({
        "path": str(path),
        "start_line": 1,
        "end_line": len(lines),
        "snippet": content,
    })

    # Optional: split by blank lines for rough snippets
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "" or i == len(lines) - 1:
            if i - start > 10:
                snippet = "\n".join(lines[start:i+1])
                chunks.append({
                    "path": str(path),
                    "start_line": start + 1,
                    "end_line": i + 1,
                    "snippet": snippet,
                })
            start = i + 1

    return chunks

def scan_repo(root: str) -> List[Path]:
    """Scan a Git repo for Python/JS/TS files, ignoring some dirs."""
    root_path = Path(root).resolve()
    files: List[Path] = []

    for pattern in ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"]:
        for path in root_path.glob(pattern):
            if any(IGNORE_DIR in path.parts for IGNORE_DIR in IGNORE_DIRS):
                continue
            if path.is_file():
                files.append(path)

    return files

def build_index(root: str, db_path: str = "db") -> None:
    """Build or rebuild the LanceDB index for a repo."""
    root_path = Path(root).resolve()
    db_dir = Path(db_path)
    db_dir.mkdir(parents=True, exist_ok=True)

    db = lancedb.connect(str(db_dir))

    files = scan_repo(root)
    print(f"Found {len(files)} files to index.")

    all_chunks: List[Dict[str, Any]] = []
    for f in files:
        chunks = chunk_code_file(f)
        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks.")

    # Embed all snippets
    texts = [c["snippet"] for c in all_chunks]
    print("Generating embeddings...")
    embeddings = get_embeddings(texts)

    # Build vector table
    data = []
    for i, chunk in enumerate(all_chunks):
        chunk["vector"] = embeddings[i]
        data.append(chunk)

    if len(data) == 0:
        print("No chunks to index.")
        return

    # Create or overwrite table
    tbl_name = "code_chunks"

    if tbl_name in db.list_tables():
        db.drop_table(tbl_name)

    table = db.create_table(
        tbl_name,
        data=data,
        mode="overwrite",
    )

    print(f"Index saved to {db_dir}")

def search_codebase(query: str, top_k: int = 5, db_path: str = "db") -> List[Dict[str, Any]]:
    """Search the index for code snippets matching the query."""
    db = lancedb.connect(str(db_path))
    tbl_name = "code_chunks"

    tables = db.list_tables()
    # Handle both list-like and page_token-like return types
    if isinstance(tables, list):
        table_names = tables
    else:
        # Newer API: tables.tables is a list
        table_names = getattr(tables, "tables", [])

    if tbl_name not in table_names:
        raise RuntimeError(f"No index found at {db_path}. Run --index first.")

    table = db.open_table(tbl_name)

    resp = ollama.embed(model=OLLAMA_MODEL, input=[query])
    query_vec = resp["embeddings"][0]

    results = (
        table.search(query_vec)
        .limit(top_k)
        .to_pandas()
        .to_dict(orient="records")
    )

    for r in results:
        r.pop("vector", None)

    return results

def main(argv=None):
    parser = argparse.ArgumentParser(description="Local codebase indexer using LanceDB + Ollama.")
    parser.add_argument("--index", action="store_true", help="Build/rebuild the index.")
    parser.add_argument("--search", nargs="+", metavar="QUERY", help="Search the index.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done, without doing it.")

    args = parser.parse_args(argv)

    # Default to current directory
    root = os.getcwd()
    db_path = os.path.join(os.getcwd(), "db")

    if args.index:
        if args.dry_run:
            print(f"Would index repo at {root}")
            return
        build_index(root, db_path)

    if args.search:
        query = " ".join(args.search)
        if args.dry_run:
            print(f"Would search for: {query}")
            return
        hits = search_codebase(query, top_k=5, db_path=db_path)
        for i, h in enumerate(hits):
            print(f"[{i+1}] {h['path']}:{h['start_line']}-{h['end_line']}")
            print(h['snippet'])
            print("-" * 40)


if __name__ == "__main__":
    main()
