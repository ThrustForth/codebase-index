#!/usr/bin/env python3
"""
Brain AI Wrapper for Code Puppy
Calls Brain AI and returns results
"""

import subprocess
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BRAIN_AI_ROOT = Path(__file__).parent / "brain-ai"
PROJECT_ROOT = Path(__file__).parent
CRITIQUES_DIR = PROJECT_ROOT / "critiques"


class BrainAI:
    def __init__(self):
        self.venv_python = BRAIN_AI_ROOT / "venv" / "bin" / "python"
        self.main_script = BRAIN_AI_ROOT / "brain_ai" / "src" / "brain_ai" / "main.py"

    def run(self, prompt: str = None) -> str:
        """Run Brain AI with optional prompt"""
        cmd = [str(self.venv_python), str(self.main_script)]

        if prompt:
            import os
            os.environ["BRAIN_AI_PROMPT"] = prompt

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(BRAIN_AI_ROOT)
        )

        if result.returncode != 0:
            logger.error("Brain AI subprocess failed: %s", result.stderr)
            return f"Brain AI error: {result.stderr}"

        return result.stdout

    def critique(self, code: str) -> str:
        """Get Brain AI critique of code"""
        prompt = f"""
CRITIQUE THIS CODE:

{code}

Evaluate:
1. Bugs or edge cases
2. Pattern violations
3. Performance issues
4. Security concerns
5. Suggested improvements

Return structured critique with issues and fixes.
"""
        return self.run(prompt)

    def plan(self, task: str) -> str:
        """Get Brain AI plan for task"""
        prompt = f"""
CREATE IMPLEMENTATION PLAN:

Task: {task}

Return:
1. Phases with milestones
2. Steps per phase
3. Skills needed
4. Timeline estimates
"""
        return self.run(prompt)

    def add_skill(self, name: str, description: str, steps: list):
        """Add successful pattern to skill archive"""
        cmd = [
            str(self.venv_python),
            "-c",
            f"""
import sys
sys.path.insert(0, '{BRAIN_AI_ROOT}/brain_ai/src')
from crew import skill_archive
skill_archive.add_skill('{name}', '{description}', {steps})
print(f'Skill added: {name}')
"""
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Skill archive add failed: %s", result.stderr)
        return result.stdout

    def merge(self, codebase_results: str, openrouter_result: str) -> str:
        """Merge codebase search + OpenRouter results"""
        prompt = f"""
MERGE THESE TWO ANSWERS INTELLIGENTLY:

CODEBASE RESULTS (facts from code):
{codebase_results}

OPENROUTER (deep reasoning):
{openrouter_result}

MERGE GUIDELINES:
- Use codebase facts for accuracy
- Use OpenRouter reasoning for depth
- Remove redundancy
- Keep best parts
- Output coherent final answer
"""
        return self.run(prompt)


class BrainAIWrapper:
    """Wrapper for Brain AI integration with Code Puppy"""

    def __init__(self):
        self.brain = BrainAI()
        CRITIQUES_DIR.mkdir(exist_ok=True)

    def analyze_code(self, code: str, query: str = "") -> dict:
        """Analyze code and return structured critique"""
        critique = self.critique(code)
        result = {
            "query": query,
            "critique": critique,
            "needs_new_tool": self._detect_missing_tool(critique),
            "recommended_tool": None,
            "tool_purpose": None,
        }

        if result["needs_new_tool"]:
            result["recommended_tool"] = self._extract_tool_name(critique)
            result["tool_purpose"] = self._extract_tool_purpose(critique)

        self.save_critique(result)
        return result

    def critique(self, code: str) -> str:
        """Get Brain AI critique of code"""
        return self.brain.critique(code)

    def plan(self, task: str) -> str:
        """Get Brain AI plan for task"""
        return self.brain.plan(task)

    def save_critique(self, critique: dict):
        """Save critique to critiques directory"""
        filename = f"critique_{hash(critique.get('query', 'unknown')) % 10000}.json"
        with open(CRITIQUES_DIR / filename, 'w') as f:
            json.dump(critique, f, indent=2)

    def _detect_missing_tool(self, critique: str) -> bool:
        """Detect if critique suggests a new tool is needed"""
        keywords = [
            "missing pattern",
            "security pattern",
            "new tool",
            "tool needed",
            "should add",
            "would benefit from"
        ]
        critique_lower = critique.lower()
        return any(keyword in critique_lower for keyword in keywords)

    def _extract_tool_name(self, critique: str) -> str:
        """Extract suggested tool name from critique"""
        if "security" in critique.lower():
            return "security_validator"
        elif "pattern" in critique.lower():
            return "pattern_detector"
        else:
            return "code_reviewer"

    def _extract_tool_purpose(self, critique: str) -> str:
        """Extract tool purpose from critique"""
        if "security" in critique.lower():
            return "Detect security vulnerabilities in code"
        elif "pattern" in critique.lower():
            return "Find code patterns and anti-patterns"
        else:
            return "Review code quality"


# CLI interface
if __name__ == "__main__":
    wrapper = BrainAIWrapper()

    if len(sys.argv) < 2:
        print("Usage: brain_ai_wrapper.py [run|critique|plan|merge|analyze] [args]")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "run":
        prompt = sys.argv[2] if len(sys.argv) > 2 else None
        print(wrapper.brain.run(prompt))

    elif mode == "critique":
        code = sys.argv[2] if len(sys.argv) > 2 else "print('hello')"
        print(wrapper.critique(code))

    elif mode == "plan":
        task = sys.argv[2] if len(sys.argv) > 2 else "Add logging feature"
        print(wrapper.plan(task))

    elif mode == "merge":
        codebase = sys.argv[2] if len(sys.argv) > 2 else ""
        openrouter = sys.argv[3] if len(sys.argv) > 3 else ""
        print(wrapper.brain.merge(codebase, openrouter))

    elif mode == "analyze":
        code = sys.argv[2] if len(sys.argv) > 2 else ""
        query = sys.argv[3] if len(sys.argv) > 3 else ""
        print(json.dumps(wrapper.analyze_code(code, query), indent=2))