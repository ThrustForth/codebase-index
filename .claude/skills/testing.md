# Testing Guidelines

## Behavioral Guardrails
- Test-first mindset: Define expected behavior before writing tests
- Simplicity first: One test per concept, minimal assertions
- Surgical changes: Only add tests for actual code changes
- Goal-driven: Tests must catch real bugs, not just pass

## Test Types
1. Unit tests: Single function/method, isolated dependencies
2. Integration tests: Multiple components working together
3. Edge case tests: Invalid inputs, boundary conditions
4. Regression tests: Known bugs that must not return

## Test Quality Checklist
- Descriptive test names (test_login_with_invalid_password_fails)
- Independent tests (no shared state)
- Proper setup/teardown
- Assert actual behavior, not implementation
- Cover edge cases (empty, None, max values)
- Mock external dependencies

## Common Test Commands
- Run all tests: pytest
- Run specific file: pytest tests/test_login.py
- Run with coverage: pytest --cov=. tests/
- Run failed tests only: pytest --lf
