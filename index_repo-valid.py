#!/usr/bin/env python3

from __future__ import annotations
from index_repo import search_codebase as _search_codebase
from typing import List, Dict, Any

# Validation added
if not isinstance(top_k, int) or top_k <= 0:
    raise ValueError('top_k must be positive integer')
if not isinstance(query, str) or not query.strip():
    raise ValueError('Query must be non-empty string')
if not isinstance(db_path, str):
    raise TypeError('db_path must be a string')

def search_codebase(query: str, top_k: int = 5, db_path: str = "db", file_ext: str = None, path_pattern: str = None, as_dci: bool = False) -> str | List[Dict[str, Any]]:
    """..."
    # rest of original implementation..."
