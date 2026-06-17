#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

BRAIN_RUN_FISH = Path(__file__).parent.parent / "brain-ai" / "brain_ai" / "run_brain_task.fish"

def run_brain_task(task: str) -> str:
    cmd = f"fish \"{BRAIN_RUN_FISH}\" \"{task}\""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return f"Brain AI error:\n{result.stderr}\n{result.stdout}"
    return result.stdout

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_brain_task.py <task>")
        sys.exit(1)
    task = sys.argv[1]
    print(run_brain_task(task))

