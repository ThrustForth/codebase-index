# search.py
from index_repo import search_codebase as _search_codebase

def search_codebase(query: str, top_k: int = 5, db_path: str = "db"):
    return _search_codebase(query, top_k=top_k, db_path=db_path)
