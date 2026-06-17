# Code Puppy + Brain AI Workflow for Spaces

## Overview
This workspace combines Code Puppy (AI coding agent) with Brain AI (self-improving critique system) for automated codebase analysis and skill acquisition.

---

## Core Components

### 1. Code Puppy Tool (`code_puppy_tool.py`)
- Main entry point for `cp` commands
- Searches indexed codebase using LanceDB
- Integrates Brain AI for critique generation

### 2. Brain AI Wrapper (`brain_ai_wrapper.py`)
- Generates code critiques using Ollama (phi3 model)
- Saves critiques to `critiques/` directory
- Identifies gaps and recommends new tools

### 3. Brain AI Coordinator (`brain_coordinator.py`)
- Manages parallel workflows (OpenRouter_FAST + BRAIN_DEEP)
- Implements iterative refinement with quality scoring
- Coordinates agent roles and tool selection

### 4. Skill Database (`AGENTS.md`)
- Documents agent definitions and tools
- Auto-updated when Brain AI adds new skills
- Persists across sessions

---

## Quick Start Commands

### Search Codebase
```bash
cp "search for <pattern>"
# Example: cp "search for SQL injection vulnerabilities"
```

### Get Brain AI Critique
```bash
cp "critique this code: <code_snippet>"
# Example: cp "critique: def insecure(x): return x"
```

### Run Security Analysis
```bash
cp "run security_validator on <file>"
# Example: cp "run security_validator on index_repo.py"
```

### View Critiques
```bash
!ls -la ~/projects/codebase-index/critiques/
!cat ~/projects/codebase-index/critiques/*.json
```

### Check Brain AI Tools
```bash
!grep -B2 "added_by: brain_ai" ~/projects/codebase-index/AGENTS.md
```

---

## Self-Improvement Loop

1. **Trigger**: `cp "query"` searches codebase
2. **Critique**: Brain AI analyzes results, finds gaps
3. **Save**: Critique saved to `critiques/critique_XXXX.json`
4. **Learn**: If gap found, new tool added to `AGENTS.md`
5. **Improve**: Future searches use new tools
6. **Repeat**: System gets smarter each iteration

---

## File Structure

~/projects/codebase-index/
├── code_puppy_tool.py # Main tool (cp commands)
├── code_puppy_brain.py # Brain AI integration layer
├── brain_ai_wrapper.py # Critique generator
├── brain_coordinator.py # Parallel workflow manager
├── index_repo.py # Codebase indexer
├── search.py # Search implementation
├── AGENTS.md # Agent definitions + tools
├── critiques/ # Critique files
│ ├── critique_XXXX.json
│ └── ...
├── db/ # LanceDB index
├── venv/ # Python environment
└── SPACES_WORKFLOW.md # This file

text

---

## Common Workflows

### Workflow 1: Find Security Issues
```bash
# Step 1: Search for vulnerabilities
cp "search for SQL injection"

# Step 2: Get critique
cp "critique the found code for security issues"

# Step 3: Review critique
!cat ~/projects/codebase-index/critiques/*.json | tail -100
```

### Workflow 2: Add New Skill
```bash
# Step 1: Trigger a problem
cp "search for <pattern> but it keeps missing results"

# Step 2: Brain AI adds tool
cp "add a tool to better detect <pattern>"

# Step 3: Verify
!grep -A3 "<tool_name>" ~/projects/codebase-index/AGENTS.md
```

### Workflow 3: Review Learning
```bash
# Count critiques
!ls ~/projects/codebase-index/critiques/*.json | wc -l

# Count tools added
!grep -c "added_by: brain_ai" ~/projects/codebase-index/AGENTS.md

# View all tools
!grep -B2 "added_by: brain_ai" ~/projects/codebase-index/AGENTS.md
```

---

## Troubleshooting

### Issue: NameError on BrainAIWrapper
**Fix**: Ensure imports in `code_puppy_tool.py` include:
```python
from brain_ai_wrapper import BrainAIWrapper
from brain_coordinator import BrainCoordinator
```

### Issue: Critiques directory empty
**Fix**: Run test command:
```bash
cp "search for missing input validation"
!ls -la ~/projects/codebase-index/critiques/
```

### Issue: Timeout errors
**Fix**: Check `brain_ai_wrapper.py` is complete (not truncated)

---

## Next Steps

1. **Test**: Run security analysis on your codebase
2. **Monitor**: Watch critique count grow
3. **Expand**: Add more Brain AI tools as needed
4. **Optimize**: Tune Ollama model parameters

---

## Maintenance

### Daily
- Run `cp` commands for code analysis
- Review new critiques in `critiques/`
- Check AGENTS.md for new tools

### Weekly
- Count total critiques and tools
- Review tool effectiveness
- Update AGENTS.md with manual improvements

### Monthly
- Archive old critiques
- Consolidate redundant tools
- Optimize index performance

---

## Contact

For issues or questions about this workflow, refer to:
- `CODE_PUPPY.md` - Code Puppy documentation
- `README.md` - Project overview
- Brain AI integration comments in source files
EOF

# Verify it was created
!ls -la ~/projects/codebase-index/SPACES_WORKFLOW.md

# Show the file
!head -50 ~/projects/codebase-index/SPACES_WORKFLOW.md

## Auto-Test Hook

After every code edit, run tests automatically:

1. Edit file → `on_edit(file_path)` called
2. Run tests → `./venv/bin/pytest test_code_puppy_tool.py --cov`
3. Output results → Show pass/fail in terminal
4. If failed → Auto-suggest fix with Code Puppy
