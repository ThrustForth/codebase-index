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

BRAIN_AI_ROOT = Path("/home/mine/projects/brain-ai")
PROJECT_ROOT = Path(__file__).parent
CRITIQUES_DIR = PROJECT_ROOT / "critiques"

# Helper: format monitoring section
def format_monitoring_section(metrics: dict, trends: dict) -> str:
    """Create a pretty MODEL MONITORING EFFICACY markdown section.
    Categories:
      * Performance – performance_rating, complexity_score
      * Data Quality – test_coverage, code_quality_score
      * Operational – edge_case_handling, error_handling
      * Robustness – security_issues, documentation_quality
    Includes overall score and trend analysis.
    """
    lines = []
    lines.append("\n---\n**MODEL MONITORING EFFICACY**\n---\n")
    lines.append(f"Overall Efficacy Score: {metrics.get('overall_efficacy_score', 0):.2f}\n")
    # Categories
    lines.append("**Performance**\n")
    lines.append(f"- Performance Rating: {metrics.get('performance_rating', 0):.2f}\n")
    lines.append(f"- Complexity Score: {metrics.get('complexity_score', 0):.2f}\n\n")
    lines.append("**Data Quality**\n")
    lines.append(f"- Test Coverage: {metrics.get('test_coverage', 0):.2f}\n")
    lines.append(f"- Code Quality Score: {metrics.get('code_quality_score', 0):.2f}\n\n")
    lines.append("**Operational**\n")
    lines.append(f"- Edge‑Case Handling: {metrics.get('edge_case_handling', 0):.2f}\n")
    lines.append(f"- Error Handling: {metrics.get('error_handling', 0):.2f}\n\n")
    lines.append("**Robustness**\n")
    lines.append(f"- Security Issues Score: {metrics.get('security_issues', 0):.2f}\n")
    lines.append(f"- Documentation Quality: {metrics.get('documentation_quality', 0):.2f}\n\n")
    # Trend analysis
    if trends:
        lines.append("**Trend Analysis**\n")
        lines.append(f"Trend: {trends.get('trend', 'unknown')} – {trends.get('message', '')}\n")
        improving = trends.get('improving_metrics', [])
        declining = trends.get('declining_metrics', [])
        if improving:
            lines.append(f"- Improving: {', '.join(improving)}\n")
        if declining:
            lines.append(f"- Declining: {', '.join(declining)}\n")
    lines.append("---\n")
    return "".join(lines)

# Helper: save critique together with monitoring data
def save_critique_with_monitoring(critique: dict, efficacy_metrics: dict):
    """Persist critique JSON including a 'model_monitoring_efficacy' field.
    The file is stored in CRITIQUES_DIR with a deterministic hash‑based name.
    """
    # Merge efficacy metrics under a dedicated key
    critique_copy = dict(critique)  # shallow copy to avoid mutating caller
    critique_copy['model_monitoring_efficacy'] = efficacy_metrics
    filename = f"critique_{hash(critique_copy.get('query', 'unknown')) % 10000}.json"
    with open(CRITIQUES_DIR / filename, 'w') as f:
        json.dump(critique_copy, f, indent=2)


class ModelMonitoringEfficacy:
    """Monitors and evaluates model efficacy during M2 execution by analyzing critique text"""

    def __init__(self):
        self.metrics_history = []

    def capture_model_efficacy(self, critique_text: str) -> dict:
        """Capture model monitoring metrics during M2 execution"""
        metrics = {
            "accuracy_score": self._estimate_accuracy(critique_text),
            "f1_score": self._estimate_f1(critique_text),
            "code_quality_score": self._extract_code_quality(critique_text),
            "test_coverage": self._extract_test_coverage(critique_text),
            "edge_case_handling": self._analyze_edge_cases(critique_text),
            "complexity_score": self._calculate_complexity(critique_text),
            "performance_rating": self._extract_performance(critique_text),
            "security_issues": self._count_security_issues(critique_text),
            "error_handling": self._analyze_error_handling(critique_text),
            "documentation_quality": self._extract_doc_quality(critique_text),
        }
        metrics["overall_efficacy_score"] = self._calculate_overall_score(metrics)
        self.metrics_history.append(metrics)
        return metrics

    def _estimate_accuracy(self, critique_text: str) -> float:
        """Estimate accuracy score based on bug/edge case mentions"""
        critique_lower = critique_text.lower()
        score = 100.0
        bug_indicators = ["bug", "error", "fail", "issue", "problem", "defect", "flaw"]
        for indicator in bug_indicators:
            if indicator in critique_lower:
                score -= 5.0
        edge_case_indicators = ["edge case", "corner case", "boundary", "unhandled"]
        for indicator in edge_case_indicators:
            if indicator in critique_lower:
                score -= 3.0
        return max(0.0, min(100.0, score))

    def _estimate_f1(self, critique_text: str) -> float:
        """Estimate F1 score based on precision/recall implications"""
        critique_lower = critique_text.lower()
        score = 80.0
        if "false positive" in critique_lower:
            score -= 10.0
        if "false negative" in critique_lower:
            score -= 10.0
        if "precision" in critique_lower:
            score += 5.0
        if "recall" in critique_lower:
            score += 5.0
        return max(0.0, min(100.0, score))

    def _extract_code_quality(self, critique_text: str) -> float:
        """Extract code quality score from pattern/style mentions"""
        critique_lower = critique_text.lower()
        score = 75.0
        positive_indicators = ["clean", "readable", "maintainable", "well-structured", "good practice"]
        for indicator in positive_indicators:
            if indicator in critique_lower:
                score += 5.0
        negative_indicators = ["messy", "unclear", "complex", "convoluted", "poor style", "anti-pattern"]
        for indicator in negative_indicators:
            if indicator in critique_lower:
                score -= 5.0
        return max(0.0, min(100.0, score))

    def _extract_test_coverage(self, critique_text: str) -> float:
        """Extract test coverage estimate from testing mentions"""
        critique_lower = critique_text.lower()
        score = 60.0
        if "test" in critique_lower:
            if "unit test" in critique_lower:
                score += 15.0
            if "integration test" in critique_lower:
                score += 10.0
            if "test coverage" in critique_lower:
                import re
                match = re.search(r"(\d+)%", critique_text)
                if match:
                    score = float(match.group(1))
                else:
                    score += 20.0
        else:
            score -= 20.0
        if "untested" in critique_lower or "lack of test" in critique_lower:
            score -= 30.0
        return max(0.0, min(100.0, score))

    def _analyze_edge_cases(self, critique_text: str) -> float:
        """Analyze edge case handling from critique"""
        critique_lower = critique_text.lower()
        score = 70.0
        edge_case_terms = ["edge case", "boundary condition", "corner case", "edge condition"]
        handled_terms = ["handles", "considers", "accounts for", "covers"]
        missed_terms = ["misses", "does not handle", "fails to", "overlooks", "ignores"]
        edge_mentioned = any(term in critique_lower for term in edge_case_terms)
        if edge_mentioned:
            handled = any(term in critique_lower for term in handled_terms)
            missed = any(term in critique_lower for term in missed_terms)
            if handled and not missed:
                score += 20.0
            elif missed and not handled:
                score -= 20.0
            elif handled and missed:
                score += 0.0
            else:
                score += 5.0
        else:
            score -= 10.0
        return max(0.0, min(100.0, score))

    def _calculate_complexity(self, critique_text: str) -> float:
        """Calculate complexity score (lower is better)"""
        critique_lower = critique_text.lower()
        score = 80.0
        complexity_indicators = ["complex", "complicated", "convoluted", "intricate", "elaborate"]
        simplicity_indicators = ["simple", "straightforward", "clear", "straight-forward"]
        for indicator in complexity_indicators:
            if indicator in critique_lower:
                score -= 10.0
        for indicator in simplicity_indicators:
            if indicator in critique_lower:
                score += 5.0
        if "nested" in critique_lower:
            if "deeply nested" in critique_lower:
                score -= 15.0
            else:
                score -= 5.0
        return max(0.0, min(100.0, score))

    def _extract_performance(self, critique_text: str) -> float:
        """Extract performance rating from critique"""
        critique_lower = critique_text.lower()
        score = 75.0
        perf_indicators = ["performance", "slow", "fast", "efficient", "inefficient", "optimization"]
        for indicator in perf_indicators:
            if indicator in critique_lower:
                if "slow" in critique_lower or "inefficient" in critique_lower:
                    score -= 10.0
                elif "fast" in critique_lower or "efficient" in critique_lower:
                    score += 10.0
                elif "optimization" in critique_lower:
                    score += 5.0
        return max(0.0, min(100.0, score))

    def _count_security_issues(self, critique_text: str) -> float:
        """Count security issues (higher score is better)"""
        critique_lower = critique_text.lower()
        score = 100.0
        security_indicators = ["security", "vulnerability", "exploit", "injection", "breach", "unsafe"]
        for indicator in security_indicators:
            if indicator in critique_lower:
                score -= 15.0
        high_risk = ["sql injection", "xss", "csrf", "buffer overflow", "race condition"]
        for item in high_risk:
            if item in critique_lower:
                score -= 25.0
        return max(0.0, min(100.0, score))

    def _analyze_error_handling(self, critique_text: str) -> float:
        """Analyze error handling quality"""
        critique_lower = critique_text.lower()
        score = 70.0
        error_terms = ["error", "exception", "try", "catch", "handle"]
        if any(term in critique_lower for term in error_terms):
            if "proper error handling" in critique_lower or "good error handling" in critique_lower:
                score += 20.0
            elif "poor error handling" in critique_lower or "lack of error handling" in critique_lower:
                score -= 20.0
            elif "unhandled exception" in critique_lower:
                score -= 25.0
        else:
            score -= 10.0
        return max(0.0, min(100.0, score))

    def _extract_doc_quality(self, critique_text: str) -> float:
        """Extract documentation quality score"""
        critique_lower = critique_text.lower()
        score = 60.0
        doc_terms = ["document", "comment", "docstring", "readme"]
        if any(term in critique_lower for term in doc_terms):
            if "well documented" in critique_lower or "good documentation" in critique_lower:
                score += 25.0
            elif "poorly documented" in critique_lower or "lack of documentation" in critique_lower:
                score -= 20.0
            elif "needs documentation" in critique_lower:
                score -= 10.0
        else:
            score -= 10.0
        return max(0.0, min(100.0, score))

    def _calculate_overall_score(self, metrics: dict) -> float:
        """Calculate overall efficacy score (0-100) from individual metrics"""
        weights = {
            "accuracy_score": 0.15,
            "f1_score": 0.10,
            "code_quality_score": 0.15,
            "test_coverage": 0.10,
            "edge_case_handling": 0.10,
            "complexity_score": 0.10,
            "performance_rating": 0.10,
            "security_issues": 0.10,
            "error_handling": 0.05,
            "documentation_quality": 0.05,
        }
        weighted_sum = sum(metrics[m] * w for m, w in weights.items() if m in metrics)
        total_weight = sum(w for m, w in weights.items() if m in metrics)
        return weighted_sum / total_weight if total_weight else 0.0

    def get_trend_analysis(self) -> dict:
        """Get trend analysis from historical metrics"""
        if len(self.metrics_history) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Need at least 2 data points for trend analysis",
                "improving_metrics": [],
                "declining_metrics": [],
            }
        trends = {}
        metric_names = [m for m in self.metrics_history[0].keys() if m != "overall_efficacy_score"]
        for metric in metric_names:
            values = [h.get(metric, 0) for h in self.metrics_history]
            mid = len(values) // 2
            first_avg = sum(values[:mid]) / len(values[:mid]) if mid else values[0]
            second_avg = sum(values[mid:]) / len(values[mid:]) if values[mid:] else values[-1]
            diff = second_avg - first_avg
            if diff > 2.0:
                trends[metric] = "improving"
            elif diff < -2.0:
                trends[metric] = "declining"
            else:
                trends[metric] = "stable"
        improving = [m for m, t in trends.items() if t == "improving"]
        declining = [m for m, t in trends.items() if t == "declining"]
        overall = "stable"
        if len(improving) > len(declining):
            overall = "improving"
        elif len(declining) > len(improving):
            overall = "declining"
        return {
            "trend": overall,
            "message": f"Model efficacy is {overall} based on {len(self.metrics_history)} evaluations",
            "improving_metrics": improving,
            "declining_metrics": declining,
            "metric_trends": trends,
            "data_points": len(self.metrics_history),
        }



class BrainAI:
    def __init__(self):
        self.venv_python = BRAIN_AI_ROOT / "venv" / "bin" / "python"
        self.main_script = BRAIN_AI_ROOT / "brain_ai" / "src" / "brain_ai" / "main.py"

    def run(self, prompt: str = None) -> str:
        """Run Brain AI with optional prompt"""
        cmd = [str(self.venv_python), "-m", "brain_ai.main"]

        if prompt:
            import os
            os.environ["BRAIN_AI_PROMPT"] = prompt

        src_dir = BRAIN_AI_ROOT / "brain_ai" / "src"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(src_dir),  # <-- Run from src/, not root
            env={**os.environ, "PYTHONPATH": str(src_dir)}
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
        """Analyze code and return structured critique with model monitoring efficacy"""
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

        # Integrate model monitoring efficacy (M2 execution)
        monitoring = ModelMonitoringEfficacy()
        efficacy_metrics = monitoring.capture_model_efficacy(result.get('critique', ''))
        monitoring_section = format_monitoring_section(efficacy_metrics, monitoring.get_trend_analysis())
        result['critique'] = result.get('critique', '') + "\n\n" + monitoring_section

        # Save critique including monitoring data
        save_critique_with_monitoring(result, efficacy_metrics)

        return result

    def critique(self, code: str) -> str:
        """Get Brain AI critique of code"""
        return self.brain.critique(code)

    def plan(self, task: str) -> str:
        """Get Brain AI plan for task"""
        return self.brain.plan(task)

    def save_critique(self, critique: dict):
        """Legacy save (kept for backward compatibility)"""
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

    def psychoanalytic_critique(self, code: str, task: str) -> str:
        """Run psychoanalytic: Id -> Superego -> Ego"""
        from crewai import Agent, Task, Crew, LLM
        from config import (get_psycho_model, OLLAMA_BASE_URL, ID_TEMPERATURE, SUPERCERO_TEMPERATURE, EGO_TEMPERATURE)

        # Id Agent - uses ID_MODEL from config
        id_agent = Agent(
            role="Id - Impulsive Critic",
            goal="Find bugs",
            backstory="Impulsive brutal",
            verbose=False,
            llm=LLM(
                model=get_psycho_model('id'),
                base_url=OLLAMA_BASE_URL,
                temperature=ID_TEMPERATURE,
            ),
        )
        id_desc = "ID: " + task + "\n" + code
        id_res = Crew(agents=[id_agent], tasks=[Task(description=id_desc, agent=id_agent, expected_output="x")], verbose=False).kickoff().raw

        # Superego Agent - uses SUPERCERO_MODEL from config
        superego_agent = Agent(
            role="Superego - Perfectionist Guardian",
            goal="Quality",
            backstory="Perfectionist",
            verbose=False,
            llm=LLM(
                model=get_psycho_model('superego'),
                base_url=OLLAMA_BASE_URL,
                temperature=SUPERCERO_TEMPERATURE,
            ),
        )
        sg_desc = "SUPEREGO: " + task + "\n" + code
        sg_res = Crew(agents=[superego_agent], tasks=[Task(description=sg_desc, agent=superego_agent, expected_output="x")], verbose=False).kickoff().raw

        # Ego Agent - uses EGO_MODEL from config
        ego_agent = Agent(
            role="Ego - Rational Mediator",
            goal="Balance",
            backstory="Mediator",
            verbose=False,
            llm=LLM(
                model=get_psycho_model('ego'),
                base_url=OLLAMA_BASE_URL,
                temperature=EGO_TEMPERATURE,
            ),
        )
        eg_desc = "EGO: ID: " + id_res + " SUP: " + sg_res + " TASK: " + task
        ego_res = Crew(agents=[ego_agent], tasks=[Task(description=eg_desc, agent=ego_agent, expected_output="x")], verbose=False).kickoff().raw
        return ego_res

def _legacy_get_brain_critique(code: str) -> str:
    return BrainAIWrapper().critique(code)

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
