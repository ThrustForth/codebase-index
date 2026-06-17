# brain_modes/brain_mode_m3_dreamer.py
import time
import os
import json
from datetime import datetime

ROOT = "/home/mine/projects/codebase-index"
BRAIN_MODES = f"{ROOT}/brain_modes"

MAP_JSON = f"{BRAIN_MODES}/project_map.json"
MAP_MD = f"{BRAIN_MODES}/project_map.md"
DREAMS_DIR = f"{BRAIN_MODES}/dreams"
DREAM_STATE = f"{DREAMS_DIR}/dream_state.json"
DREAM_INDEX = f"{DREAMS_DIR}/dream_index.json"

GPU_TARGET = 0.2  # conceptual 20%

def load_m1_data():
    # Placeholder: load recent sessions, critiques, tool changes
    # In real impl, read from brain_modes/reflections/ or critiques/
    return {
        "sessions": [],
        "critiques": [],
        "tool_changes": [],
    }

def load_m2_data():
    if not os.path.exists(MAP_JSON):
        return {"map": None}
    with open(MAP_JSON, "r") as f:
        return {"map": json.load(f)}

def load_previous_dream_state():
    if not os.path.exists(DREAM_STATE):
        return {}
    with open(DREAM_STATE, "r") as f:
        return json.load(f)

def generate_dream_diary(m1_data, m2_data, prev_state):
    # In real impl, this would call an LLM with creative temperature
    # Here, we just produce a placeholder structure.
    diary = {
        "timestamp": datetime.now().isoformat(),
        "observations": [
            "Project map is stable.",
            "No major changes detected since last dream.",
        ],
        "hypotheses": [
            "Repeated critique patterns may indicate missing tool for X.",
            "Some modules may need more tests.",
        ],
        "repeated_failures": [],
        "possible_fixes": [
            "Add validation for CLI arguments.",
            "Consider adding a new tool for static analysis.",
        ],
        "open_questions": [
            "Should we split code_puppy and brain_ai into sub-packages?",
        ],
        "prev_state_summary": prev_state,
    }
    return diary

def write_dream_artifacts(diary):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    diary_md_path = os.path.join(DREAMS_DIR, f"dream_diary_{ts}.md")
    diary_json_path = os.path.join(DREAMS_DIR, f"dream_diary_{ts}.json")

    # JSON
    with open(diary_json_path, "w") as f:
        json.dump(diary, f, indent=2)

    # Markdown
    md_lines = [
        f"# Dream Diary ({diary['timestamp']})",
        "",
        "## Observations",
    ]
    for o in diary["observations"]:
        md_lines.append(f"- {o}")
    md_lines.append("\n## Hypotheses")
    for h in diary["hypotheses"]:
        md_lines.append(f"- {h}")
    md_lines.append("\n## Possible Fixes")
    for f in diary["possible_fixes"]:
        md_lines.append(f"- {f}")
    md_lines.append("\n## Open Questions")
    for q in diary["open_questions"]:
        md_lines.append(f"- {q}")

    with open(diary_md_path, "w") as f:
        f.write("\n".join(md_lines))

    # Update dream_state
    with open(DREAM_STATE, "w") as f:
        json.dump(diary, f, indent=2)

    # dream_index
    index = {
        "latest_diary": diary_md_path,
        "timestamp": diary["timestamp"],
    }
    with open(DREAM_INDEX, "w") as f:
        json.dump(index, f, indent=2)

    print(f"[M3] dream diary written: {diary_md_path}")

def main():
    print("[M3] dreamer started: will dream about M1 and M2 output")

    while True:
        # One dream cycle
        m1_data = load_m1_data()
        m2_data = load_m2_data()
        prev_state = load_previous_dream_state()

        diary = generate_dream_diary(m1_data, m2_data, prev_state)
        write_dream_artifacts(diary)

        # Sleep until next cycle (e.g., every 4 hours)
        time.sleep(4 * 3600)
        print("[M3] next dream cycle starting...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[M3] dreamer shutting down...")
