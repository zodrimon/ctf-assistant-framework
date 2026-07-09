# Learning Log

This file explains, in plain language, what was built at each step and why.

---
### TASK-002 — Add dev tooling
**Date:** 2026-07-09
**What I built:** Added development tooling configurations for the project, including `pytest` for testing, `black` and `ruff` for code formatting and linting, and `pre-commit` to run these checks automatically before code is committed.
**Key concepts:** 
- **Linters/Formatters:** Tools like `black` and `ruff` automatically check for code style issues and format the code so it looks consistent across all files.
- **pre-commit:** A framework that runs checks automatically whenever you try to create a new `git commit`, preventing bad code from being saved to the history.
**How it fits together:** This tooling does not directly affect the engine or the CTF modules described in the architecture. Instead, it forms the foundation for writing the engine and modules cleanly, ensuring all future code follows the same standard.
**Files touched:** 
- `pyproject.toml`
- `.pre-commit-config.yaml`

---
### TASK-003 — Define Module and Workflow interfaces
**Date:** 2026-07-09
**What I built:** I created the base interfaces (blueprints) for all CTF modules and workflows in a new file `base.py`. These interfaces define what a module and a workflow must look like, ensuring they have standardized methods like `analyze()` and `run()`.
**Key concepts:** 
- **Interfaces/Protocols:** In Python, a Protocol is like a contract. It says "any module you build must have these specific functions." This allows the main engine to run any module without needing to know what the module actually does inside.
- **Modularity:** By using a standard interface, we can easily plug in new forensic tools later without changing the core investigation engine.
**How it fits together:** This is the foundation of Rule #6 in the architecture. Every new evidence analyzer (like a file analyzer or memory forensics tool) will inherit from this `Module` interface so the `WorkflowRunner` knows exactly how to interact with it.
**Files touched:** 
- `src/ctf_assistant/modules/base.py`
- `src/ctf_assistant/modules/__init__.py`

---
### TASK-004 — Build the Session state manager
**Date:** 2026-07-09
**What I built:** I created the `Session` class which tracks everything that happens during an investigation. It stores findings from modules and can save all of its data to a JSON file on disk, and load it back up later.
**Key concepts:** 
- **State Management/Serialization:** "State" is all the data generated so far. "Serialization" means taking that live data in memory (like Python objects) and converting it into a string format (like JSON) so it can be written to a hard drive and restored later without losing any information.
**How it fits together:** If you stop an investigation halfway or if the power goes out, the `Session` JSON file acts as a save game. The `WorkflowRunner` uses this Session to remember what steps were already completed and what evidence was already found.
**Files touched:** 
- `src/ctf_assistant/engine/session.py`
- `src/ctf_assistant/engine/__init__.py`
- `tests/test_session.py`
