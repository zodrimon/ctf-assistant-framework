# TASKS.md — Task Queue

> One task = one branch = one commit = one review. Do not combine tasks.
> Status values: `TODO`, `IN PROGRESS`, `DONE`, `BLOCKED`

## Milestone 0 — Project Skeleton

- [x] TASK-001 — DONE — Create a new **public** GitHub repository named
      `ctf-assistant-framework` (via the GitHub MCP connection). Then locally:
      scaffold `pyproject.toml`, `src/ctf_assistant/` package layout,
      `.gitignore` (must exclude `.env`, `.sessions/`, `__pycache__/`, and any
      credentials file), `LICENSE` (MIT), empty `tests/`. Commit and push
      directly to `main` for this one task only (there's nothing to review
      yet — it's just scaffolding). If repo creation or push fails, that's a
      setup/auth problem — ask the human, don't guess at fixes.
- [x] TASK-002 — DONE — Add dev tooling: pytest, ruff/black config, pre-commit
      hook config (formatting only, no logic yet).
- [x] TASK-003 — DONE — Define `Module` and `Workflow` protocol/interfaces in
      `modules/base.py` per CONTEXT.md §2 rule 6. No implementations yet —
      interfaces and docstrings only.

## Milestone 1 — Investigation Engine Core (skeleton, no real detection logic)

- [x] TASK-004 — DONE — `engine/session.py`: `Session` class that can be
      created, saved to and loaded from a JSON file on disk (this is the
      resumability mechanism for actual investigations, separate from
      CONTEXT.md which tracks *build* progress).
- [x] TASK-005 — DONE — `engine/detector.py`: stub `Detector` that only
      identifies file type via the `file` command + magic bytes (no full
      multi-signal confidence scoring yet — that's a later task).
- [x] TASK-006 — DONE — `engine/workflow.py`: `WorkflowRunner` that can load a
      YAML workflow file and execute its steps as subprocess calls, storing
      output into the `Session`.
- [x] TASK-007 — DONE — `engine/report.py`: minimal Markdown report renderer
      that takes a `Session` and outputs a `.md` file.

## Milestone 2 — First Real Module: File Analysis (reference implementation)

- [x] TASK-008 — DONE — `modules/forensics/file_analysis/module.py`:
      implement the `Module` interface using `Detector` from TASK-005.
- [x] TASK-009 — DONE — `modules/forensics/file_analysis/workflow.yaml`:
      baseline triage steps (`file`, `exiftool`, `strings` with sane limits).
- [x] TASK-010 — DONE — Wire tool-missing detection + user prompt
      (per CONTEXT.md §2 rule 5) into `WorkflowRunner`.
- [x] TASK-011 — DONE — Tests for the File Analysis module end-to-end
      (use a small fixture file checked into `tests/fixtures/`).
- [x] TASK-012 — DONE — CLI command `ctf-assistant investigate <file>` that
      runs Detector → matching Module → WorkflowRunner → prints findings.

## Milestone 3 — RAG (do not start until Milestone 2 is fully DONE)

- [x] TASK-013 — DONE — `rag/store.py`: ChromaDB wrapper, local embedding
      model, persistent collection on disk.
- [x] TASK-014 — DONE — `rag/ingest.py`: CLI command to add a Markdown/PDF/TXT
      file into the knowledge base.
- [x] TASK-015 — DONE — `rag/retriever.py`: query function used by workflows
      to pull relevant notes given a finding.

---

## Milestone 4 — AI & Analysis
- [x] TASK-016 — DONE — AI provider abstraction (`ai/provider.py`) + first provider (Gemini). Includes human-friendly CLI configuration guidance.

---

## Backlog (not yet broken into tasks — do not start)

- Manual vs Auto investigation mode
- Remaining Phase 1 modules (Archives, PCAP, Memory, Steganography, Disk,
  Log Analysis, Malware Triage, Binary Inspection)
- TUI (Textual) beyond basic CLI
- PDF/HTML report export
