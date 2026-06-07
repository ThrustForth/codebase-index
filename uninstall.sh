#!/usr/bin/env bash
set -euo pipefail

RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m

success() { echo -e ${GREEN}[*] $*${NC}; }
info() { echo -e ${YELLOW}[+] $*${NC}; }

info Uninstalling codebase-index...

# Remove .venv if [[ -d .venv ]]; then
rm -rf .venv
success Removed .venv
else
info .venv not found
fi

# Remove db if [[ -d db ]]; then
rm -rf db
success Removed db/
else
info db/ not found
fi

# Remove cs wrapper
WRAPPER=$HOME/bin/cs
if [[ -f $WRAPPER ]]; then
rm $WRAPPER
success Removed $WRAPPER
else
info $WRAPPER not found
fi

# Remove from fish_user_paths
FISH_CONFIG=$HOME/.config/fish/config.fish
if [[ -f $FISH_CONFIG ]] && grep -q fish_user_paths $FISH_CONFIG; then
sed -i /fish_user_paths/d $FISH_CONFIG
success Removed from fish_user_paths
else
info fish_user_paths not configured
fi

success Uninstall complete!
info Note: Ollama and uv are NOT removed.
info To remove Ollama: brew uninstall ollama (macOS) or sudo systemctl stop ollama (Linux)
info To remove uv: ~/.local/bin/uv self uninstall