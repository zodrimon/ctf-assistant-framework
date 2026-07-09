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

---
### TASK-005 — Build the file type Detector stub
**Date:** 2026-07-09
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

---
### TASK-005 — Build the file type Detector stub
**Date:** 2026-07-09
**What I built:** I created a `Detector` class that uses two basic techniques to identify what type a file is: reading its "magic bytes" (the very first few bytes of the file) and asking the Linux `file` command for its opinion. 
**Key concepts:** 
- **Magic Bytes (File Signatures):** Most file formats start with a specific sequence of bytes that act like a signature. For example, Windows executables start with "MZ". By reading these, we don't have to rely on the file extension (like `.exe`), which can easily be faked or removed by malware authors.
- **Subprocess Execution:** Sometimes the best way to do a task is to ask another program to do it. We use Python's `subprocess` to run the system's built-in `file` command behind the scenes and capture its text output.
**How it fits together:** Later tasks will use this `Detector` inside a dedicated File Analysis module. By creating it as a separate engine component now, we can eventually make it much smarter (combining multiple signals to give a confidence score) without changing the CTF modules that rely on it.
**Files touched:** 
- `src/ctf_assistant/engine/detector.py`
- `tests/test_detector.py`

---
### TASK-006 — Build the YAML Workflow Runner
**Date:** 2026-07-09
**What I built:** I created the `WorkflowRunner` class which reads investigation instructions from a YAML file. It executes a series of terminal commands defined in that file and saves the output of those commands directly into the active `Session`.
**Key concepts:** 
- **YAML Configuration:** YAML is a human-readable data format. We use it to define simple workflows (like "run this command, then run that command") without having to write complex Python code for every new procedure.
- **Dynamic Context variables:** The runner supports injecting variables into the commands (e.g., `{target}`) so a generic YAML file can be used to investigate specific, dynamically provided files or IP addresses.
**How it fits together:** This is the execution engine described in the architecture. Instead of hardcoding how to analyze a file, we can just write a YAML file that tells the `WorkflowRunner` to use tools like `strings`, `binwalk`, or our own `Detector` module, and all results are automatically funneled back into the central `Session` state.
**Files touched:** 
- `src/ctf_assistant/engine/workflow.py`
- `tests/test_workflow.py`
- `pyproject.toml`

---
### TASK-007 — Build the Markdown Report Renderer
**Date:** 2026-07-09
**What I built:** I created a `ReportRenderer` class that takes a `Session` (which holds all our investigation data) and automatically turns it into a neatly formatted Markdown report. It loops through all the findings and formats them with headers and code blocks.
**Key concepts:** 
- **Data Presentation:** While JSON (from our `Session` class) is great for computers to read and save, it's terrible for humans to read. The Report Renderer's job is purely translation—taking structured data and presenting it cleanly.
- **Markdown:** A lightweight markup language that allows us to format text (like adding bolding or code blocks) using plain text characters. It's universally supported by platforms like GitHub.
**How it fits together:** Once a workflow finishes running all its tools and gathering evidence into the `Session`, this renderer provides the final output that the investigator actually reads to figure out what happened.
**Files touched:** 
- `src/ctf_assistant/engine/report.py`
- `tests/test_report.py`

---
### TASK-008 — Build the first real Module: File Analysis
**Date:** 2026-07-09
**What I built:** I created our very first CTF Module called `FileAnalysisModule`. It follows the exact blueprint (the `Module` interface) we created in TASK-003 and uses the `Detector` from TASK-005 to identify file types.
**Key concepts:** 
- **Modularity in Practice:** This is where the architecture comes together. The `FileAnalysisModule` is completely isolated from the engine. It doesn't know how workflows are run or how reports are generated; it only knows how to take a file and return basic analysis results as a dictionary.
- **Reference Implementation:** This module serves as the "gold standard" example. If someone wants to add a "Memory Dump Analysis" module later, they can just copy how this `FileAnalysisModule` is structured.
**How it fits together:** We are entering Milestone 2! We now have the engine running, and we are starting to plug in the actual forensic capabilities. This module is the bridge between the raw investigation files and our execution engine.
**Files touched:** 
- `src/ctf_assistant/modules/forensics/file_analysis/module.py`
- `src/ctf_assistant/modules/forensics/file_analysis/__init__.py`
- `src/ctf_assistant/modules/forensics/__init__.py`
- `tests/test_file_analysis.py`

---
### TASK-009 — Build the Baseline Triage Workflow
**Date:** 2026-07-09
**What I built:** I created a simple YAML file (`workflow.yaml`) inside the `file_analysis` module that tells the `WorkflowRunner` exactly which commands to execute to triage a file: `file`, `exiftool`, and `strings`.
**Key concepts:** 
- **Triage:** In forensics, triage means taking a quick, initial look at evidence to figure out what it is and whether it's important, before spending hours doing deep analysis. The commands in this workflow perform that rapid initial check.
- **Strings Analysis:** Running the `strings` command on a file extracts any human-readable text hidden inside compiled code. We set a minimum length of 15 characters to filter out random garbage bytes that just happen to look like letters, keeping only the most likely useful text (like passwords or URLs).
**How it fits together:** When the CLI is run, it will load this YAML file and hand it to the `WorkflowRunner`. The runner will then execute these system commands against whatever file the user wants to investigate, saving the output to our `Session`.
**Files touched:** 
- `src/ctf_assistant/modules/forensics/file_analysis/workflow.yaml`

---
### TASK-010 — Wire Tool-Missing Detection into WorkflowRunner
**Date:** 2026-07-09
**What I built:** I added logic to the `WorkflowRunner` that checks if a required terminal tool (like `exiftool` or `strings`) is actually installed before trying to run it. If it's missing, it automatically pauses and asks the user if they want to install it via `apt-get`.
**Key concepts:** 
- **Dependency Management:** Scripts often fail unexpectedly when they assume a tool is installed. By explicitly checking for the tool using `shutil.which` and handling the missing case interactively, we make the framework much more robust and user-friendly.
**How it fits together:** This enforces Rule 5 from our architecture: we use standard Linux tools under the hood, but if the investigator's machine doesn't have them installed, the `WorkflowRunner` catches the problem and attempts to fix it automatically, rather than crashing or returning silent errors.
**Files touched:** 
- `src/ctf_assistant/engine/workflow.py`
- `tests/test_workflow.py`

---
### TASK-011 — Build End-to-End Tests for File Analysis
**Date:** 2026-07-09
**What I built:** I created an end-to-end (E2E) test for the File Analysis module. It creates a small dummy binary file, runs it through the `FileAnalysisModule` and the `WorkflowRunner`, and verifies that all expected forensic commands are executed successfully.
**Key concepts:** 
- **End-to-End Testing (E2E):** While unit tests check if one specific function works in isolation, E2E tests check if the entire system works when all the pieces are plugged together. This test simulates a full investigation on a single file from start to finish.
- **Mocking External Dependencies:** Because we can't guarantee that tools like `exiftool` are installed on the computer running the tests, I used a technique called "mocking". The test intercepts calls to the terminal and fakes the output, allowing us to test our Python logic without actually needing the forensics tools installed.
**How it fits together:** This test proves that the engine (Session + WorkflowRunner) and the module (FileAnalysisModule + workflow.yaml) can communicate seamlessly to perform a complete triage operation.
**Files touched:** 
- `tests/test_file_analysis.py`
- `tests/fixtures/sample.bin`

---
### TASK-012 — Build the CLI Entrypoint
**Date:** 2026-07-09
**What I built:** I created `src/ctf_assistant/cli.py` which provides the main command-line interface for the application. It adds the `ctf-assistant investigate <file>` command. This script takes the file, feeds it to the `FileAnalysisModule` (which uses the `Detector`), passes the results into a `Session`, runs the `WorkflowRunner`, and finally prints a Markdown report to the screen using our `ReportRenderer`.
**Key concepts:** 
- **CLI (Command Line Interface):** A text-based way to interact with a program, instead of clicking buttons in a GUI. `argparse` is the built-in Python library we used to parse the words the user types into the terminal.
- **Entrypoint:** The main script that starts the whole application. Before this, we had lots of disconnected parts (the engine, the module, the session, the renderer). This file is the "glue" that binds them all into a single, usable tool.
**How it fits together:** This officially completes Milestone 2! We now have a fully functional (albeit basic) forensics tool that an investigator can run directly from their terminal to automatically triage evidence files.
**Files touched:** 
- `src/ctf_assistant/cli.py`

---
### TASK-013 — Build the RAG Knowledge Store
**Date:** 2026-07-09
**What I built:** I created `src/ctf_assistant/rag/store.py` to manage our offline document database. It uses `chromadb` as the storage engine and automatically converts text into mathematical coordinates (embeddings) using the `onnxruntime` engine so we can search by meaning instead of exact keywords.
**Key concepts:** 
- **Embeddings:** A way to translate human text into a massive list of numbers (coordinates). Sentences with similar meanings get coordinates that are close together, allowing the AI to search for concepts rather than exact words.
- **Vector Database (ChromaDB):** A special type of database designed specifically to store these long lists of coordinates and search through them incredibly fast.
**How it fits together:** This is the beginning of Phase 3 (RAG). By setting up this database, we now have a place to dump CTF writeups, manuals, and hints. In the future, when the CLI runs a triage, it will be able to search this offline database to provide relevant hints based on the evidence it found.
**Files touched:** 
- `pyproject.toml`
- `src/ctf_assistant/rag/__init__.py`
- `src/ctf_assistant/rag/store.py`
- `tests/test_rag_store.py`

---
### TASK-014 — Build the RAG Ingest CLI Command
**Date:** 2026-07-09
**What I built:** I added an `ingest` command to our CLI tool that allows you to easily add Markdown, TXT, or PDF files into the local ChromaDB database. It automatically extracts the text and splits it into small, overlapping chunks before saving.
**Key concepts:** 
- **Chunking:** Because embedding models (the AI that turns text into coordinates) have a strict limit on how much text they can process at once (usually around 200-300 words), we must split large documents like PDFs into smaller "chunks" so that every paragraph gets indexed properly.
- **PDF Parsing:** We used a library called `pypdf` to read the binary data of a PDF file and extract the raw, human-readable text out of it.
**How it fits together:** This command is the bridge between your raw notes and the `KnowledgeStore` database we built in the last task. Now that we can actually put data into the database, the next task will be building the tool to pull it back out!
**Files touched:** 
- `src/ctf_assistant/rag/ingest.py`
- `src/ctf_assistant/cli.py`
- `pyproject.toml`
