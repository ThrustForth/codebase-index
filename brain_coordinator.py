#!/usr/bin/env python3
"""
Brain Coordinator: Parallel Coordination between OpenRouter and Brain AI
Option 4 Implementation: Fast initial code + iterative refinement
"""

import threading
import queue
import time
import subprocess
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    OPENROUTER_FAST = "openrouter_fast"
    BRAIN_DEEP = "brain_deep"

@dataclass
class CodeCandidate:
    source: str
    code: str
    quality_score: float = 0.0
    critique: str = ""
    timestamp: float = 0.0

class BrainCoordinator:
    """
    Coordinates parallel execution between OpenRouter (fast) and Brain AI (deep)
    with iterative refinement loop.
    """

    def __init__(self, config: dict):
        self.config = config
        self.brain_queue = queue.Queue()

        # Shell commands from your setup
        self.BRAIN_RUN_CMD = "!~/projects/brain-ai/brain_ai/run_brain_task.fish"
        self.CS_CMD = "!cs"

    def coordinated_workflow(self, task: str, top_k: int = 3) -> CodeCandidate:
        """
        Main coordination workflow:
        1. OpenRouter generates initial code FAST (5s)
        2. Brain analyzes in background (30-60s)
        3. OpenRouter refines code using Brain's critique (5-10s)
        4. Quality scoring to pick best candidate
        """
        print(f"\n🚀 Starting coordinated workflow for: {task}")
        start_time = time.time()

        # Phase 1: Parallel execution
        print("\n📍 Phase 1: Parallel execution (OpenRouter fast + Brain deep)")
        initial_code = self._openrouter_generate(task, top_k)

        brain_analysis_thread = threading.Thread(
            target=self._brain_analyze,
            args=(task, initial_code.code)
        )
        brain_analysis_thread.start()

        # Phase 2: Iterative refinement
        print("\n📍 Phase 2: Iterative refinement (Brain critiques → OpenRouter improves)")
        refined_code = self._refine_with_brain_critique(task, initial_code)

        # Phase 3: Quality scoring
        print("\n📍 Phase 3: Quality scoring (pick best candidate)")
        best_candidate = self._score_and_select([initial_code, refined_code])

        elapsed = time.time() - start_time
        print(f"\n✅ Workflow complete in {elapsed:.2f}s")
        print(f"   Best source: {best_candidate.source}")
        print(f"   Quality score: {best_candidate.quality_score:.2f}")

        return best_candidate

    def _openrouter_generate(self, task: str, top_k: int) -> CodeCandidate:
        """Generate initial code using OpenRouter (fast, ~5s)"""
        print(f"\n⚡️ OpenRouter: Generating initial code for '{task}'")

        initial_code = self._execute_openrouter_query(task, top_k)

        candidate = CodeCandidate(
            source=AgentRole.OPENROUTER_FAST.value,
            code=initial_code,
            quality_score=0.0,
            timestamp=time.time()
        )

        print(f"   ✅ Initial code generated ({len(initial_code)} chars)")
        return candidate

    def _brain_analyze(self, task: str, code: str) -> None:
        """Analyze code using Brain AI in background (deep, ~30-60s)"""
        print(f"\n🧠 Brain: Starting deep analysis (background thread)")

        analysis_prompt = f"""
Analyze this code for the task: {task}

CODE:
{code}

Provide:
1. Technical critique (bugs, edge cases, performance)
2. Architecture improvements
3. Security concerns
4. Better alternatives
"""

        critique = self._execute_brain_query(analysis_prompt)

        self.brain_queue.put({
            'task': task,
            'critique': critique,
            'timestamp': time.time()
        })

        print(f"   ✅ Brain analysis complete ({len(critique)} chars)")

    def _refine_with_brain_critique(self, task: str, initial_code: CodeCandidate) -> CodeCandidate:
        """Refine code using Brain's critique"""
        print(f"\n🔄 Refining: Using Brain's critique to improve code")

        try:
            brain_result = self.brain_queue.get(timeout=60)
            critique = brain_result['critique']
            print(f"   Got Brain critique ({len(critique)} chars)")
        except queue.Empty:
            print("   ⚠️ Brain timeout, using initial code only")
            return initial_code

        refinement_prompt = f"""
Improve this code based on Brain AI's critique:

TASK: {task}

ORIGINAL CODE:
{initial_code.code}

BRAIN'S CRITIQUE:
{critique}

Generate improved code that addresses all critique points.
"""

        refined_code = self._execute_openrouter_query(refinement_prompt, top_k=1)

        candidate = CodeCandidate(
            source=AgentRole.OPENROUTER_FAST.value + "_refined",
            code=refined_code,
            critique=critique,
            timestamp=time.time()
        )

        print(f"   ✅ Refinement complete ({len(refined_code)} chars)")
        return candidate

    def _score_and_select(self, candidates: list) -> CodeCandidate:
        """Score all candidates and select best one"""
        print(f"\n📊 Scoring {len(candidates)} candidates")

        scored = []
        for candidate in candidates:
            score = self._calculate_quality_score(candidate)
            candidate.quality_score = score
            scored.append((score, candidate))
            print(f"   {candidate.source}: {score:.2f}")

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_candidate = scored[0]

        print(f"\n🏆 Best candidate: {best_candidate.source} (score: {best_score:.2f})")
        return best_candidate

    def _calculate_quality_score(self, candidate: CodeCandidate) -> float:
        """Calculate quality score based on completeness, critique, performance, security"""
        score = 0.0

        # Base score from code length (completeness)
        score += min(len(candidate.code) / 1000, 3.0)

        # If refined with Brain critique, add bonus
        if candidate.critique:
            score += 2.0
            critique_words = len(candidate.critique.split())
            score += min(critique_words / 50, 2.0)

        # Performance indicators
        performance_keywords = ['efficient', 'optimal', 'fast', 'cache', 'batch']
        if any(kw in candidate.code.lower() for kw in performance_keywords):
            score += 1.5

        # Security indicators
        security_keywords = ['secure', 'validate', 'sanitize', 'escape', 'auth']
        if any(kw in candidate.code.lower() for kw in security_keywords):
            score += 1.5

        return max(score, 0.0)

    def _execute_openrouter_query(self, prompt: str, top_k: int = 1) -> str:
        """Execute query using OpenRouter via cs command"""
        cmd = f"cs {prompt[:50]} .py {top_k}"

        try:
            result = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                timeout=self.config['openrouter']['timeout'],
                executable='/usr/bin/fish'
            )
            return result.stdout if result.stdout else f"# Error: {result.stderr}"
        except Exception as e:
            return f"# OpenRouter error: {str(e)}"

    def _execute_brain_query(self, prompt: str) -> str:
        """Execute query using Brain AI multi-agent system"""
        cmd = f"~/projects/brain-ai/brain_ai/run_brain_task.fish '{prompt}'"

        try:
            result = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                timeout=self.config['brain']['timeout'],
                executable='/usr/bin/fish'
            )
            return result.stdout if result.stdout else f"# Error: {result.stderr}"
        except Exception as e:
            return f"# Brain AI error: {str(e)}"

def create_brain_coordinator(config: dict = None) -> BrainCoordinator:
    """Create BrainCoordinator with default config"""
    default_config = {
        'openrouter': {'model': 'your-openrouter-model', 'timeout': 10},
        'brain': {'timeout': 60, 'agents': ['ID', 'EGO', 'SUPER-EGO']},
        'refinement': {'max_iterations': 2, 'min_score_improvement': 0.5},
    }

    if config:
        default_config.update(config)

    return BrainCoordinator(default_config)


if __name__ == "__main__":
    coordinator = create_brain_coordinator()
    test_task = "create a Python function that parses JSON config files"
    result = coordinator.coordinated_workflow(test_task, top_k=3)

    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(result.code)
