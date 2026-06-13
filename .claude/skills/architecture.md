# Architecture Guidelines

## Behavioral Guardrails
- Think before designing: Understand the problem before proposing solutions
- Simplicity first: YAGNI - avoid overengineering
- Surgical changes: Modify only what is necessary for the feature
- Goal-driven: Architecture should serve business needs, not be elegant

## Design Principles
1. Single Responsibility: One thing per function/class
2. Explicit dependencies: Pass dependencies, do not hide them
3. Fail fast: Validate early, surface errors immediately
4. Composition over inheritance: Prefer mixins/funcs over deep hierarchies

## Architecture Checklist
- Clear module boundaries
- Dependency injection (not global state)
- Error handling at boundaries
- Logging at key decision points
- Configuration externalized (env vars, not hardcoded)
- API versioning considered

## Common Patterns
- API layer: Route > Controller > Service > Model
- Database: Repository pattern for data access
- Async: Task queues for heavy operations
- Caching: Cache-aside pattern, explicit TTL

## When to Refactor
- Duplicate logic > 2 times
- Function > 50 lines without clear subsections
- Class with > 5 methods doing unrelated things
- Cross-cutting concerns scattered everywhere
