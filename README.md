# Codebase Indexer + Brain AI Integration

This was tested alongside the Walmart **Code Puppy** AI wrapper with **Brain AI** self-improving integration. Using OpenRouter as the model, but you can use any model. LMK if you get it working on any other "Wrapper".

A local, **Git‑style** codebase indexer powered by **LanceDB** (purely local vector store) and **Ollama** embeddings, now enhanced with **Brain AI** for automated code critique and self-improving skill acquisition.

## Features
- Scans your repository for **files**, **functions/methods**, and **small code snippets**.
- Generates embeddings with a locally‑running Ollama model (e.g. `nomic-embed-text`).
- Stores everything in an on‑disk LanceDB collection – no API keys required.
- Simple CLI to **index** (`--index`) and **search** (`--search <query>`).
- Tiny helper `search_codebase(query, top_k=5)` you can import from **search.py** and call from any Python process (including Code Puppy).

### NEW: Brain AI Integration
- **Automated Code Critique**: Every `cp` command triggers Brain AI analysis
- **Self-Improving**: Automatically adds new tools to `AGENTS.md` when gaps are found
- **Security Analysis**: Detects command injection, path traversal, and other vulnerabilities
- **Critique Archive**: Saves all critiques to `critiques/` directory for tracking
- **Persistent Learning**: Skills persist across sessions

## Prerequisites
- Python **3.10+**
- **Ollama** installed and running locally. Example model:
  ```bash
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

## Quick Start with Code Puppy + Brain AI

### Launch Code Puppy
```bash
pl  # Project launcher
# Select "codebase-index" project
```

### Use Brain AI Commands
```bash
cp "search for <pattern>"              # Search codebase with Brain AI
cp "critique <code>"                   # Get Brain AI critique
cp "run security_validator on <file>"  # Security analysis
cp "critique this project"             # Full project security audit
```

### Check Brain AI Tools
```bash
# View critique files
!ls -la ~/projects/codebase-index/critiques/

# View added tools
!grep -B2 "added_by: brain_ai" ~/projects/codebase-index/AGENTS.md

# Count total critiques
!ls ~/projects/codebase-index/critiques/*.json | wc -l
```

## Usage
```bash
# Search codebase (standalone cs command)
cs <query> <extension> <top>

# Examples
cs ollama .py 3    # Search for ollama in Python files, top 3 results
cs database .py 5  # Search for database in Python files, top 5 results
cs api .rs 10      # Search for api in Rust files, top 10 results
```

### Index your repo
```bash
# From the directory that contains your git repo (or run inside the repo)
python index_cli.py --index
```

### Search (CLI)
```bash
python index_cli.py --search "how to parse json"
```

### NEW: Hybrid Search (keyword + semantic)
```bash
# Adjust keyword vs semantic weights (defaults: 0.3 keyword, 0.7 semantic)
python index_cli.py --search "parse json" --keyword-weight 0.5 --semantic-weight 0.5

# Pure keyword search (exact matches)
python index_cli.py --search "function_name" --keyword-weight 1.0 --semantic-weight 0.0

# Pure semantic search (conceptual matches)
python index_cli.py --search "handle authentication" --keyword-weight 0.0 --semantic-weight 1.0
```

### Programmatic usage
```python
from search import search_codebase

# Default hybrid search
results = search_codebase("parse json", top_k=5)

# Custom weights for keyword vs semantic
results = search_codebase("parse json", top_k=5, keyword_weight=0.5, semantic_weight=0.5)

# Get formatted DCI context for LLM injection
context = search_codebase("parse json", top_k=5, as_dci=True)

for r in results:
    print(r['path'], r['start_line'], '-', r['end_line'])
    print(r['content'][:120])
```

## Integration with Code Puppy + Brain AI

### How It Works
1. ** cp Command**: User types `cp "query"`
2. **Codebase Search**: Calls `search_codebase(query, top_k=5)`
3. **Brain AI Critique**: Analyzes results, finds gaps/issues
4. **Save Critique**: Writes to `critiques/critique_XXXX.json`
5. **Add Tool**: If gap found, adds new tool to `AGENTS.md`
6. **Improve**: Future searches use new tools
7. **Repeat**: System gets smarter each iteration

### Key Files
- `code_puppy_tool.py` - Main `cp` command tool
- `brain_ai_wrapper.py` - Generates critiques
- `brain_coordinator.py` - Manages parallel workflows
- `AGENTS.md` - Agent definitions + auto-added tools
- `critiques/` - Stored critique files
- `SPACES_WORKFLOW.md` - Full workflow documentation

### Self-Improvement Loop

cp query → search → critique → save → learn → improve → repeat

text

Each iteration closes the loop, making the next search more accurate and thorough.

## Updating the Index
- **Manual** – run the indexer again (`--index`).
- **Automated** – add a git hook (e.g. `post-commit`) that calls the indexer.

## Project Structure

codebase-index/
├─ index_repo.py # Core indexing logic
├─ index_cli.py # CLI wrapper
├─ search.py # Public search_codebase function
├─ code_puppy_tool.py # Main cp command
├─ brain_ai_wrapper.py # Brain AI critique generator
├─ brain_coordinator.py # Parallel workflow manager
├─ AGENTS.md # Agent definitions + tools
├─ critiques/ # Critique files
├─ requirements.txt # Dependencies
├─ README.md
├─ SPACES_WORKFLOW.md # Full workflow doc
└─ db/ # LanceDB files (auto-created)

text

## Security Features
After Brain AI integration, the codebase was hardened against:
- ✅ Command injection (shell=False)
- ✅ Path traversal prevention
- ✅ Input validation (MAX_QUERY_LENGTH)
- ✅ Secure logging (logger.error)
- ✅ Unsafe subprocess calls
- ✅ SQL injection in LanceDB
- ✅ Info disclosure prevention

## License
MIT – feel free to tweak and share!

## Contributing
Got it working with another wrapper? Let me know! Open an issue or PR with your setup.
