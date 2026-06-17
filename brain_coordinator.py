#!/usr/bin/env python3
"""Brain Coordinator - Runs M2/M3 self-improvement loop in background with required-section validation"""

import os
import json
import subprocess
import time
import hashlib
import secrets
import shlex
from pathlib import Path
from datetime import datetime, timedelta
from brain_ai_wrapper import ModelMonitoringEfficacy, format_monitoring_section, save_critique_with_monitoring

# Required sections that MUST appear in every fix proposal
REQUIRED_SECTIONS = [
    "Alternatives considered",
    "Chosen solution",
    "Why this solution is better",
    "Tradeoffs",
    "Constraints"
]

MAX_FIX_RETRY = 3


class BrainCoordinator:
    def __init__(self, project_path: str = "~/projects/codebase-index"):
        self.project_path = Path(project_path).expanduser()
        self.critiques_dir = self.project_path / "critiques"
        self.agents_file = self.project_path / "AGENTS.md"
        self.map_file = self.project_path / "brain_modes" / "project_map.json"

        self.critiques_dir.mkdir(parents=True, exist_ok=True)
        self.map_file.parent.mkdir(parents=True, exist_ok=True)

    def get_file_hash(self, file_path: Path) -> str:
        try:
            return hashlib.md5(file_path.read_bytes()).hexdigest()
        except:
            return ""

    def validate_fix_proposal(self, response: str, task_type: str = "fix_proposal") -> bool:
        """
        Return True if the response contains all required sections.
        Skip validation for brain-council audits (task_type != "fix_proposal").
        """
        # Skip validation for audits — only enforce on fix proposals
        if task_type != "fix_proposal":
            return True

        if not response:
            return False
        for section in REQUIRED_SECTIONS:
            if section.lower() not in response.lower():
                return False
        return True

    def get_fix_with_validation(self, task_prompt: str) -> str:
        """
        Run M1 task with auto-retry if required sections are missing.
        """
        prompt = task_prompt

        # Inject required-section template if not already present
        if "\n\nWhen proposing a fix, you MUST include:\n" not in prompt:
            prompt = (
                f"{task_prompt}\n\n"
                "When proposing a fix, you MUST include:\n\n"
                f"- {REQUIRED_SECTIONS[0]}\n"
                f"- {REQUIRED_SECTIONS[1]}\n"
                f"- {REQUIRED_SECTIONS[2]}\n"
                f"- {REQUIRED_SECTIONS[3]}\n"
                f"- {REQUIRED_SECTIONS[4]}\n\n"
                "Do not skip any section. If any section is missing, the solution is invalid."
            )

        for attempt in range(MAX_FIX_RETRY):
            result = self.run_m1_task(prompt)

            if self.validate_fix_proposal(result):
                return result

            if attempt < MAX_FIX_RETRY - 1:
                # Augment prompt to force structure on retry
                prompt = (
                    f"{task_prompt}\n\n"
                    "Your previous response was incomplete. You MUST include all of these sections:\n\n"
                    f"- {REQUIRED_SECTIONS[0]}\n"
                    f"- {REQUIRED_SECTIONS[1]}\n"
                    f"- {REQUIRED_SECTIONS[2]}\n"
                    f"- {REQUIRED_SECTIONS[3]}\n"
                    f"- {REQUIRED_SECTIONS[4]}\n\n"
                    "Do not skip any section. If any section is missing, the solution is invalid.\n\n"
                    "Please regenerate your response with all sections included."
                )

        raise ValueError(
            "Fix proposal failed validation after multiple retries. "
            "The model did not include all required sections."
        )

    def update_file_map(self) -> dict:
        file_map = {}
        for py_file in self.project_path.rglob("*.py"):
            if any(part in str(py_file) for part in ['venv', '__pycache__', '.git']):
                continue
            file_map[str(py_file)] = {
                "hash": self.get_file_hash(py_file),
                "size": py_file.stat().st_size,
                "modified": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
            }
        self.map_file.write_text(json.dumps(file_map, indent=2))
        return file_map

    def find_recent_changes(self, file_map: dict, hours: int = 1) -> list:
        changes = []
        for file_path, info in file_map.items():
            modified = datetime.fromisoformat(info["modified"])
            if modified > datetime.now() - timedelta(hours=hours):
                changes.append(file_path)
        return changes

    def find_orphaned_patterns(self, file_map: dict) -> list:
        orphans = []
        for file_path, info in file_map.items():
            if info["size"] == 0:
                orphans.append(file_path)
        return orphans

    def find_tasks(self, file_map: dict) -> list:
        tasks = []
        for file_path in self.find_recent_changes(file_map, hours=1):
            tasks.append({"type": "recent_change", "file": file_path, "prompt": f"Review recent changes to {file_path}"})
        for file_path in self.find_orphaned_patterns(file_map):
            tasks.append({"type": "orphaned", "file": file_path, "prompt": f"Check if {file_path} is orphaned"})
        if len(tasks) == 0:
            py_files = [f for f in self.project_path.rglob("*.py") if 'venv' not in str(f)]
            if py_files:
                random_file = secrets.choice(list(py_files)[:50])
                tasks.append({"type": "random_review", "file": str(random_file), "prompt": f"Code review: {random_file}"})
        return tasks

    def run_m1_task(self, task_prompt: str) -> str:
        try:
            # Escape the task_prompt to prevent shell injection
            safe_prompt = shlex.quote(task_prompt)
            cmd = f"cd {self.project_path} && echo '{safe_prompt}' | timeout 60 uvx code-puppy 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"M1 Error: {str(e)}"

    def run_m3_critique(self, task: dict, result: str) -> str:
        try:
            from brain_ai_wrapper import BrainAI
            critique = BrainAI().critique(f"Task Type: {task['type']}\nFile: {task['file']}\nTask: {task['prompt']}\nResult: {result}\n\nPlease critique this work and identify: 1. Security gaps 2. Quality issues 3. Missing edge cases 4. Suggestions for improvement 5. New tools that should be added")
            return critique
        except Exception as e:
            return f"M3 Critique Error: {str(e)}"

    def save_critique(self, task: dict, result: str, critique: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        critique_id = f"critique_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
        critique_data = {
            "id": critique_id,
            "timestamp": timestamp,
            "task_type": task["type"],
            "task_file": task["file"],
            "task_prompt": task["prompt"],
            "result": result,
            "critique": critique,
            "improvements": self.extract_improvements(critique),
        }
        monitoring = ModelMonitoringEfficacy()
        efficacy = monitoring.capture_model_efficacy(critique_data.get('critique', ''))
        critique_data['model_monitoring_efficacy'] = efficacy
        monitoring_section = format_monitoring_section(efficacy, monitoring.get_trend_analysis())
        critique_data['critique'] = critique_data.get('critique', '') + '\n\n' + monitoring_section
        critique_file = self.critiques_dir / f"{critique_id}.json"
        critique_file.write_text(json.dumps(critique_data, indent=2))

        if 'Error:' in result or 'cannot import' in result:
            error_log_path = self.project_path / "errors.log"
            with open(error_log_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] - Error detected: {result}\n")

        return str(critique_file)

    def extract_improvements(self, critique: str) -> list:
        improvements = []
        if "new tool" in critique.lower(): improvements.append("Add new tool")
        if "security" in critique.lower(): improvements.append("Security fix needed")
        if "quality" in critique.lower(): improvements.append("Quality improvement")
        return improvements

    def save_decision_log(self, task: dict, result: str, critique: str, passed: bool, score: float | None = None):
        """Auto-save decision log for benchmark-style scoring"""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        log_path = self.critiques_dir / f"decision-log-{timestamp}.json"

        entry = {
            "timestamp": timestamp,
            "task_type": task["type"],
            "task_file": task["file"],
            "task_prompt": task["prompt"],
            "result": result,
            "critique": critique,
            "passed": passed,
            "score": score,
        }

        log_path.write_text(json.dumps(entry, indent=2))

    def run_critique_loop(self, interval: int = 60):
        print(f"🧠 Brain Coordinator starting critique loop (interval: {interval}s)")
        prev_map = {}
        if self.map_file.exists(): prev_map = json.loads(self.map_file.read_text())

        while True:
            try:
                file_map = self.update_file_map()
                new_count = sum(1 for f in file_map if f not in prev_map)
                modified_count = sum(1 for f in file_map if f in prev_map and file_map[f]["hash"] != prev_map[f]["hash"])
                deleted_count = sum(1 for f in prev_map if f not in file_map)
                print(f"[M2] Map updated: {len(file_map)} files total, {new_count} new, {modified_count} modified, {deleted_count} deleted")

                tasks = self.find_tasks(file_map)
                if tasks:
                    print(f"[M2] Found {len(tasks)} tasks")
                    for task in tasks:
                        try:
                            result = self.get_fix_with_validation(task["prompt"])
                        except ValueError as e:
                            print(f"[M2] Validation failed for task: {e}")
                            result = f"[VALIDATION FAILED] {e}"

                        critique = self.run_m3_critique(task, result)
                        critique_file = self.save_critique(task, result, critique)

                        # Auto-save decision log with pass/fail based on validation
                        passed = self.validate_fix_proposal(result, task["type"])
                        self.save_decision_log(task, result, critique, passed, score=None)

                        print(f"[M2] Saved critique: {critique_file}")
                else:
                    print("[M2] No tasks")
                prev_map = file_map
            except Exception as e:
                print(f"[M2] Error: {str(e)}")
            time.sleep(interval)


if __name__ == "__main__":
    BrainCoordinator().run_critique_loop(interval=60)
