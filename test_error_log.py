#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/mine/projects/codebase-index')
from brain_coordinator import BrainCoordinator
import os
import tempfile
import shutil

# Create a temporary directory for project path to avoid interfering with real data
tmpdir = tempfile.mkdtemp()
print(f"Using temporary project path: {tmpdir}")

# Initialize BrainCoordinator with temp path
bc = BrainCoordinator(project_path=tmpdir)

# Override critiques dir to be inside tmpdir
bc.critiques_dir = bc.project_path / "critiques"
bc.critiques_dir.mkdir(parents=True, exist_ok=True)

# Dummy task and result
task = {
    "type": "test",
    "file": "test_file.py",
    "prompt": "Test prompt"
}
result = "Something went wrong: Error: import failed"
critique = "This is a test critique."

# Call save_critique
critique_file = bc.save_critique(task, result, critique)
print(f"Saved critique to: {critique_file}")

# Check if errors.log was written
error_log = bc.project_path / "errors.log"
if error_log.exists():
    print("errors.log found:")
    with open(error_log, 'r') as f:
        print(f.read())
else:
    print("errors.log not found.")

# Cleanup
shutil.rmtree(tmpdir)
print("Cleaned up temp directory.")