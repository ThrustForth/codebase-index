## Mode System (Always-On Background Modes)

Code Puppy now has three modes that run automatically:

- **M1 (Normal)**: Interactive mode when you use `cp` commands.
- **M2 (Mapper)**: Runs when idle for ~1 minute.
  - Cleans up M3's old dream artifacts.
  - Builds and updates a project map of `codebase-index`.
  - Runs at ~30% GPU (low concurrency).
- **M3 (Dream)**: Runs when idle for ~1 hour and map is ready.
  - Dreams about M1 and M2 output (sessions, critiques, map).
  - Writes a dream diary with insights and possible improvements.
  - Runs at ~20% GPU (single-task, low concurrency).

### How to Operate

- Launch with:
  ```bash
  pl
  # select codebase-index
  ```
  The mode manager starts automatically.

- Any `cp` command:
  ```bash
  cp "search for ollama"
  cp "critique code"
  ```
  Records activity and switches to M1 (normal).

- When idle:
  - After ~1 minute → M2 (mapper) starts.
  - After ~1 hour + map ready → M3 (dream) starts.

- Interview the dream:
  ```bash
  cp "interview the dream"
  cp "what did you learn while idle?"
  cp "summarize the last dream"
  cp "show me the project map"
  ```

- The mode system is always on and doing something productive:
  - While you interact: M1.
  - While idle short: M2.
  - While idle long: M3.
