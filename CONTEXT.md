# CONTEXT.md — Read this file completely before doing anything else.

> This file is the project's memory. You (the AI builder) have no memory between
> sessions. Everything you need to resume correctly must be read from here and
> from TASKS.md. At the end of every task, you MUST update the "Current Status"
> section below before committing.

---

## 1. Project Identity (do not change without explicit human approval)

**Name:** CTF Assistant Framework (working name)
**License:** MIT
**Platform:** Linux, offline-first, optional online AI

**What this is:** An interactive CTF investigation assistant. It automates
repetitive forensic reconnaissance, recommends next steps with reasoning,
searches the user's personal knowledge base (RAG), and optionally consults an
AI model — but the workflow engine must always function without AI.

**What this is NOT:**
- Not a script that auto-solves CTFs
- Not an AI that makes final decisions
- Not a thin wrapper around Linux tools with no reasoning layer

**Target users:** CTF players (beginner to advanced), security students, blue
team learners. Not enterprise incident response (not yet).

---

## 2. Architecture Rules (immutable — every task must respect these)

1. **The Investigation Engine is domain-agnostic and must never contain
   forensics-specific, web-specific, or crypto-specific logic.** New evidence
   types are added as modules/plugins, never as engine changes.
2. **Workflows are hybrid:** simple deterministic steps go in YAML
   (`workflows/*.yaml`); anything with branching logic, AI calls, or RAG
   queries goes in a Python `Workflow` subclass.
3. **Detection is multi-signal, never extension-based only:** magic bytes,
   MIME type, `file` command output, entropy, known signatures. If confidence
   is low, ask the user instead of guessing.
4. **AI is optional and advisory.** Every code path must work with AI disabled.
   AI provider access goes through the abstraction in `ai/provider.py` — never
   call a provider SDK directly from a module.
5. **Tools are wrapped via subprocess, not reimplemented.** If a required tool
   is missing, the framework prompts the user before installing anything.
6. **Every module implements the same `Module`/`Workflow` interface**
   (`modules/base.py`). Copy the File Analysis module's structure for new
   modules — it is the reference implementation.
7. **No AI-generated code touches `main` directly.** Work happens on a feature
   branch per task; the human reviews before merge (see §5).

---

## 3. Tech Stack

- Python 3.11+, `pyproject.toml` managed
- CLI/TUI: Textual (or Rich for simpler output) — terminal-first, GUI later
- RAG: ChromaDB + local `sentence-transformers` embeddings (offline-capable)
- AI providers: pluggable via a common interface; initial target Gemini,
  later OpenAI/Anthropic/OpenRouter/Ollama
- Reports: Markdown always generated; PDF/HTML exported from the same source

---

## 4. Current Status — UPDATE THIS EVERY SESSION

```
Phase: 1 (Digital Forensics MVP)
Module in progress: File Analysis
Last completed task: TASK-002
Current task: TASK-003 (see TASKS.md)
Blockers: none
Last commit: b35e1b4
Branch: task/002-dev-tooling
```

**Session startup checklist (do this every time, in order):**
1. Read this file fully.
2. Read `TASKS.md`, find the first task marked `[ ] IN PROGRESS` or the first
   `[ ] TODO` if none are in progress.
3. Do ONLY that one task. Do not start additional tasks even if it seems
   efficient to batch them.
4. Create/switch to a feature branch named `task/<task-id>-<short-slug>`.
5. Implement, run any tests/formatting for that task.
6. Commit with message format: `[TASK-XXX] <short description>`.
7. Write a Learning Log entry for the completed task in `docs/LEARNING_LOG.md`
   per §7, before updating TASKS.md status.
8. Update the task's status in `TASKS.md` to `DONE`.
9. Update the "Current Status" block above (module, last completed task,
   next task, last commit hash, branch).
10. Stop. Do not proceed to the next task automatically — the human decides
    whether to merge, review, or continue.

---

## 4b. When to Ask Instead of Assuming

You (the AI builder) do all the implementation work — the human is not going
to hand-write scaffolding or code. But you must STOP and ask a direct
question, instead of guessing, whenever:

- A task description is ambiguous enough that two reasonable implementations
  would produce different behavior (not just different style).
- You need to choose between two libraries/approaches not already decided in
  this file (e.g. "requests vs httpx" — pick either; "SQLite vs JSON for
  session storage" — ask, that's an architecture choice).
- Completing the task would require breaking an Architecture Rule in §2.
- You discover the current task depends on something not yet built that
  isn't listed as a dependency in TASKS.md.
- A required external tool needs to be installed (per §2 rule 5) — always
  ask before installing anything, never assume yes.

Ask as a short, specific question with your recommended default, e.g.:
*"TASK-004 needs session storage. I recommend a single JSON file per session
under `.sessions/`. OK to proceed, or do you want SQLite instead?"*
Do not ask about things already answered in this file — read §2 and §3 first.

---

## 5. Git Workflow

- **TASK-001 only** is committed and pushed directly to `main` (pure
  scaffolding, nothing to review). Every task from TASK-002 onward follows
  the branch workflow below.
- `main` is always stable and human-reviewed.
- One feature branch per task, named `task/<id>-<slug>`.
- After committing, **push the branch and open a Pull Request** — do not
  merge to `main` yourself. The human merges after reviewing.
- Never force-push. Never rewrite history on `main`.
- **Never write the GitHub token, or any API key, into any file that could
  be committed** — not in code, not in a config file, not in a comment, not
  even temporarily. If a task needs a credential, read it from an
  environment variable that the human sets up outside the repo, and confirm
  `.gitignore` covers it first.

---

## 6. Coding Standards

- Type hints on all public functions.
- Docstrings on all public classes/functions explaining *why*, not just what.
- Tests live alongside each module in `tests/`, named `test_<module>.py`.
- No bare `except:` — catch specific exceptions.
- Keep functions small; one responsibility each (matches the "one task, one
  commit" philosophy of the whole project).

---

## 7. Learning Log Requirement

After completing EVERY task (starting from TASK-002 onward), you must append
an entry to `docs/LEARNING_LOG.md` before marking the task DONE. This file
is for the human to read later and actually learn from — write it in plain,
non-jargon language, as if explaining to someone who knows Python but is new
to CTF/forensics concepts.

Each entry must use this format:

---
### TASK-XXX — <task title>
**Date:** <date>
**What I built:** 2-4 plain-language sentences on what was added and why it
was needed.
**Key concepts:** Any forensics/security/Python concept introduced in this
task, explained in 1-2 sentences each — assume the reader doesn't know it yet.
**How it fits together:** 1-2 sentences on how this piece connects to the
engine/modules/workflow described in CONTEXT.md §2.
**Files touched:** bullet list of files created or changed.
---

Do not skip this even for small tasks. If a task is trivial, the entry can
be short, but it must still exist.
