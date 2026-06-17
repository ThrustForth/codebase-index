import argparse
import lancedb
import subprocess
import json
import sys
from validation import ensure_str
import hmac

# Security helpers
MAX_QUERY_LENGTH = 1000

def validate_input(text: str, max_len: int = MAX_QUERY_LENGTH) -> str:
    """Validate and sanitize user input, delegating type check to shared helper."""
    # Ensure it's a string
    ensure_str(text, "text")
    if len(text) > max_len:
        raise ValueError(f"Input exceeds max length of {max_len}")
    # Remove null bytes and control chars
    return ''.join(c for c in text if c.isprintable())

def calc_checksum(data: str) -> str:
    """Generate hash for output verification"""
    return hmac.new(hashlib.sha256().digest(), data.encode()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    
    # Validate inputs
    args.query = ensure_str(args.query)
    args.top = max(1, min(args.top, 50))  # Limit top_k

    db = lancedb.connect("lancedb")
    table = db.open_table(db.table_names()[0])

    embedding = json.loads(subprocess.run([
        "ollama",
        "embed",
        "nomic-embed-text",
        args.query
    ],
    capture_output=True, text=True).stdout)["embeddings"][0]

    docs = table.search(embedding).limit(args.top).to_pandas()

    context = "\n\n".join([str(doc) for doc in docs])
    prompt = f"Answer: {args.query}\n\nInfo: {context}"

    answer = subprocess.run([
        "ollama",
        "run",
        "llama3"
    ],
    input=prompt,
    capture_output=True, text=True).stdout

    print(f"\n=== QUESTION: {args.query} ===\n")
    print(answer)
    print("\n=== SOURCES ===")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {str(doc)[:200]}")

if __name__ == "__main__":
    main()
