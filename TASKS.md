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
- [ ] TASK-002 — TODO — Add dev tooling: pytest, ruff/black config, pre-commit
      hook config (formatting only, no logic yet).
- [ ] TASK-003 — TODO — Define `Module` and `Workflow` protocol/interfaces in
      `modules/base.py` per CONTEXT.md §2 rule 6. No implementations yet —
      interfaces and docstrings only.

## Milestone 1 — Investigation Engine Core (skeleton, no real detection logic)

- [ ] TASK-004 — TODO — `engine/session.py`: `Session` class that can be
      created, saved to and loaded from a JSON file on disk (this is the
      resumability mechanism for actual investigations, separate from
      CONTEXT.md which tracks *build* progress).
- [ ] TASK-005 — TODO — `engine/detector.py`: stub `Detector` that only
      identifies file type via the `file` command + magic bytes (no full
      multi-signal confidence scoring yet — that's a later task).
- [ ] TASK-006 — TODO — `engine/workflow.py`: `WorkflowRunner` that can load a
      YAML workflow file and execute its steps as subprocess calls, storing
      output into the `Session`.
- [ ] TASK-007 — TODO — `engine/report.py`: minimal Markdown report renderer
      that takes a `Session` and outputs a `.md` file.

## Milestone 2 — First Real Module: File Analysis (reference implementation)

- [ ] TASK-008 — TODO — `modules/forensics/file_analysis/module.py`:
      implement the `Module` interface using `Detector` from TASK-005.
- [ ] TASK-009 — TODO — `modules/forensics/file_analysis/workflow.yaml`:
      baseline triage steps (`file`, `exiftool`, `strings` with sane limits).
- [ ] TASK-010 — TODO — Wire tool-missing detection + user prompt
      (per CONTEXT.md §2 rule 5) into `WorkflowRunner`.
- [ ] TASK-011 — TODO — Tests for the File Analysis module end-to-end
      (use a small fixture file checked into `tests/fixtures/`).
- [ ] TASK-012 — TODO — CLI command `ctf-assistant investigate <file>` that
      runs Detector → matching Module → WorkflowRunner → prints findings.

## Milestone 3 — RAG (do not start until Milestone 2 is fully DONE)

- [ ] TASK-013 — TODO — `rag/store.py`: ChromaDB wrapper, local embedding
      model, persistent collection on disk.
- [ ] TASK-014 — TODO — `rag/ingest.py`: CLI command to add a Markdown/PDF/TXT
      file into the knowledge base.
- [ ] TASK-015 — TODO — `rag/retriever.py`: query function used by workflows
      to pull relevant notes given a finding.

---

## Backlog (not yet broken into tasks — do not start)

- AI provider abstraction (`ai/provider.py`) + first provider (Gemini)
- Manual vs Auto investigation mode
- Remaining Phase 1 modules (Archives, PCAP, Memory, Steganography, Disk,
  Log Analysis, Malware Triage, Binary Inspection)
- TUI (Textual) beyond basic CLI
- PDF/HTML report export
