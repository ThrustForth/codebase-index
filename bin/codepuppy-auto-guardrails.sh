#!/usr/bin/env bash

# Check for CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    echo "🐕 Code Puppy starting with behavioral guardrails (CLAUDE.md found)"
    echo ""
    # Send the instruction to Code Puppy's stdin
    echo "Please read CLAUDE.md in the project root and follow the behavioral guardrails (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) for all code changes." | uvx code-puppy -i
else
    echo "🐕 Code Puppy starting (no CLAUDE.md found)"
    uvx code-puppy -i
fi
