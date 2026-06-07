#!/usr/bin/env bash
set -euo pipefail

RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m

info() { echo -e ${YELLOW}[+] $*${NC}; }
success() { echo -e ${GREEN}[*] $*${NC}; }
error() { echo -e ${RED}[!] $*${NC}; }

EXT=.py TOP=100

while [[ $# -gt 0 ]]; do
    case $1 in
        --ext) EXT=$2 shift 2 ;;
        --top) TOP=$2 shift 2 ;;
        *)
            error Unknown option: $1
            exit 1
            ;;
    esac
done

info Re-indexing codebase (ext=$EXT, top=$TOP)

# Delete old index if [[ -d db ]]; then
info Removing existing index directory (db/)
rm -rf db
success Old index removed
else
info No existing index directory found
fi

# Activate venv if [[ -f .venv/bin/activate ]]; then
source .venv/bin/activate
fi

# Run indexing
info Running fresh indexing pass
python index_repo.py --index --ext $EXT --top $TOP
success Re-indexing complete (ext=$EXT, top=$TOP)