# Code Puppy Workspace - Brain AI Integration

## Things to Remember

### How to Start Code Puppy
1. Run `pl` in terminal
2. Select "codebase-index" project from the list
3. Code Puppy starts automatically in that project
4. Use `cp` commands - Brain AI works automatically!

No need to manually `cd` or restart - `pl` loads everything for you!

### Core Setup
- Code Puppy has Brain AI integration for self-improving code analysis
- `cp "query"` commands search codebase + get Brain AI critiques automatically
- No setup needed every time - everything is permanent

### Key Files
- `code_puppy_tool.py` - Main cp command tool
- `brain_ai_wrapper.py` - Generates critiques
- `brain_coordinator.py` - Manages parallel workflows
- `AGENTS.md` - Agent definitions + auto-added tools
- `critiques/` - Stored critique files
- `SPACES_WORKFLOW.md` - Full workflow documentation
- `project-launcher.fish` - Your project launcher script

### Quick Commands
```bash
cp "search for <pattern>"           # Search codebase with Brain AI
cp "critique <code>"                # Get Brain AI critique
cp "run security_validator on <file>" # Security analysis
!ls -la ~/projects/codebase-index/critiques/
!grep "added_by: brain_ai" AGENTS.md
```

### Self-Improvement Loop
1. `cp` query → searches codebase
2. Brain AI critiques → finds gaps
3. Saves critique → `critiques/XXXX.json`
4. Adds tool → `AGENTS.md`
5. Future searches → use new tools
6. **Repeat → gets smarter**

### Shell Passthrough Works
- Use `!` prefix for shell commands
- Example: `!cs ollama .py 5`

### Custom `cs` Command
```bash
!cs ollama .py 5
```
Uses LanceDB+Ollama for codebase indexing

### No Reload Needed
- Everything auto-loads when you start Code Puppy via `pl`
- Just use `cp` commands - Brain AI works automatically!
