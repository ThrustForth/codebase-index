# search.py
from __future__ import annotations
import re
from typing import List, Dict, Any
from index_repo import search_codebase as _search_codebase

# Security limits
MAX_QUERY_LEN = 512
MAX_TOP_K = 100

def _sanitize_query(query: str) -> str:
    """Sanitize user query string to prevent injection attacks."""
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if len(query) > MAX_QUERY_LEN:
        raise ValueError(f"query exceeds maximum length of {MAX_QUERY_LEN} characters")
    # Remove null bytes and control characters
    return ''.join(c for c in query if c.isprintable())

def _clamp_weight(weight: float, name: str) -> float:
    """Clamp weight value to valid range [0.0, 1.0]."""
    if not isinstance(weight, (int, float)):
        raise TypeError(f"{name} must be a number")
    return max(0.0, min(1.0, float(weight)))

def _keyword_score(text: str, query: str) -> float:
    """Calculate keyword matching score for text against query."""
    if not text or not query:
        return 0.0
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    text_words = set(re.findall(r'\b\w+\b', text.lower()))
    if not query_words:
        return 0.0
    intersection = len(query_words & text_words)
    union = len(query_words | text_words)
    if union == 0:
        return 0.0
    return intersection / union

def search_codebase(query: str, top_k: int = 5, db_path: str = "db", file_ext: str = None, path_pattern: str = None,
                   as_dci: bool = False, keyword_weight: float = 0.3, semantic_weight: float = 0.7) -> str | List[Dict[str, Any]]:
    """Hybrid keyword + semantic search.

    Args:
        query: search string
        top_k: number of results
        db_path: path to LanceDB
        file_ext: optional file extension filter
        path_pattern: optional path pattern filter
        as_dci: return <DYNAMIC_CONTEXT> string if True
        keyword_weight: weight for keyword match (0.0‑1.0)
        semantic_weight: weight for semantic similarity (0.0‑1.0)
    """
    # Security checks
    query = _sanitize_query(query)
    keyword_weight = _clamp_weight(keyword_weight, "keyword_weight")
    semantic_weight = _clamp_weight(semantic_weight, "semantic_weight")
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k must be a positive integer")
    if top_k > MAX_TOP_K:
        raise ValueError(f"top_k exceeds maximum of {MAX_TOP_K}")

    # Retrieve a superset for re‑ranking
    search_k = max(top_k * 3, 20)
    results = _search_codebase(query, top_k=search_k, db_path=db_path, file_ext=file_ext, path_pattern=path_pattern)

    for result in results:
        text_content = result.get('content', '')
        keyword_score = _keyword_score(text_content, query)
        # Approximate semantic score by position (first result = 1.0, decay 0.05 per rank)
        semantic_score = max(0.0, 1.0 - (results.index(result) * 0.05))
        combined = (keyword_weight * keyword_score) + (semantic_weight * semantic_score)
        result['_hybrid_score'] = combined
        result['_keyword_score'] = keyword_score
        result['_semantic_score'] = semantic_score

    results.sort(key=lambda x: x.get('_hybrid_score', 0), reverse=True)
    results = results[:top_k]

    for r in results:
        r.pop('_hybrid_score', None)
        r.pop('_keyword_score', None)
        r.pop('_semantic_score', None)

    if as_dci:
        dci = "<DYNAMIC_CONTEXT>\n"
        dci += f"Codebase search results for: {query}\n"
        dci += f"Top-{top_k} results (hybrid), extension: {file_ext or 'all'}\n\n"
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
