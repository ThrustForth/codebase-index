# cp_tool.py - NEW VERSION (use LanceDB)
from index_cli import lance_search

def cp(query: str, ext: str = ".py", top_k: int = 5) -> str:
    """Codebase search with Brain AI critique - uses LanceDB for semantic search"""

    # Use semantic search instead of grep
    results = lance_search(query, top_k=top_k)

    if not results:
        return f"❌ No results found for '{query}'"

    # Format results nicely
    output = f"🔍 Found {len(results)} results for '{query}':\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. `{result['file']}` (similarity: {result['score']:.2f})\n"
        output += f"   {result['snippet'][:200]}...\n\n"

    return output
