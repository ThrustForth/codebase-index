"""Generate pytest tests for uncovered code using Ollama.

Extracts the full source of a target function (including its body) and sends it to Ollama
to generate a desired number of pytest test cases.
"""

import json
import re
from pathlib import Path
import ollama

def extract_function_names(source: str) -> list:
    """Return a list of all top‑level function names in *source*.

    Uses a simple regex that matches ``def name(`` and ignores methods inside classes.
    """
    pattern = r"^def\s+(\w+)\s*\("  # start of line, def, name, opening paren
    return re.findall(pattern, source, flags=re.MULTILINE)

def get_full_function(source: str, function_name: str) -> str | None:
    """Return the complete source of *function_name* including its indented body.

    The implementation captures the ``def`` line and all following lines that are
    indented more than the ``def`` line. It stops when it encounters another top‑level
    ``def`` or ``class`` declaration or reaches EOF.
    """
    # Locate the start of the function definition.
    start_match = re.search(rf"^def\s+{re.escape(function_name)}\s*\([^\n]*\):", source, flags=re.MULTILINE)
    if not start_match:
        return None
    start_idx = start_match.start()

    # Determine the indentation level of the ``def`` line.
    def_line = source[start_match.start():source.find('\n', start_match.end())]
    indent_match = re.match(r"^(\s*)", def_line)
    base_indent = indent_match.group(1) if indent_match else ""

    # Scan forward line by line until a line with less indentation appears.
    lines = source[start_idx:].splitlines(keepends=True)
    function_lines = []
    for line in lines:
        # First line is always included.
        function_lines.append(line)
        # Look ahead to the next line to decide whether to stop.
        if line is lines[-1]:
            break
        next_line = lines[lines.index(line) + 1]
        # Empty lines are part of the function.
        if next_line.strip() == "":
            continue
        # If the next line starts at column 0 or less indentation than the base, stop.
        next_indent = re.match(r"^(\s*)", next_line).group(1)
        if len(next_indent) <= len(base_indent) and not next_line.lstrip().startswith("@"):
            # Reached a new top‑level block.
            break
    return "".join(function_lines)

def generate_tests(file_path: str, target: str | None = None, cases: int = 5) -> dict:
    """Generate pytest tests for *target* function in *file_path*.

    If *target* is ``None`` the first public (non‑private) function is used.
    Returns a dictionary with information about the generated test file.
    """
    source = Path(file_path).read_text()

    # Choose the function to test.
    if not target:
        candidates = [n for n in extract_function_names(source) if not n.startswith("_")]
        if not candidates:
            return {"error": "No public functions found", "all_functions": extract_function_names(source)}
        target = candidates[0]

    function_code = get_full_function(source, target)
    if not function_code:
        return {"error": f"Function {target} not found"}

    # Build a prompt for Ollama.
    prompt = f"""Generate exactly {cases} pytest test cases for the following Python function.

{function_code}

- Use plain pytest (no unittest).
- Cover edge cases and error handling.
- Do not include any explanatory text or markdown.
"""
    try:
        resp = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt}])
        test_code = resp["message"]["content"].strip()
    except Exception as exc:
        return {"error": f"Ollama request failed: {exc}"}

    test_path = Path(file_path).parent / f"test_{Path(file_path).name}"
    test_content = (
        "import pytest\n"
        f"# from {Path(file_path).stem} import {target}\n\n"
        f"{test_code}\n"
    )
    test_path.write_text(test_content)

    return {
        "test_file": str(test_path),
        "function_tested": target,
        "cases_requested": cases,
    }

if __name__ == "__main__":
    import sys
    fp = sys.argv[1] if len(sys.argv) > 1 else "code_puppy_tool.py"
    fn = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(generate_tests(fp, fn), indent=2))
