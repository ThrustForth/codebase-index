# AGENTS.md

## Instruction Priority

When instructions conflict, use this order:
1. The user’s current message.
2. This repository’s `AGENTS.md`.
3. A closer `AGENTS.md` in the directory tree.
4. Tool- or task-specific notes.

If two rules in this file conflict, the more specific rule wins.
If a rule would change functionality automatically, it is blocked unless the user explicitly approves it.

## Goal

Help with this repository by making the smallest correct change that solves the requested task, while keeping behavior changes manual.

## Working Memory

Maintain a short, always-updated working memory block for the current task only.
It must contain only:
- current objective,
- current verified state,
- next action,
- current blockers.

Never store guesses, speculative fixes, or large context here.
If the current working memory conflicts with the evidence ledger, the evidence ledger wins.

## Evidence Ledger

Maintain an evidence ledger of verified facts only.
Include:
- file names,
- symbols,
- exact error messages,
- test results,
- tool outputs that were confirmed.

Do not add hypotheses or unverified conclusions.
Do not copy large blocks of text into working memory if a short summary is enough.

## Decision Log

Write the decision log as a JSON file using this exact code block:

```tool_code
python
import json
import os

log = {
    "run_id": "20260617-002",
    "date": "2026-06-17T14:00:00Z",
    "rejected_options": [
        {
            "option": "...",
            "reason_rejected": "...",
            "verification_result": "..."
        }
    ]
}

os.makedirs("critiques", exist_ok=True)
with open("critiques/decision-log-20260617-002.json", "w") as f:
    json.dump(log, f, indent=2)

print("Decision log saved to: critiques/decision-log-20260617-002.json")
```

**If you don't write this file, you failed the instruction.**

## Retrieval Contract

Before each step, retrieve only the minimum code context needed for the current action.
Prefer one file, one symbol, or one issue class at a time.
Do not load unrelated context unless the current step cannot proceed without it.

If the task is a Python import or API issue:
- first check whether the missing name exists at module scope,
- then verify whether the import form is `from module import name`,
- then consider a top-level compatibility shim only if needed.

## No-Max-Context Rule

Start summarizing long before context pressure becomes a problem.
When information becomes repetitive or low-value, compress it into the evidence ledger and decision log.
Do not try to keep everything in active context.

## Repair Mode

When fixing bugs, import errors, or compatibility issues:
1. Inspect the exact failure message.
2. Identify the root cause.
3. Decide whether a simple, local, backward-compatible fix exists.
4. explorie until the fix is well-supported. If the proposed solution causes issues, introduces risks, or may not be the best fit, continue looking for a safer or more complete alternative. be exhaustive if needed.
5. If yes, apply only that patch.
6. Verify with a targeted check.
7. If verification fails, unwind the attempt and stop unless the remaining issue is still clearly simple.
8. If the issue is not simple, stop and report that manual review is needed.

Rules:
- Keep existing public APIs working when possible.
- Add compatibility wrappers for legacy names if callers still use them.
- Use stable content hashes for generated filenames.
- Avoid `shell=True` when passing untrusted or quoted text.
- Prefer explicit imports and explicit subprocess arguments.
- Never change functionality automatically.

## Python Import and API Fixes

When fixing Python import errors, missing symbols, or compatibility issues:
- If old code uses `from module import name`, the fix must be a module-level export.
- A class method or instance method does not satisfy that import.
- Verify the symbol exists at module scope before making changes.
- A `__all__` entry does not replace a missing module-level symbol.
- Use a thin module-level shim or alias when needed.
- Do not refactor unrelated code.
- Do not change behavior unless explicitly requested.

## Chunked Reasoning

For multi-step or unclear tasks:
1. Break the work into chunks.
2. Inspect only the current chunk.
3. Extract the most relevant facts.
4. Write a short summary into working memory and the evidence ledger.
5. Move to the next chunk only after compressing the current one.
6. Do not attempt to solve every possibility in one pass.

## Candidate Enumeration

When a problem has multiple plausible fixes:
- enumerate the simple candidate fixes first,
- rank them by scope, compatibility, and verification cost,
- test the best simple candidate first,
- if it fails, record why in the decision log,
- then move to the next simple candidate.

Do not skip directly to broad refactors.

## Verification

Always verify the smallest meaningful behavior change before continuing.
Prefer:
- import checks for symbol/export issues,
- one-file tests for local behavior,
- direct CLI runs for workflow issues,
- existing test suites for regressions.

Do not claim verification that you did not run.

## Tool Routing

Use the most specific available tool or workflow for the task.
Prefer narrow searches, focused reads, and local checks over broad reasoning when the issue is already well-scoped.
If the task remains ambiguous after one focused pass, summarize the ambiguity and stop.
Prefer the local reasoning workflow available in this workspace when it is present and applicable.
If it is not available in the current context, report that limitation and continue with the closest supported workflow.
Do not assume command availability unless the current agent context explicitly exposes it.

## Stop Conditions

Stop immediately if:
- the fix would change functionality and has not been explicitly approved,
- the problem requires redesign rather than repair,
- the issue is not clearly simple, local, and backward-compatible,
- verification fails and no smaller safe retry is obvious.

## Change scope

Do not over-constrain solutions to minimal edits. If a slightly larger refactor or compatibility shim better solves the current bug, consider it and explain why it is preferable. Preserve public behavior unless the user explicitly requests a breaking change.

## Fix strategy

Prefer the smallest safe fix, but if a broader refactor clearly solves the current problem better, propose it and explain the tradeoffs. Keep backward compatibility unless there is a strong reason not to.

## Global Output Requirements (APPLIES TO ALL AGENTS)

When proposing fixes, bug reports, security analysis, or code recommendations, you MUST include these sections for each recommendation:

### 1. Alternatives Considered
- List at least 2 different approaches
- Explain why each alternative was considered or rejected

### 2. Tradeoffs
- **Complexity vs Safety**: How much complexity does this add vs security/quality benefit?
- **Scope vs Impact**: How broad is the change vs how much risk does it eliminate?
- **Performance Cost**: Any measurable performance impact or overhead?

### 3. Constraints
- **Backward Compatibility**: Will this break existing APIs, data formats, or behaviors?
- **What Must Not Break**: List specific behaviors that must be preserved
- **Migration Effort**: Does this require changes to config, data, or other files?

### Violation Rule

If any required section is missing (Alternatives, Tradeoffs, or Constraints), the response is **incomplete** and must be regenerated with all sections included.

## Output Style

Be concise, explicit, and evidence-based.
When reporting a fix, include:
- root cause,
- minimal change,
- verification,
- any remaining blocker,
- the next manual step if needed.
