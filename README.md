# 🕵️‍♂️ CTF Assistant Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Framework: Textual](https://img.shields.io/badge/framework-textual-green.svg)](https://github.com/Textualize/textual)

> **An interactive, offline-first CTF investigation assistant.**

CTF Assistant Framework is a terminal-based reconnaissance and analysis engine designed for Capture The Flag (CTF) players, security students, and blue team learners. It automates repetitive forensic tasks, recommends next steps, and allows optional AI integration to help guide your investigation—all while keeping you in control.

## ✨ Features

- **Offline-First Analysis**: Perform your investigations without relying on an internet connection. The framework is designed to work completely offline.
- **Domain-Agnostic Engine**: A flexible architecture where new evidence types are added as modules/plugins.
- **Automated Forensics**: Multi-signal detection (magic bytes, MIME type, file output, entropy, known signatures) instead of relying solely on file extensions.
- **RAG-Powered Knowledge Base**: Automatically index and search through your personal notes using ChromaDB and local `sentence-transformers`.
- **Optional AI Integration**: Need a hint? You can optionally plug in an AI model (like Gemini) for advisory suggestions. The workflow engine will always function fully without AI.
- **Textual TUI**: A beautiful terminal user interface (TUI) built on Textual.
- **Automated Reporting**: Export your findings seamlessly into Markdown, PDF, or HTML formats.

## 🚀 Installation

### Prerequisites
- Linux Environment (Recommended)
- Python 3.11+
- System tools (used by modules for forensic analysis)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zodrimon/ctf-assistant-framework.git
   cd ctf-assistant-framework
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the framework:**
   ```bash
   pip install -e .
   ```

   *Optional: To install development dependencies (for contributing):*
   ```bash
   pip install -e .[dev]
   ```

## 💻 Usage

Once installed, the framework provides a convenient CLI/TUI to manage your CTF investigations.

To start the interactive terminal interface:

```bash
ctf-assistant
```

### Common Commands (CLI)

You can also use the framework directly from the command line for specific tasks:

- **Ingest files into RAG knowledge base:**
  ```bash
  ctf-assistant rag ingest /path/to/ctf/notes
  ```

- **Run a basic file analysis:**
  ```bash
  ctf-assistant analyze file /path/to/suspicious.bin
  ```

- **Generate a report:**
  ```bash
  ctf-assistant report export --format pdf my_investigation
  ```

*(Run `ctf-assistant --help` to see all available commands and options).*

## 🧩 Architecture

The CTF Assistant Framework follows strict architectural rules to ensure reliability and extensibility:
- **Hybrid Workflows**: Simple steps are defined in YAML (`workflows/*.yaml`); complex logic branching goes into Python `Workflow` subclasses.
- **Pluggable Modules**: All analysis capabilities (e.g., File Analysis) implement a standard `Module`/`Workflow` interface.
- **Tool Wrapping**: External system tools are executed via subprocesses. If a tool is missing, the framework will gracefully prompt you before taking action.
- **Privacy & Control**: AI is strictly optional and advisory.

## 🤝 Contributing

We welcome contributions! Please review the [CONTEXT.md](CONTEXT.md) and [TASKS.md](TASKS.md) files for our architecture rules, current project status, and task list.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
