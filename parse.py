import argparse
import lancedb
import subprocess
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    db = lancedb.connect("lancedb")
    table = db.open_table(db.table_names()[0])

    embedding = json.loads(subprocess.run(
        f'ollama embed nomic-embed-text "{args.query}"',
        capture_output=True, text=True
    ).stdout)["embeddings"][0]

    docs = table.search(embedding).limit(args.top).to_pandas()

    context = "\n\n".join([str(doc) for doc in docs])
    prompt = f"Answer: {args.query}\n\nInfo: {context}"

    answer = subprocess.run(
        "ollama run llama3",
        capture_output=True, text=True,
        input=prompt
    ).stdout

    print(f"\n=== QUESTION: {args.query} ===\n")
    print(answer)
    print("\n=== SOURCES ===")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {str(doc)[:200]}")

if __name__ == "__main__":
    main()
