# index_repo.py
from __future__ import annotations

import sys
import argparse
import os
import glob
import hashlib
import json
from pathlib import Path

import pyarrow as pa
from typing import List, Dict, Any

import numpy as np

from pydantic import Field

import lancedb
import ollama

# Default Ollama model for embeddings
OLLAMA_MODEL = "nomic-embed-text"

# Ensure local imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# External deps – will be installed via requirements.txt
try:
    import lancedb
    from lancedb.embeddings import EmbeddingFunction
    import ollama
except ImportError as e:
    print("Missing dependencies. Install them with: pip install -r requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
DB_DIR = Path(__file__).parent / "db"
TABLE_NAME = "codebase"
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768  # dimension for the nomic model
CHUNK_LINES = 40
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "env", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache"}
SKIP_EXTS = {".pyc", ".pyo", ".so", ".dll", ".exe", ".bin", ".jpg", ".png", ".gif", ".pdf", ".zip", ".tar", ".gz", ".lock"}

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def should_skip(path: Path) -> bool:
    """Return True if a file or directory should be ignored during indexing."""
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in SKIP_EXTS:
        return True
    return False

def file_hash(content: str) -> str:
    """Stable SHA‑256 fingerprint of file contents (used for deduplication)."""
    return hashlib.sha256(content.encode()).hexdigest()

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

def chunk_file(text: str) -> List[Dict[str, Any]]:
    """Split a file into a whole‑file chunk plus smaller line‑based snippets.
    Returns a list of dicts with keys: type, name, content, start_line, end_line.
    """
    lines = text.splitlines()
    chunks: List[Dict[str, Any]] = []
    # Whole file chunk (useful for file‑level relevance)
    chunks.append({
        "type": "file",
        "name": "file",
        "content": text,
        "start_line": 1,
        "end_line": len(lines),
    })
    # Snippet chunks – each CHUNK_LINES long
    for i in range(0, len(lines), CHUNK_LINES):
        snippet = lines[i:i + CHUNK_LINES]
        if len(snippet) < 5:  # ignore very tiny tails
            continue
        chunks.append({
            "type": "snippet",
            "name": f"snippet_{i // CHUNK_LINES + 1}",
            "content": "\n".join(snippet),
            "start_line": i + 1,
            "end_line": min(i + CHUNK_LINES, len(lines)),
        })
    return chunks

# ---------------------------------------------------------------------------
# Embedding via Ollama
# ---------------------------------------------------------------------------
from pydantic import Field

class OllamaEmbedder(EmbeddingFunction):
    model: str = Field(default=OLLAMA_MODEL)
    _dim: int = EMBEDDING_DIM

    def ndim(self) -> int:
        return self._dim

    def ndims(self) -> int:
        return self._dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = ollama.embed(model=self.model, input=texts)
        return resp["embeddings"]

    def compute_query_embeddings(self, query: str) -> List[float]:
        resp = ollama.embed(model=self.model, input=[query])
        return resp["embeddings"][0]

    def compute_source_embeddings(self, text: str) -> List[float]:
        resp = ollama.embed(model=self.model, input=[text])
        return resp["embeddings"][0]

# ---------------------------------------------------------------------------
# Index building (incremental)
# ---------------------------------------------------------------------------
def build_index(root: Path) -> None:
    """Walk ``root`` recursively, embed each chunk, and store in LanceDB.
    Only re-index files that have changed (based on content hash)."""
    db = lancedb.connect(str(DB_DIR))
    embedder = OllamaEmbedder()

    # Create table with file_hash column if it doesn't exist
    if TABLE_NAME in db.list_tables():
        tbl = db.open_table(TABLE_NAME)
        # Check if file_hash column exists
        schema = tbl.schema
        if "file_hash" not in [field.name for field in schema]:
            print(" Adding file_hash column for incremental indexing...")
            # Need to recreate table with new schema
            existing = tbl.to_pandas()
            db.drop_table(TABLE_NAME)
            schema = pa.schema([
                pa.field("path", pa.string()),
                pa.field("line_start", pa.int64()),
                pa.field("line_end", pa.int64()),
                pa.field("text", pa.string()),
                pa.field("file_hash", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), EMBEDDING_DIM)),
            ])
            tbl = db.create_table(TABLE_NAME, schema=schema, mode="overwrite")
            # Re-add existing records with file_hash recomputed
            if len(existing) > 0:
                existing["file_hash"] = existing.apply(lambda r: file_hash(r["text"]), axis=1)
                tbl.add(existing.to_dict(orient="records"))
    else:
        schema = pa.schema([
            pa.field("path", pa.string()),
            pa.field("line_start", pa.int64()),
            pa.field("line_end", pa.int64()),
            pa.field("text", pa.string()),
            pa.field("file_hash", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), EMBEDDING_DIM)),
        ])
        tbl = db.create_table(TABLE_NAME, schema=schema, mode="overwrite")

    # Get existing file hashes for incremental indexing
    existing_files = tbl.to_pandas()
    existing_hashes = set(existing_files["file_hash"].unique()) if len(existing_files) > 0 else set()
    existing_paths = set(existing_files["path"].unique()) if len(existing_files) > 0 else set()

    total_chunks = 0
    new_chunks = 0
    skipped_chunks = 0

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if should_skip(fpath):
                continue
            txt = read_text(fpath)
            if not txt.strip():
                continue
            h = file_hash(txt)
            rel_path = str(fpath.relative_to(root))
            # Skip if file hasn't changed
            if h in existing_hashes:
                skipped_chunks += 1
                continue
            chunks = chunk_file(txt)
            texts = [chunk["content"] for chunk in chunks]
            vectors = embedder.embed(texts)
            records = []
            for chunk, vec in zip(chunks, vectors):
                records.append({
                    "path": rel_path,
                    "line_start": chunk["start_line"],
                    "line_end": chunk["end_line"],
                    "text": chunk["content"],
                    "file_hash": h,
                    "embedding": vec,
                })
            # Upsert: delete old entries for this path then add new ones
            if rel_path in existing_paths:
                tbl.delete(f"path = '{rel_path}'")
            tbl.add(records)

            new_chunks += len(records)
            total_chunks += len(records)

    print(f"Indexed {new_chunks} new chunks, skipped {skipped_chunks} unchanged files")
    print(f"Total: {total_chunks} chunks in {DB_DIR}")

# ---------------------------------------------------------------------------
# Search API
# ---------------------------------------------------------------------------
def search_codebase(query: str, top_k: int = 5, db_path: str = "db", file_ext: str = None, path_pattern: str = None, line_start: int = None, line_end: int = None) -> List[Dict[str, Any]]:
    """Search the index for code snippets matching the query."""
    db = lancedb.connect(str(db_path))
    tbl_name = "codebase"

    tables = db.list_tables()
    if isinstance(tables, list):
        table_names = tables
    else:
        table_names = getattr(tables, "tables", [])

    if tbl_name not in table_names:
        raise RuntimeError(f"No index found at {db_path}. Run --index first.")

    table = db.open_table(tbl_name)
    # Build WHERE clause for filters
    where_clause = None
    if file_ext or path_pattern or line_start is not None or line_end is not None:
        where_parts = []
        if file_ext:
            where_parts.append(f"path LIKE '%{file_ext}'")
        if path_pattern:
            where_parts.append(f"path LIKE '{path_pattern}%'")
        if line_start is not None and line_end is not None:
            where_parts.append(f"line_start >= {line_start} AND line_end <= {line_end}")
        elif line_start is not None:
            where_parts.append(f"line_start >= {line_start}")
        elif line_end is not None:
            where_parts.append(f"line_end <= {line_end}")
        if where_parts:
            where_clause = " AND ".join(where_parts)
    resp = ollama.embed(model=OLLAMA_MODEL, input=[query])
    query_vec = resp["embeddings"][0]
    results = table.search(query_vec)
    if where_clause:
        results = results.where(where_clause)
    results = results.limit(top_k).to_pandas().to_dict(orient="records")

    for r in results:
        r.pop("vector", None)
    return results

# ---------------------------------------------------------------------------
# CLI entry point – also used by ``index_cli.py``
# ---------------------------------------------------------------------------
def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(description="Local codebase indexer & search")
    parser.add_argument("--index", action="store_true", help="Build (or rebuild) the vector index")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--top", type=int, default=5, help="Number of results to return")
    parser.add_argument("--root", type=str, default=".", help="Root directory of the repo to index")
    parser.add_argument("--ext", type=str, help="Filter by file extension (e.g., .py)")
    parser.add_argument("--path", type=str, help="Filter by path pattern (e.g., src/)")
    parser.add_argument("--lines", type=str, help="Filter by line range (e.g., 1-100)")
    args = parser.parse_args(argv)
    if args.index:
        root_path = Path(args.root).resolve()
        print(f" Indexing repository at {root_path}")
        build_index(root_path)
    elif args.search:
        # Parse line range if provided (e.g., 1-100 or 100)
        line_start = None
        line_end = None
        if args.lines:
            if '-' in args.lines:
                parts = args.lines.split('-')
                line_start = int(parts[0])
                line_end = int(parts[1])
            else:
                line_start = int(args.lines)
        results = search_codebase(
            args.search, top_k=args.top, file_ext=args.ext,
            path_pattern=args.path, line_start=line_start, line_end=line_end
        )
        for r in results:
            if isinstance(r.get("embedding"), np.ndarray):
                r['embedding'] = r['embedding'].tolist()
        print(json.dumps(results, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
