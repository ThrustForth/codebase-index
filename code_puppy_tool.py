#!/usr/bin/env python3
"""
Code Puppy Tool - A dedicated tool for codebase search with Brain AI critique.
This can be imported and used as a tool by the Code Puppy agent.
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from search import search_codebase
from index_repo import OllamaEmbedder  # For accessing the embedder if needed
from brain_ai_wrapper import BrainAIWrapper

DB_PATH = "/home/mine/projects/codebase-index/db"

class BrainAICritique:
    """Generate critiques using Ollama."""
    
    def __init__(self, model: str = "phi3"):
        self.model = model
    
    def process(self, code: str) -> str:
        """Generate a critique using Ollama."""
        import subprocess
        
        prompt = (
            "You are an expert Python reviewer. Analyze the following code snippets, "
            "summarize their purpose, point out any potential bugs or edge cases, "
            "and suggest improvements. Return a concise critique.\n\n" + code
        )
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, "-"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            return f"Error running Ollama critique: {e}"
        
        # Fallback – return original code if critique fails
        return code

class CodePuppyTool:
    """Main tool for codebase search with Brain AI processing."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or self._find_project_root()
        self.db_path = Path(self.project_root) / 'db'
        self.brain_wrapper = BrainAIWrapper()
        self.brain_ai = BrainAICritique()
        
        # Ensure index exists
        self._ensure_index()
    
    def _find_project_root(self) -> str:
        """Find the project root by looking for .git or setup.py."""
        cur = Path.cwd()
        while cur != cur.parent:
            if (cur / '.git').is_dir() or (cur / 'setup.py').is_file():
                return str(cur)
            cur = cur.parent
        return str(Path.cwd())
    
    def _ensure_index(self):
        """Ensure the search index exists."""
        if not self.db_path.exists():
            print(f"Building index at {self.db_path}...")
            import subprocess
            subprocess.run([
                sys.executable, 
                str(Path(__file__).parent / 'index_repo.py'),
                '--index',
                '--root', self.project_root
            ], cwd=self.project_root, check=True)
    
    def search(self, query: str, ext: str = ".py", top_k: int = 5) -> str:
        """
        Search the codebase and return formatted snippets.
        
        Args:
            query: The search query
            ext: File extension to filter by
            top_k: Number of results to return
            
        Returns:
            Formatted code snippets
        """
        from search import search_codebase
        
        hits = search_codebase(query, top_k=top_k, db_path=str(self.db_path))
        
        if not hits:
            return 'No code found matching your query.'
        
        snippets = []
        for h in hits:
            text = h.get('text', '')
            path = h.get('path', 'unknown')
            line_start = h.get('line_start', '?')
            line_end = h.get('line_end', '?')
            snippets.append(f'[{path}:{line_start}-{line_end}]\\n{text}')
        
        return '\\n\\n'.join(snippets)
    
    def critique(self, code_snippets: str) -> str:
        """
        Run Brain AI critique on code snippets.
        
        Args:
            code_snippets: The code snippets to critique
            
        Returns:
            The critique from Ollama
        """
        return self.brain_ai.process(code_snippets)
    
    def process_query(self, query: str, ext: str = ".py", top_k: int = 5) -> Dict[str, Any]:
        """
        Process a query through the full pipeline: search -> critique.
        Also persist the critique JSON for future reference.
        
        Args:
            query: The user's search query
            ext: File extension filter
            top_k: Number of search results
            
        Returns:
            Dictionary with results, critique, and metadata
        """
        # Search for code
        code_results = self.search(query, ext, top_k)
        
        if "No code found" in code_results:
            return {
                "query": query,
                "results": code_results,
                "critique": None,
                "error": "No results found"
            }
        
        # Get critique
        critique_result = self.brain_wrapper.critique(code_results)
        
        # Save critique to file for traceability
        try:
            critiques_dir = Path(__file__).parent / "critiques"
            critiques_dir.mkdir(exist_ok=True)
            filename = f"critique_{hash(query) % 10000}.json"
            with open(critiques_dir / filename, "w") as f:
                json.dump({
                    "query": query,
                    "critique": critique_result,
                    "results_snippet": code_results[:200] + "..." if len(code_results) > 200 else code_results
                }, f, indent=2)
        except Exception as e:
            print(f" Failed to save critique: {e}")
        
        return {
            "query": query,
            "results": code_results,
            "critique": critique_result,
            "result_length": len(code_results),
            "critique_length": len(critique_result)
        }
    
    def ask_followup(self, critique: str) -> list:
        """
        Generate follow-up questions based on a critique.
        
        Args:
            critique: The Brain AI critique output
            
        Returns:
            List of suggested follow-up questions
        """
        # Simple heuristic-based follow-up questions
        followups = []
        
        critique_lower = critique.lower()
        
        if "bug" in critique_lower or "issue" in critique_lower or "problem" in critique_lower:
            followups.append("Would you like me to search for similar patterns that might have the same issues?")
            followups.append("Should I look for fixes or improvements to the problematic code?")
        
        if "improvement" in critique_lower or "suggest" in critique_lower or "better" in critique_lower:
            followups.append("Would you like me to implement the suggested improvements?")
            followups.append("Should I search for examples of better implementations in the codebase?")
        
        if "performance" in critique_lower or "slow" in critique_lower or "inefficient" in critique_lower:
            followups.append("Would you like me to profile or optimize the performance-critical sections?")
        
        if "security" in critique_lower or "vulnerability" in critique_lower or "risk" in critique_lower:
            followups.append("Should I conduct a security audit of the related code?")
            followups.append("Would you like me to look for similar security patterns?")
        
        # Default follow-ups if none matched
        if not followups:
            followups = [
                "Would you like me to search for related patterns or usage examples?",
                "Should I generate code based on the critique suggestions?",
                "Would you like to see more detailed analysis of any specific snippet?",
                "Should I search for tests or documentation related to this code?"
            ]
        
        return followups[:3]  # Return top 3

def main():
    """Command-line interface for the tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Puppy Tool - Search codebase with Brain AI critique")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--ext", default=".py", help="File extension to search (default: .py)")
    parser.add_argument("--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--no-critique", action="store_true", help="Skip Brain AI critique")
    
    args = parser.parse_args()
    
    tool = CodePuppyTool()
    result = tool.process_query(args.query, args.ext, args.top)
    
    print(f"\n Code Puppy Tool: {args.query}")
    print(f" Results: {result['result_length']} characters")
    
    if not args.no_critique and result['critique']:
        print(f" Critique: {result['critique_length']} characters")
        print("\n" + "="*50)
        print("BRAIN AI CRITIQUE:")
        print("="*50)
        print(result['critique'])
        print("="*50)
        
        # Show follow-up suggestions
        followups = tool.ask_followup(result['critique'])
        if followups:
            print("\nSuggested follow-up actions:")
            for i, followup in enumerate(followups, 1):
                print(f"  {i}. {followup}")
    else:
        print("\n Results:")
        print("-"*50)
        print(result['results'])
        print("-"*50)

if __name__ == "__main__":
    main()