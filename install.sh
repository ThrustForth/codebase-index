#!/usr/bin/env bash

# Codebasе Index & Code Puppy Installer

set -euo pipefail

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m"

success() { echo -e "${GREEN}[+] $*${NC}"; }
error() { echo -e "${RED}[!] $*${NC}"; }

# Check command existence
command_exists() { command -v \$1 >/dev/null 2>&1; }

# 1. Install UV (if needed)
if ! command_exists uv; then
  info "Installing UV package manager"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Python setup
if command_exists python3; then
  PYTHON=$(which python3)
else
  error "Python 3 not found"
  exit 1
fi

# 3. Create virtual environment
if [ -d ".venv" ]; then
  success ".venv exists"
else
  $PYTHON -m venv .venv
  success "New .venv created"
fi
source .venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Install Ollama
if ! command_exists ollama; then
  OS=$(uname)
  if [ $OS = "Darwin" ]; then
    brew install ollama
  else
    curl -fsSL https://ollama.com/install.sh | sh
  fi
fi
ollama pull nomic-embed-text

# 6. Install Code Puppy
info "Installing Code Puppy"
curl -LsSf https://github.com/code-puppy/uvx-code-puppy/releases/latest/download/uvx-code-puppy | sudo tee /usr/local/bin/uvx-code-puppy >/dev/null
chmod +x /usr/local/bin/uvx-code-puppy
uvx code-puppy install

# 7. Setup shell commands
BIN_DIR="$HOME/bin"
mkdir -p $BIN_DIR
cat > $BIN_DIR/cs <<'EOL'
#!/usr/bin/env bash
cd /home/mine/projects/codebase-index && source .venv/bin/activate && python index_repo.py \"\$@\"
EOL
chmod +x $BIN_DIR/cs

# 8. Create required directories
mkdir -p critiques/

# 9. Initialize AGENTS.md
cat > AGENTS.md <<'EOL'
# Code Puppy Agents

### tool_security_validator
- purpose: Detect security issues
- added_by: brain_ai

### tool_pattern_detector
- purpose: Find code patterns
- added_by: brain_ai
EOL

# 10. Setup Brain AI files
m -rf brain_coordinator.py brain_ai_wrapper.py
cp /home/mine/projects/codebase-index/core/brain_coordinator.py .
brain_coordinator.py make executable
cp /home/mine/projects/codebase-index/core/brain_ai_wrapper.py .
brain_ai_wrapper.py make executable

# 11. Add pl command
cat > $BIN_DIR/pl <<'EOL'
#!/usr/bin/env bash
cd /home/mine/projects/codebase-index && python index_repo.py \"\$@\"
EOL
chmod +x $BIN_DIR/pl

# Test installation
if ! command_exists cs; then
  error "cs command not found"
  exit 1
fi
if ! command_exists pl; then
  error "pl command not found"
  exit 1
fi
success "Setup complete! Run 'pl' to start indexing"
exec bash