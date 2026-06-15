#!/usr/bin/env bash

# Check for CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    cd ~/projects/codebase-index
    echo "🐕 Code Puppy starting with behavioral guardrails (CLAUDE.md found)"
    echo ""
    # Send initial instruction then keep stdin open for interactive input
    (echo "IMPORTANT: Read CLAUDE.md in the project root and follow these behavioral guardrails STRICTLY:

1. Think Before Coding - Always ask clarifying questions FIRST. State assumptions. Never assume.
2. Simplicity First - PUSH BACK on complexity. If I request multiple features, suggest simpler first. Minimum code.
3. Surgical Changes - Edit existing files minimally. Don't create new files unless necessary.
4. Goal-Driven - Define what done means. Don't add speculative features.

CRITICAL: If I request something overengineered, PUSH BACK and suggest simpler alternatives." && cat) | uvx code-puppy -i
else
    echo "🐕 Code Puppy starting (no CLAUDE.md found)"
    uvx code-puppy -i
fi
