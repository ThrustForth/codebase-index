# code_puppy_with_index.py

import sys

from search import search_codebase
import os

DB_PATH = "/home/mine/Desktop/codebase-index/db"

def enrich_prompt(user_question: str, base_prompt: str) -> str:
    hits = search_codebase(user_question, top_k=5, db_path=DB_PATH)
    snippets = "\n".join(
        f"[{i+1}] {h['path']}:{h['start_line']}-{h['end_line']}\n{h['snippet']}"
        for i, h in enumerate(hits)
    )
    return f"{base_prompt}\n\n# Relevant code from your repo\n{snippets}\n\nUser: {user_question}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python code_puppy_with_index.py \"your question here\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    base_prompt = "You are a helpful coding assistant. Use the provided code snippets to answer accurately."

    enriched = enrich_prompt(question, base_prompt)

    # TODO: Call Code Puppy / OpenRouter here with `enriched` as the prompt.
    # For example, if you already have a wrapper for OpenRouter, call it here.

    print("Enriched prompt to send to Code Puppy:")
    print(enriched)
