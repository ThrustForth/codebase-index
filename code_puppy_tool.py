#!/usr/bin/env python3
"""
Code Puppy Tool - A dedicated tool for codebase search with Brain AI critique.
This can be imported and used as a tool by the Code Puppy agent.
"""

import sys
import os
import json
import configparser
from pathlib import Path
from typing import Optional, Dict, Any
from langcrew.llm import LLM

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Load config
config = configparser.ConfigParser()
config.read('/home/mine/.code_puppy/puppy.cfg')

# Lazy imports inside methods to avoid heavy dependencies at import time
try:
    from brain_modes.brain_mode_manager import record_activity
except ImportError:
    # Stub for environments without brain_modes
    def record_activity(*args, **kwargs):
        pass

# Import project map tool functions
from project_map_tool import search_relevant_files, load_file_content, get_file_metadata
from config import (CODEPUPPY_MODEL, OLLAMA_BASE_URL, OPENROUTER_MODEL, OPENROUTER_BASE_URL, OPENROUTER_API_KEY_ENV)

DB_PATH = "/home/mine/projects/codebase-index/db"

class BrainAICritique:
    """Generate critiques using Ollama."""

    def __init__(self, model: str = "llama3.2:1b"):
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
        self.default_model = CODEPUPPY_MODEL
        self.base_url = OLLAMA_BASE_URL
        # Lazy import to avoid heavy dependencies
        from brain_ai_wrapper import BrainAIWrapper
        self.brain_wrapper = BrainAIWrapper()
        self.brain_ai = BrainAICritique(model=self.default_model)

    def plan_openrouter(self, task: str):
        """Use OpenRouter fallback model for complex tasks."""
        api_key = os.environ.get(OPENROUTER_API_KEY_ENV)
        if not api_key:
            raise ValueError(f"OpenRouter API key not found. Set {OPENROUTER_API_KEY_ENV} environment variable.")
        return LLM(
            model=OPENROUTER_MODEL,
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
        )

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
        from index_repo import search_codebase
        results = search_codebase(query)

        if not results:
            return f"No results found for '{query}'"

        formatted = []
        for i, result in enumerate(results[:top_k], 1):
            formatted.append(f"\n### Result {i}: {result["path"]}")
            formatted.append(f"Lines: {result["line_start"]}-{result["line_end"]}")
            formatted.append(f"Score: {result["_distance"]:.3f}")
            formatted.append(f"Code:\n{result["text"]}")

        return "\n".join(formatted)

    def process_query(self, query: str, ext: str = ".py", top_k: int = 5, no_critique: bool = False) -> str:
        """
        LLM Council Architecture: Auto-call CrewAI Brain for complex tasks

        Args:
            query: The search query
            ext: File extension to filter by
            top_k: Number of results to return
            no_critique: Skip Brain Council critique/analysis

        Returns:
            Codebase results merged with Brain Council analysis
        """
        # Step 1: Code Puppy search (fast)
        codebase_results = self.search(query, ext, top_k)

        if no_critique:
            return codebase_results

        # Step 2: Always call Brain Council for full analysis
        print("\n Calling Brain Council (ID/EGO/SUPER-EGO/MEMORY)...")

        # Step 3: Call CrewAI Brain Council (ID→EGO→SUPER-EGO→MEMORY)
        brain_result = self.brain_wrapper.plan(query)

        # Step 4: Merge results
        merged = f"""
 CODEBASE RESULTS (from codebase-index):
{codebase_results}

 BRAIN COUNCIL ANALYSIS (ID/EGO/SUPER-EGO/MEMORY):
{brain_result}

 MERGED RESULT:
{brain_result}
"""
        return merged

def main():
    """Main entry point for the cp command."""
    import argparse

    parser = argparse.ArgumentParser(description='Code Puppy Tool - Codebase search with Brain AI')
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--ext', default='.py', help='File extension to filter by')
    parser.add_argument('--critique', action='store_true', help='Enable Brain Council critique (default)')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results')

    args = parser.parse_args()

    # Interactive mode if no query provided
    if not args.query:
        print("\n🐶 Code Puppy v1.0 - Interactive Shell")
        print("🧠 Brain Council integrated (ID/EGO/SUPER-EGO/MEMORY)")
        print("\nCommands:")
        print("  cpb <task>              - Call Brain Council (auto-OpenRouter)")
        print("  cpb plan <task>         - Brain Council planning")
        print("  cpb ID <task>           - Raw code facts (ID lobe)")
        print("  cpb EGO <task>          - Practical approach (EGO lobe)")
        print("  cpb SUPER-EGO <task>    - Ethics/security (SUPER-EGO lobe)")
        print("  cpb MEMORY <task>       - Past learning (MEMORY lobe)")
        print("  search <query>          - Search codebase")
        print("  help                    - Show this help")
        print("  exit                    - Exit interactive mode\n")

        cp = CodePuppyTool()

        while True:
            try:
                query = input("> ").strip()

                if not query:
                    continue

                if query == "exit" or query == "quit":
                    print("\n🐶 Goodbye!\n")
                    break

                if query == "help":
                    print("\n🐶 Code Puppy Commands:")
                    print("  cpb <task>              - Call Brain Council (auto-OpenRouter)")
                    print("  cpb plan <task>         - Brain Council planning")
                    print("  cpb ID <task>           - Raw code facts (ID lobe)")
                    print("  cpb EGO <task>          - Practical approach (EGO lobe)")
                    print("  cpb SUPER-EGO <task>    - Ethics/security (SUPER-EGO lobe)")
                    print("  cpb MEMORY <task>       - Past learning (MEMORY lobe)")
                    print("  search <query>          - Search codebase")
                    print("  exit                    - Exit interactive mode\n")
                    continue

                # Handle cpb command (Brain Council)
                if query.startswith("cpb "):
                    from brain_ai_wrapper import BrainAIWrapper

                    # Parse command: cpb [lobe] [task]
                    parts = query[4:].split()  # Remove "cpb "
                    if not parts:
                        print("❌ Usage: cpb <task> or cpb [lobe] <task>")
                        print("   Lobe options: plan, ID, EGO, SUPER-EGO, MEMORY")
                        continue

                    lobe = parts[0] if parts[0] in ['ID', 'EGO', 'SUPER-EGO', 'MEMORY', 'plan'] else 'plan'
                    task = query[5:]  # Get everything after "cpb "

                    brain = BrainAIWrapper()

                    # Auto-detect OpenRouter need based on task complexity
                    complex_tasks = ['plan', 'architecture', 'design', 'strategy', 'implement',
                                   'create', 'add', 'build', 'setup', 'configure', 'refactor']
                    use_openrouter = any(k in task.lower() for k in complex_tasks) or lobe != 'plan'

                    if use_openrouter:
                        # Use OpenRouter for complex tasks
                        print("\n🧠 Calling Brain Council via OpenRouter...")
                        result = brain.plan_openrouter(task, lobe)
                    else:
                        # Use Ollama for simple tasks
                        print("\n🧠 Calling Brain Council via Ollama...")
                        result = brain.plan(task)

                    print(result)

                elif query.startswith('brain-council '):
                    task = query[14:]
                    brain = BrainAIWrapper()
                   print("\nCalling Brain Council via CrewAI...")
                    model = config.get('command_to_model_mapping', 'command_brain-council_model', fallback='openrouter_qwen')
                    result = brain.plan_crewai(task, model)
                    print(result)


                elif query.startswith('openrouter '):
                    task = query[11:]
                    brain = BrainAIWrapper()
                    print("
 Calling Brain Council via OpenRouter...")
                    result = brain.plan_openrouter(task, plan)
                    print(result)

                elif query.startswith('qwencoder '):
                    task = query[10:]
                    cp = CodePuppyTool()
                    print("
 Calling QwEncoder via Ollama...")
                    result = cp.brain_ai.process(task)
                    print(result)

                # Handle search command
                elif query.startswith("search "):
                    search_query = query[7:]
                    if not search_query:
                        print("❌ Usage: search <query>")
                        continue
                    result = cp.process_query(search_query, ".py", 5)
                    print(result)

                # Normal Code Puppy search with auto Brain Council
                else:
                    result = cp.process_query(query, args.ext, args.top_k, no_critique=args.no_critique)
                    print(result)

            except KeyboardInterrupt:
                print("\n🐶 Goodbye!\n")
                break
            except EOFError:
                print("\n🐶 Goodbye!\n")
                break

    # Non-interactive mode
    else:
        cp = CodePuppyTool()
        result = cp.process_query(args.query, args.ext, args.top_k, no_critique=not args.critique)
        print(result)

if __name__ == "__main__":
    main()
