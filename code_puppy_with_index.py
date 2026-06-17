# code_puppy_with_index.py

import sys
import os
import json
from pathlib import Path
import subprocess

from search import search_codebase

DB_PATH = "/home/mine/projects/codebase-index/db"
BRAIN_AI_ROOT = "/home/mine/projects/brain-ai"

class BrainAICritique:
    def process(self, code: str) -> str:
        """Generate a simple critique using Ollama.
        It receives the aggregated code snippets (as a string) and asks Ollama
        to summarize what the snippets do and suggest improvements.
        """
        # Build a prompt for Ollama
        # Limit prompt size to avoid timeouts with large snippets
        MAX_PROMPT_TOKENS = 1500
        if len(code) > MAX_PROMPT_TOKENS:
            code_to_send = code[:MAX_PROMPT_TOKENS] + " ... [TRUNCATED]"
        else:
            code_to_send = code
        prompt = (
            "You are an expert Python reviewer. Analyze the following code snippets, "
            "summarize their purpose, point out any potential bugs or edge cases, "
            "and suggest improvements. Return a concise critique.\n\n" + code_to_send
        )
        # Call Ollama locally (assumes `ollama` CLI is installed and the model is available)
        try:
            result = subprocess.run(
                ["ollama", "run", "llama3.2:1b", "-"],  # using phi3 as a lightweight model
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

def enrich_prompt(question: str, base: str) -> str:
    hits = search_codebase(question, top_k=5, db_path=DB_PATH)
    snippets = []
    for h in hits:
        text = h.get('text', '')
        path = h.get('path', 'unknown')
        line_start = h.get('line_start', '?')
        line_end = h.get('line_end', '?')
        snippets.append(f'[{path}:{line_start}-{line_end}]\n{text}')
    return f"{base}\n\n# Code from repo\n{'\n'.join(snippets)}\n\nUser: {question}"

def call_cs(prompt: str, ext: str = ".py", top_k: int = 5) -> str:
        # Determine project root (env var or nearest .git / setup.py)
    project_root = os.getenv('PROJECT_ROOT')
    if not project_root:
        # walk up from current dir to find .git or setup.py
        cur = Path.cwd()
        while cur != cur.parent:
            if (cur / '.git').is_dir() or (cur / 'setup.py').is_file():
                project_root = str(cur)
                break
            cur = cur.parent
    if not project_root:
        project_root = str(Path.cwd())
    # Ensure index exists
    db_path = Path(project_root) / 'db'
    if not db_path.exists():
        # Build index
        subprocess.run([sys.executable, 'index_repo.py', '--index', '--root', project_root], cwd=project_root)
    # Run cs with proper flags and DB path
    cs_cmd = f"cs --search {prompt} --ext {ext} --top {top_k} --root {project_root}"
    result = subprocess.run(cs_cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        output = result.stdout.strip()
        if not output:
            return 'No code found matching your query, what would you like me to do?'
        
        # Parse JSON and extract text fields
        try:
            results = json.loads(output)
            snippets = []
            for h in results:
                text = h.get('text', '')
                path = h.get('path', 'unknown')
                line_start = h.get('line_start', '?')
                line_end = h.get('line_end', '?')
                snippets.append(f'[{path}:{line_start}-{line_end}]\n{text}')
            
            if not snippets:
                return 'No code found matching your query, what would you like me to do?'
            
            return '\n\n'.join(snippets)
        except json.JSONDecodeError as e:
            return f'Error parsing code search results: {e}'
    return ""

POST_PROCESSORS = [BrainAICritique()]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python code_puppy_with_index.py \"question\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    print(f"\n🔍 Code Puppy: {question}")
    code = call_cs(question, ".py", 5)

    if code:
        print(f"\n Generated: {len(code)} chars")
        for pp in POST_PROCESSORS:
            print(f"\n Calling Brain AI critique ({pp.__class__.__name__})...")
            before_len = len(code)
            code = pp.process(code)
            after_len = len(code)
            print(f" Brain AI returned {after_len} chars (was {before_len} chars)")

        print(f"\n Brain AI processed: {len(code)} chars")
        print("\n--- START RESULT (first 500 chars) ---")
        if len(code) > 500:
            print(code[:500] + "...\n[truncated]")
        else:
            print(code)
        print("\n--- END RESULT ---")
    else:
        print("⚠️ Empty result")
