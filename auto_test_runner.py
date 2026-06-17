#!/usr/bin/env python3
"""Auto-run tests after code edits and output results for bug fixes."""

import subprocess
import sys
import os
from pathlib import Path

def run_tests(test_file=None, coverage=False):
    """Run pytest and return results."""
    cmd = ['./venv/bin/pytest']

    if test_file:
        cmd.append(test_file)
    else:
        cmd.append('test_*.py')

    if coverage:
        cmd.extend(['--cov=code_puppy_tool', '--cov-report=term-missing'])

    cmd.append('-v')

    print(f"🧪 Running: {cmd}")
    print("=" * 60)

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode == 0, result.stdout, result.stderr

def on_edit(file_path):
    """Hook function called when a file is edited."""
    print(f"📝 File edited: {file_path}")

    # Run tests for the edited file
    test_file = None
    if 'code_puppy_tool' in file_path:
        test_file = 'test_code_puppy_tool.py'

    success, output, errors = run_tests(test_file, coverage=True)

    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed! Bug detected:")
        print(output)
        # Auto-suggest fix
        suggest_fix(output)

    return success, output

def suggest_fix(test_output):
    """Auto-suggest fix for failed tests."""
    print("\n💡 Suggested fix:")
    print("cp 'Fix the failing tests in test_code_puppy_tool.py. Here are the errors:'")
    print(test_output)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run as CLI: auto_test_runner.py test_code_puppy_tool.py
        success, output = run_tests(sys.argv[1], coverage=True)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success, output = run_tests(None, coverage=True)
        sys.exit(0 if success else 1)
