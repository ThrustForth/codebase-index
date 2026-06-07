# Codebase Search Configuration

When the user asks to search the codebase, find code, or look for something in the files:

1. **ALWAYS use semantic search first** instead of grep when possible
2. Run: `cd /home/mine/projects/codebase-index && ./venv/bin/python index_repo.py --search "<query>" --ext ".py" --top 5`
3. This uses LanceDB + Ollama embeddings for semantic/vector search
