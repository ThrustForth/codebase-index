# brain_modes/brain_mode_m2_mapper.py
import time
import os
import json
import glob
import hashlib

ROOT = "/home/mine/projects/codebase-index"
BRAIN_MODES = f"{ROOT}/brain_modes"

MAP_JSON = f"{BRAIN_MODES}/project_map.json"
MAP_MD = f"{BRAIN_MODES}/project_map.md"
MAP_READY_FILE = f"{BRAIN_MODES}/map_ready.json"
CLEANUP_LOG = f"{BRAIN_MODES}/cleanup_log.json"
PREV_HASHES = f"{BRAIN_MODES}/prev_file_hashes.json"  # NEW: store previous hashes

IDLE_POLL = 10  # seconds
GPU_TARGET = 0.3  # conceptual 30%

def cleanup_m3_mess():
    dreams_dir = f"{BRAIN_MODES}/dreams"
    archive_dir = f"{dreams_dir}/archive"
    os.makedirs(archive_dir, exist_ok=True)

    kept = []
    archived = []
    deleted = []

    # Keep latest dream_diary and dream_state
    pattern = os.path.join(dreams_dir, "dream_diary_*.md")
    files = sorted(glob.glob(pattern))
    latest_diary = files[-1] if files else None

    latest_state = os.path.join(dreams_dir, "dream_state.json")

    for f in files:
        if f != latest_diary:
            archived.append(f)
            os.rename(f, os.path.join(archive_dir, os.path.basename(f)))

    old_states = [
        os.path.join(dreams_dir, s)
        for s in os.listdir(dreams_dir)
        if s.startswith("dream_state_") and s.endswith(".json")
    ]
    for f in old_states:
        archived.append(f)
        os.rename(f, os.path.join(archive_dir, os.path.basename(f)))

    cleanup_log = {
        "kept": [latest_diary, latest_state],
        "archived": archived,
        "deleted": deleted,
    }

    with open(CLEANUP_LOG, "w") as f:
        json.dump(cleanup_log, f, indent=2)

    print("[M2] cleanup completed")
    return cleanup_log

def md5_file(path):
    """Calculate MD5 hash of file content"""
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def build_file_info(path):
    # Minimal: path, size, language, symbols (placeholder)
    try:
        size = os.path.getsize(path)
    except:
        size = 0

    lang = "unknown"
    if path.endswith(".py"):
        lang = "python"
    elif path.endswith(".md"):
        lang = "markdown"
    elif path.endswith(".json"):
        lang = "json"

    symbols = []  # placeholder: parse with ast later if desired

    return {
        "path": path,
        "size_bytes": size,
        "language": lang,
        "symbols": symbols,
        "imports": [],
        "role": "unknown",
        "notes": "",
    }

def load_previous_hashes():
    """Load previous file hashes from disk"""
    if os.path.exists(PREV_HASHES):
        try:
            with open(PREV_HASHES, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_hashes(files_dict):
    """Save current file hashes to disk"""
    with open(PREV_HASHES, "w") as f:
        json.dump(files_dict, f, indent=2)

def build_project_map():
    files = []
    current_hashes = {}

    # Load previous hashes
    prev_hashes = load_previous_hashes()

    changes = {"new": [], "modified": [], "deleted": [], "unchanged": []}

    for root, dirs, filenames in os.walk(ROOT):
        # Skip venv, .git, db, etc.
        if any(x in root for x in ["/venv", "/.git", "/db", "/lancedb", "__pycache__"]):
            continue
        for name in filenames:
            path = os.path.join(root, name)
            file_hash = md5_file(path)
            current_hashes[path] = file_hash

            # Always build file info for ALL files
            info = build_file_info(path)
            info["hash"] = file_hash

            # Track changes
            if path not in prev_hashes:
                changes["new"].append(path)
                info["notes"] = "New file detected"
            elif prev_hashes[path] != file_hash:
                changes["modified"].append(path)
                info["notes"] = "File modified"
            else:
                changes["unchanged"].append(path)
                info["notes"] = ""

            files.append(info)

    # Check for deleted files
    for path in prev_hashes:
        if path not in current_hashes:
            changes["deleted"].append(path)

    # Always rebuild map with all files
    map_data = {
        "version": "1.0",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": ROOT,
        "files": files,
        "summary": {
            "total_files": len(files),
            "total_python_files": sum(1 for f in files if f["language"] == "python"),
            "changes": {
                "new": len(changes["new"]),
                "modified": len(changes["modified"]),
                "deleted": len(changes["deleted"]),
                "unchanged": len(changes["unchanged"]),
            }
        },
        "recent_changes": {
            "new_files": changes["new"][-10:],  # Last 10 new files
            "modified_files": changes["modified"][-10:],
            "deleted_files": changes["deleted"][-10:],
        }
    }

    with open(MAP_JSON, "w") as f:
        json.dump(map_data, f, indent=2)

    # Human-readable summary
    md_lines = [
        "# Project Map",
        f"Root: {ROOT}",
        f"Total files: {len(files)}",
        f"Python files: {map_data['summary']['total_python_files']}",
        f"",
        f"## Changes (last scan)",
        f"- New: {len(changes['new'])}",
        f"- Modified: {len(changes['modified'])}",
        f"- Deleted: {len(changes['deleted'])}",
        f"- Unchanged: {len(changes['unchanged'])}",
        f"",
        "## Files",
    ]
    for f in files[:100]:  # limit in MD
        md_lines.append(f"- `{f['path']}` ({f['language']}, {f['size_bytes']} bytes) {f['notes']}")

    with open(MAP_MD, "w") as f:
        f.write("\n".join(md_lines))

    # Save current hashes for next comparison
    save_hashes(current_hashes)

    print(f"[M2] Map updated: {len(files)} files total, {len(changes['new'])} new, {len(changes['modified'])} modified, {len(changes['deleted'])} deleted, {len(changes['unchanged'])} unchanged")

def main():
    print("[M2] mapper started: cleaning up M3 mess and building project map")
    cleanup_m3_mess()
    build_project_map()

    # Mark map as ready
    with open(MAP_READY_FILE, "w") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ"))

    print("[M2] map ready; continuing to update while idle")

    while True:
        time.sleep(IDLE_POLL)
        build_project_map()
        # Don't print if no changes - too noisy

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[M2] mapper shutting down...")
