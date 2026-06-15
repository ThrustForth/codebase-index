#!/usr/bin/env python3
"""Code Puppy Brain AI Integration Layer"""

import os, sys, json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"
CRITIQUES_DIR = PROJECT_ROOT / "critiques"

class BrainAIIntegration:
    def __init__(self):
        self.brain_coordinator = None
        self.brain_wrapper = None

    def integrate_with_code_puppy(self):
        sys.path.append(str(PROJECT_ROOT))
        from brain_coordinator import BrainCoordinator
        self.brain_coordinator = BrainCoordinator()
        from brain_ai_wrapper import BrainAIWrapper
        self.brain_wrapper = BrainAIWrapper()
        print("✓ Brain AI integrated with Code Puppy")

    def process_cp_query(self, query):
        results = self.search_codebase(query)
        if results:
            critique = self.brain_wrapper.analyze_code(results, query)
            self.save_critique(critique, query)
            if critique.get("needs_new_tool"):
                self.add_tool_to_agents_md(critique)
            return critique
        return results

    def search_codebase(self, query):
        from index_repo import search_index
        return search_index(query)

    def save_critique(self, critique, query):
        CRITIQUES_DIR.mkdir(exist_ok=True)
        filename = CRITIQUES_DIR / f"critique_{hash(query) % 10000}.json"
        with open(filename, 'w') as f:
            json.dump(critique, f, indent=2)

    def add_tool_to_agents_md(self, critique):
        tool_name = critique["recommended_tool"]
        tool_desc = critique["tool_purpose"]
        with open(AGENTS_MD, 'r') as f:
            content = f.read()
        new_tool = f"\ntool_{tool_name}:\n  purpose: \"{tool_desc}\"\n  added_by: \"brain_ai\"\n"
        with open(AGENTS_MD, 'a') as f:
            f.write(new_tool)
        print(f"✓ Added tool_{tool_name} to AGENTS.md")

if __name__ == "__main__":
    integration = BrainAIIntegration()
    integration.integrate_with_code_puppy()
