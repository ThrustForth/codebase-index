# Code Review Guidelines

## Behavioral Guardrails
- Think before reviewing: State what the code is supposed to do before critiquing
- Simplicity first: Prefer simpler solutions over complex ones
- Surgical feedback: Focus on actual issues, not stylistic preferences
- Goal-driven: Define what good means for this specific codebase

## Review Priorities
1. Correctness: Does it work as intended? Edge cases? Error handling?
2. Security: Input validation? Authentication? Data exposure?
3. Performance: Bottlenecks? Unnecessary loops? Memory leaks?
4. Maintainability: Readability? Documentation? Testability?

## Code Quality Checklist
- Follows existing project patterns
- No hardcoded values or magic numbers
- Proper error handling and logging
- Adequate test coverage
- Clear variable/function names
- No dead code or unused imports

## PR Review Style
- Be specific: This loop is O(n^2) not this is slow
- Offer alternatives: Consider using a dict here for O(1) lookup
- Acknowledge tradeoffs: This is more verbose but clearer
