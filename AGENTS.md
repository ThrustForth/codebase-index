# Code Puppy Brain AI Agent Definitions

## Agents

### agent_openrouter_fast
- **role:** OpenRouter_FAST
- **purpose:** Fast searches and basic code lookup
- **tools:**
  - search_codebase
  - grep
  - file_read

### agent_brain_deep
- **role:** BRAIN_DEEP
- **purpose:** Deep code critique and security analysis
- **tools:**
  - brain_ai_critique
  - security_validator
  - pattern_detector

## Skills Added by Brain AI
New tools will be added here automatically when Brain AI identifies gaps.

### tool_security_validator
- **purpose:** Detect security issues in code
- **added_by:** brain_ai
- **detail:** Scans for SQL injection, XSS, insecure patterns

### tool_pattern_detector
- **purpose:** Find code patterns and bugs
- **added_by:** brain_ai
- **detail:** Identifies missing validation, error handling