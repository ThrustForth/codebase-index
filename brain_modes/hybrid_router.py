"""Hybrid router: auto-detects simple vs complex queries and routes accordingly."""
import re
from pathlib import Path
from typing import Dict, Any

# Thresholds for complexity detection
SIMPLE_KEYWORDS = {
    "status", "hello", "hi", "help", "time", "date", "who", "what is",
    "simple", "basic", "quick", "short", "hello", "hey"
}

COMPLEX_INDICATORS = {
    "analyze", "refactor", "optimize", "implement", "create", "build",
    "design", "architect", "debug", "troubleshoot", "complex", "multi-step"
}

def detect_complexity(query: str) -> str:
    """Return 'simple' or 'complex' based on query analysis."""
    q = query.lower()
    
    # Count complex indicators
    complexity_score = sum(1 for word in COMPLEX_INDICATORS if word in q)
    
    # Check for multi-step patterns
    multi_step_patterns = [
        r"\b(how to|write a|create a|build a)\s+\w+",
        r"\b(refactor|optimize|improve)\s+\w+",
        r"\b(implement|design)\s+\w+",
        r"\band\s+\w+.*and\s+\w+",  # multiple requirements
    ]
    
    for pattern in multi_step_patterns:
        if re.search(pattern, q):
            complexity_score += 2
    
    # Simple queries are short and have no complex indicators
    if complexity_score == 0 and len(query.split()) <= 5:
        return "simple"
    
    return "complex" if complexity_score > 0 else "simple"


def route_query(query: str, **kwargs) -> Dict[str, Any]:
    """Route query to appropriate backend."""
    complexity = detect_complexity(query)
    
    if complexity == "simple":
        return {
            "backend": "ollama",
            "tool": "code_puppy_tool.py",
            "reason": "Simple query detected, using local Ollama"
        }
    else:
        return {
            "backend": "openrouter",
            "tool": "openrouter_proxy.py",
            "reason": "Complex query detected, offloading to OpenRouter"
        }


# For direct testing
if __name__ == "__main__":
    test_queries = [
        "hello",
        "what time is it",
        "help me debug this code",
        "analyze this codebase and suggest improvements",
        "hi there",
        "create a complex refactoring plan"
    ]
    
    for q in test_queries:
        result = route_query(q)
        print(f"Query: {q[:40]:<40} -> {result['backend']}")