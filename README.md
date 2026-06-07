# Codebase Indexer
This was tested along side the Walmart Code Puppy AI wrapper and I am using OpenRouter as the model but you can use any model. LMK if you get it working on any other "Wrapper"
A local, **Git‑style** codebase indexer powered by **LanceDB** (purely local vector store) and **Ollama** embeddings.

## Features
- Scans your repository for **files**, **functions/methods**, and **small code snippets**.
- Generates embeddings with a locally‑running Ollama model (e.g. `nomic-embed-text`).
- Stores everything in an on‑disk LanceDB collection – no API keys required.
- Simple CLI to **index** (`--index`) and **search** (`--search <query>`).
- Tiny helper `search_codebase(query, top_k=5)` you can import from **search.py** and call from any Python process (including Code Puppy).

## Prerequisites
- Python **3.10+**
- **Ollama** installed and running locally. Example model:
  ```
  ollama pull nomic-embed-text
  ```
- **LanceDB** Python package (will be installed via `requirements.txt`).

## Installation
```bash
# From the project root (where README.md lives)
bash install.sh
```

## Shell Support
The installer automatically detects your shell and configures the `cs` command appropriately:
- **Fish shell**: Creates a fish function in `~/.config/fish/config.fish`
- **Bash/Zsh**: Creates a wrapper script in `~/bin/cs`

No manual configuration needed - just run `bash install.sh`!

## Usage
```bash
# Search codebase
cs <query> <extension> <top>
# Examples
cs ollama .py 3 # Search for ollama in Python files, top 3 results
cs database .py 5 # Search for database in Python files, top 5 results
cs api .rs 10 # Search for api in Rust files, top 10 results
```

### Index your repo
```bash
# From the directory that contains your git repo (or run inside the repo)
python index_cli.py --index
```

### Search (alternative)
```bash
python index_cli.py --search "how to parse json"
```
Or programmatically:
```python
from search import search_codebase
results = search_codebase("parse json", top_k=5)
for r in results:
    print(r['type'], r['path'], r['snippet'][:120])
```

## Integration with Code Puppy
1. Add the `search_codebase` import to your prompt‑building logic.
2. When the model asks for context, call `search_codebase(query, top_k=5)` and inject the returned snippets into the prompt.
3. Keep the index fresh – re‑run `python index_cli.py --index` after committing or after a batch of changes.

## Updating the Index
- **Manual** – run the indexer again (`--index`).
- **Automated** – add a git hook (e.g. `post-commit`) that calls the indexer.

## Project Structure
```
codebase-index/
├─ index_repo.py      # Core indexing logic
├─ index_cli.py       # CLI wrapper
├─ search.py          # Public `search_codebase` function
├─ requirements.txt   # Dependencies
├─ README.md
└─ db/                # LanceDB files (auto‑created)
```

## License
MIT – feel free to tweak and share!
