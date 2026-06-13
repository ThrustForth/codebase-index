# search.py
from __future__ import annotations
from index_repo import search_codebase as _search_codebase
from typing import List, Dict, Any

def search_codebase(query: str, top_k: int = 5, db_path: str = "db", file_ext: str = None, path_pattern: str = None, as_dci: bool = False) -> str | List[Dict[str, Any]]:
    """Search the codebase index and return results.

    Args:
        query: Search query string
        top_k: Number of results to return
        db_path: Path to LanceDB database
        file_ext: Filter by file extension (e.g., ".py")
        path_pattern: Filter by path pattern
        as_dci: If True, return formatted <DYNAMIC_CONTEXT> string

    Returns:
        List of result dicts, or DCI-formatted string if as_dci=True
    """
    results = _search_codebase(query, top_k=top_k, db_path=db_path, file_ext=file_ext, path_pattern=path_pattern)

    if as_dci:
        # Format as DCI context injection
        dci = "<DYNAMIC_CONTEXT>\n"
        dci += f"Codebase search results for: {query}\n"
        dci += f"Top-{top_k} results, extension: {file_ext or 'all'}\n\n"

        for i, r in enumerate(results, 1):
            dci += f"=== Result {i} ===\n"
            dci += f"File: {r.get('path', 'unknown')}\n"
            dci += f"Type: {r.get('type', 'unknown')}\n"
            dci += f"Lines: {r.get('start_line', '?')}-{r.get('end_line', '?')}\n"
            dci += "Content:\n"
            dci += r.get('content', '') + "\n\n"

        dci += "</DYNAMIC_CONTEXT>"
        return dci

    return results
