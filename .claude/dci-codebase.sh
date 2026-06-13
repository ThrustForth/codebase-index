#!/usr/bin/env bash
# DCI (Dynamic Context Injection) wrapper for cs CLI
# Formats search_codebase() results as <DYNAMIC_CONTEXT> for Claude

QUERY="$1"
TOP_K="${2:-5}"
EXT="${3:-.py}"

if [ -z "$QUERY" ]; then
    echo "Usage: dci-codebase.sh <query> <top_k> <ext>"
    echo "Example: dci-codebase.sh ollama 5 .py"
    exit 1
fi

./venv/bin/python -c "
from search import search_codebase
import sys

results = search_codebase(sys.argv[1], top_k=int(sys.argv[2]), file_ext=sys.argv[3])
print('<DYNAMIC_CONTEXT>')
print(f'Codebase search: {sys.argv[1]}, top={sys.argv[2]}, ext={sys.argv[3]}')
for i, r in enumerate(results, 1):
    print(f'=== Result {i} === {r.get(\"path\", \"?\")}')
    print(r.get('text', '') + '\n')
print('</DYNAMIC_CONTEXT>')
" "$QUERY" "$TOP_K" "$EXT"
