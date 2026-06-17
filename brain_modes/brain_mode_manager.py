# brain_modes/brain_mode_manager.py
import time
import os
import subprocess
import signal
import sys

ROOT = "/home/mine/projects/codebase-index"
BRAIN_MODES = f"{ROOT}/brain_modes"

IDLE_SHORT = 60   # seconds → M2
IDLE_LONG = 3600  # seconds → M3 (1 hour)

LAST_ACTIVITY_FILE = f"{BRAIN_MODES}/last_activity.txt"
CURRENT_MODE_FILE = f"{BRAIN_MODES}/current_mode.txt"
MAP_READY_FILE = f"{BRAIN_MODES}/map_ready.txt"

WORKER_PIDS = {
    "M2": None,
    "M3": None,
}

def record_activity():
    try:
        with open(LAST_ACTIVITY_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception as e:
        print(f"[manager] error recording activity: {e}")

def idle_time():
    try:
        with open(LAST_ACTIVITY_FILE, "r") as f:
            last = float(f.read().strip())
        return time.time() - last
    except:
        return 0

def set_mode(mode):
    with open(CURRENT_MODE_FILE, "w") as f:
        f.write(mode)

def get_mode():
    try:
        with open(CURRENT_MODE_FILE, "r") as f:
            return f.read().strip()
    except:
        return "M1"

def is_map_ready():
    return os.path.exists(MAP_READY_FILE)

def decide_mode():
    idle = idle_time()
    if idle < IDLE_SHORT:
        return "M1"
    elif idle < IDLE_LONG:
        return "M2"
    else:
        if is_map_ready():
            return "M3"
        else:
            return "M2"

def stop_worker(mode):
    pid = WORKER_PIDS.get(mode)
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            WORKER_PIDS[mode] = None
        except Exception as e:
            print(f"[manager] error stopping worker {mode}: {e}")

def run_mode_worker(mode):
    if mode == "M2":
        stop_worker("M2")
        p = subprocess.Popen(
            ["python", f"{ROOT}/brain_modes/brain_mode_m2_mapper.py"],
            cwd=ROOT,
        )
        WORKER_PIDS["M2"] = p.pid
        print(f"[manager] started M2 mapper worker (pid={p.pid})")
    elif mode == "M3":
        stop_worker("M3")
        p = subprocess.Popen(
            ["python", f"{ROOT}/brain_modes/brain_mode_m3_dreamer.py"],
            cwd=ROOT,
        )
        WORKER_PIDS["M3"] = p.pid
        print(f"[manager] started M3 dreamer worker (pid={p.pid})")

def main():
    # Initial mode
    if idle_time() > IDLE_LONG and is_map_ready():
        mode = "M3"
    elif idle_time() > IDLE_SHORT:
        mode = "M2"
    else:
        mode = "M1"

    set_mode(mode)
    if mode in ["M2", "M3"]:
        run_mode_worker(mode)

    print(f"[manager] started in mode {mode}")
    print("[manager] this mode is always on and doing something productive.")
    print("[manager] type any cp command to interact (switches to M1).")

    # Background loop
    while True:
        time.sleep(15)
        new_mode = decide_mode()
        if new_mode != mode:
            print(f"[manager] transitioning from {mode} to {new_mode}")
            # Stop old worker
            if mode in ["M2", "M3"]:
                stop_worker(mode)
            mode = new_mode
            set_mode(mode)
            if mode in ["M2", "M3"]:
                run_mode_worker(mode)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[manager] shutting down...")
        stop_worker("M2")
        stop_worker("M3")
        sys.exit(0)
