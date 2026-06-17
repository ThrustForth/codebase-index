#!/usr/bin/env python3
"""Test script to compare hybrid search results with different weightings."""

from search import search_codebase

def run_search(query, keyword_weight, semantic_weight, label):
    """Run a search and return formatted results."""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"Query: '{query}'")
    print(f"Weights: keyword={keyword_weight}, semantic={semantic_weight}")
    print('='*60)
    
    try:
        results = search_codebase(
            query, 
            top_k=5, 
            keyword_weight=keyword_weight, 
            semantic_weight=semantic_weight
        )
        
        if not results:
            print("No results found.")
            return
            
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('path', 'unknown')}")
            print(f"   Lines: {result.get('start_line', '?')}-{result.get('end_line', '?')}")
            print(f"   Type: {result.get('type', 'unknown')}")
            # Show first 200 chars of content
            content = result.get('content', '').strip()
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"   Content: {content}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test 1: Keyword-heavy
    run_search(
        "oauth", 
        keyword_weight=0.9, 
        semantic_weight=0.1, 
        label="1. KEYWORD-HEAVY (0.9/0.1)"
    )
    
    # Test 2: Semantic-heavy
    run_search(
        "authentication security", 
        keyword_weight=0.1, 
        semantic_weight=0.9, 
        label="2. SEMANTIC-HEAVY (0.1/0.9)"
    )
    
    # Test 3: Balanced
    run_search(
        "oauth authentication", 
        keyword_weight=0.5, 
        semantic_weight=0.5, 
        label="3. BALANCED (0.5/0.5)"
    )
    
    print(f"\n{'='*60}")
    print("Comparison complete!")
    print('='*60)