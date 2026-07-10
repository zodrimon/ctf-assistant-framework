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

## Milestone 5 — Manual vs Auto Investigation Mode

> Do this before starting new modules — every module below will use this.

- [x] TASK-017 — DONE — Add `mode: "auto" | "manual"` to `Session`, and a
      `--mode` flag to the `investigate` CLI command (default: manual — safer
      default, user opts into auto). In `WorkflowRunner`, when mode is
      `manual`, prompt `Run <tool> <args>? Reason: <reason> [Y/n]` before each
      step; when `auto`, run steps sequentially without prompting but still
      log every command to the session. Reuse the existing tool-missing
      prompt logic from TASK-010 — don't duplicate it.
- [x] TASK-018 — DONE — Tests: one test asserting manual mode calls the
      confirmation prompt per step (mock the prompt to return yes/no and
      check behavior), one test asserting auto mode runs all steps without
      prompting.

---

## Milestone 6 — Archives Module

- [x] TASK-019 — DONE — modules/forensics/archives/module.py: detect zip,
      tar, gzip, rar, 7z via magic bytes (not extension). Follow the File
      Analysis module's structure exactly (CONTEXT.md 2 rule 6).
- [x] TASK-020 — DONE — archives/workflow.py: list contents, extract to a
      session-scoped temp dir, and recurse -- if an extracted file is
      itself an archive, re-run detection on it (zip-in-zip case from the
      original spec). Cap recursion depth (suggest 5) to avoid zip-bomb
      style infinite loops -- ask the human to confirm the cap before hardcoding.
- [x] TASK-021 — DONE — Tests using a small nested-archive fixture
      (zip containing a zip) checked into tests/fixtures/.

## Milestone 7 — Network Forensics (PCAP) Module

- [x] TASK-022 — DONE — modules/forensics/pcap/module.py: detect
      pcap/pcapng via magic bytes.
- [x] TASK-023 — DONE — pcap/workflow.yaml: baseline steps using tshark
      (protocol hierarchy summary, HTTP object export). Requires tshark —
      confirm tool-missing prompt (TASK-010 logic) triggers correctly if
      it's absent.
- [x] TASK-024 — DONE — Tests using a small sample .pcap fixture (a few
      packets is enough — keep the fixture file small).

## Milestone 8 — Memory Forensics Module

- [x] TASK-025 — DONE — modules/forensics/memory/module.py: detect raw
      memory dump signatures (best-effort — these are harder to fingerprint
      than other formats; ask the human if confidence is too low to proceed
      automatically, per CONTEXT.md 2 rule 3).
- [x] TASK-026 — DONE — memory/workflow.yaml or Python Workflow subclass
      (likely needs branching logic — profile detection before running
      plugins — so this may belong in Python per rule 2): baseline
      Volatility3 windows.pslist/windows.pstree. Requires volatility3.
- [x] TASK-027 — DONE — Tests: since real memory dumps are large, use a
      mocked Volatility3 output (recorded sample JSON) rather than a real
      fixture file — confirm this approach with the human before proceeding
      given section 4b (real memory dumps are impractical as committed fixtures).

## Milestone 9 — Steganography Module

- [x] TASK-028 — DONE — modules/forensics/steganography/module.py: detect
      image/audio files likely to be candidates (extend beyond magic bytes —
      consider a basic entropy check per rule 3, since stego payloads
      often raise entropy in specific regions).
- [x] TASK-029 — DONE — steganography/workflow.yaml: baseline steps —
      binwalk, exiftool, strings, and where applicable zsteg (PNG/BMP)
      or steghide (JPEG). Presented as alternative paths, not a forced
      sequence, per the original spec ("never assume only one solution
      exists") — ask the human how alternative-path selection should surface
      in manual mode before implementing (e.g. numbered menu).
- [x] TASK-030 — DONE — Tests using a small fixture image with a known
      trivial hidden string (e.g. appended after IEND in a PNG).

## Milestone 10 — Disk Images Module

- [x] TASK-031 — DONE — modules/forensics/disk/module.py: detect raw/dd
      and E01 disk image formats.
- [x] TASK-032 — DONE — disk/workflow.yaml: partition listing (mmls from
      Sleuth Kit) and file carving (foremost). Requires sleuthkit and
      foremost.
- [x] TASK-033 — DONE — Tests using a small synthetic disk image fixture
      (a few MB, built with a known partition table — document how it was
      generated in the test file's docstring so it's reproducible).

## Milestone 11 — Log Analysis Module

- [x] TASK-034 — DONE — modules/forensics/log_analysis/module.py: detect
      common log formats (syslog, Apache/nginx access logs, auth.log) by
      content pattern, not extension.
- [x] TASK-035 — DONE — log_analysis/workflow.yaml: baseline pattern
      extraction (failed logins, IPs, timestamps) via grep/ripgrep, plus
      a simple chronological timeline builder in Python.
- [x] TASK-036 — DONE — Tests using a small sample log fixture with a couple
      of planted "findings" (e.g. a few failed SSH login lines).

## Milestone 12 — Malware Triage + Basic Binary Inspection Module

- [x] TASK-037 — DONE — modules/forensics/malware_triage/module.py: detect
      PE (Windows) and ELF (Linux) executables via magic bytes.
- [x] TASK-038 — DONE — malware_triage/workflow.yaml: static-only
      triage — file hashes (md5/sha256), strings, yara scan against a
      small bundled ruleset, PE/ELF header inspection. Requires yara.
      Never execute the analyzed binary — this is a hard safety rule,
      not a style choice; if any future task suggests running the sample,
      stop and ask the human explicitly.
- [x] TASK-039 — DONE — Add a short note to docs/LEARNING_LOG.md (as part
      of this task's entry) explaining why static-only analysis is the
      default and what sandboxing would be needed before ever adding dynamic
      analysis — this is a teaching moment worth capturing explicitly.
- [x] TASK-040 — DONE — Tests using a small benign test binary (e.g. a
      trivial compiled "hello world," not any real-world sample).

---

## Milestone 13 — TUI (Textual)

> Adds a richer interface alongside the CLI — the CLI must keep working
> unchanged; this is additive, not a replacement.

- [x] TASK-041 — DONE — Textual app skeleton: `ctf-assistant tui` launches a
      main screen listing detected/available modules. No investigation logic
      yet — just navigation shell.
- [ ] TASK-042 — TODO — TUI investigation view: pick a file, run its matched
      module's workflow, stream step-by-step output live (reuse
      WorkflowRunner from the engine — do not duplicate execution logic in
      the TUI layer).
- [ ] TASK-043 — TODO — TUI session browser: list past sessions (from saved
      Session JSON files) and allow resuming/viewing one.
- [ ] TASK-044 — TODO — Since TUI interactions are harder to unit test
      automatically, add a manual QA checklist to docs/LEARNING_LOG.md
      (steps for the human to click through and verify) rather than skipping
      verification entirely.

## Milestone 14 — Report Export (PDF/HTML)

- [ ] TASK-045 — TODO — HTML report renderer: reuse the same Session data as
      the existing Markdown renderer (TASK-007) — do not build a second,
      separate data-gathering path.
- [ ] TASK-046 — TODO — PDF export from the HTML/Markdown source (e.g. via
      WeasyPrint or Pandoc — confirm which is available/lighter-weight before
      picking, per section 4b).
- [ ] TASK-047 — TODO — CLI command `ctf-assistant report export --format
      {md,html,pdf}`.
- [ ] TASK-048 — TODO — Tests verifying each export format produces a
      non-empty file with expected key sections present.

---

## Backlog (future phases — not yet broken into tasks, do not start)

- Phase 2 — Web Exploitation modules
- Phase 3 — Reverse Engineering modules
- Phase 4 — Cryptography modules
- Phase 5 — Misc (OSINT, Wireless, Cloud, Mobile, Hardware, ICS/SCADA, AI CTF)
- Challenge templates, workflow editor, community workflow sharing, plugin
  marketplace, knowledge graph, evidence relationship mapping (all listed
  under "Future Features" in the original spec — intentionally deferred)