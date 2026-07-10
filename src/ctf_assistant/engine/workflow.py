import subprocess
from pathlib import Path
from typing import Any, Dict

import yaml

from ctf_assistant.engine.session import Session
from ctf_assistant.rag.retriever import retrieve_notes


class WorkflowRunner:
    """
    Loads and executes deterministic YAML workflows.

    Workflows consist of a series of steps that execute system commands,
    storing their output into the active Session.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def load_workflow(self, yaml_path: str | Path) -> Dict[str, Any]:
        """Load and parse a YAML workflow file."""
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)
            
        if not isinstance(workflow, dict) or "steps" not in workflow:
            raise ValueError("Invalid workflow format: missing 'steps' key.")
            
        return workflow

    def execute(self, yaml_path: str | Path, context: Dict[str, str]) -> None:
        """
        Execute the steps defined in the workflow file.

        Args:
            yaml_path: Path to the YAML workflow file.
            context: A dictionary of variables to format into the commands
                     (e.g., {"target": "/path/to/evidence.bin"}).
        """
        workflow = self.load_workflow(yaml_path)
        workflow_name = workflow.get("name", "Unknown Workflow")

        for step in workflow.get("steps", []):
            step_name = step.get("name", "Unnamed Step")
            raw_command = step.get("command", [])
            
            # Format command arguments with the provided context
            try:
                command = [arg.format(**context) for arg in raw_command]
            except KeyError as e:
                self.session.add_finding(
                    workflow_name,
                    {
                        "step": step_name,
                        "status": "error",
                        "error": f"Missing context variable: {e}"
                    }
                )
                continue

            # Mode prompt
            command_str = " ".join(command)
            if getattr(self.session, "mode", "manual") == "manual":
                ans = input(f"Run {command_str}? Reason: {step_name} [Y/n]: ")
                if ans.lower().strip() == 'n':
                    self.session.add_finding(
                        workflow_name,
                        {
                            "step": step_name,
                            "status": "skipped",
                            "command": command_str,
                            "reason": "User skipped step in manual mode"
                        }
                    )
                    continue

            # Tool missing detection per Rule 5
            tool_name = command[0]
            import shutil
            if not shutil.which(tool_name):
                print(f"\n[!] Required tool '{tool_name}' is not installed.")
                ans = input(f"Attempt to install '{tool_name}' using apt-get? (Requires sudo) [y/N]: ")
                if ans.lower().strip() == 'y':
                    try:
                        print(f"[*] Installing {tool_name}...")
                        subprocess.run(["sudo", "apt-get", "install", "-y", tool_name], check=True)
                        if not shutil.which(tool_name):
                            raise FileNotFoundError
                    except Exception as e:
                        self.session.add_finding(
                            workflow_name,
                            {
                                "step": step_name,
                                "status": "error",
                                "command": " ".join(command),
                                "error": f"Failed to install tool '{tool_name}': {e}"
                            }
                        )
                        continue
                else:
                    self.session.add_finding(
                        workflow_name,
                        {
                            "step": step_name,
                            "status": "error",
                            "command": " ".join(command),
                            "error": f"Command not found and user declined installation: {tool_name}"
                        }
                    )
                    continue

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                output = result.stdout.strip()
                finding_data = {
                    "step": step_name,
                    "status": "success",
                    "command": " ".join(command),
                    "output": output
                }
                
                if output:
                    # Query RAG store with the first 1000 characters to avoid huge queries
                    query_text = output[:1000]
                    notes = retrieve_notes(query_text, n_results=1)
                    if notes:
                        finding_data["relevant_notes"] = notes
                
                self.session.add_finding(
                    workflow_name,
                    finding_data
                )
            except subprocess.CalledProcessError as e:
                self.session.add_finding(
                    workflow_name,
                    {
                        "step": step_name,
                        "status": "error",
                        "command": " ".join(command),
                        "error": e.stderr.strip() or str(e)
                    }
                )
            except FileNotFoundError as e:
                 self.session.add_finding(
                    workflow_name,
                    {
                        "step": step_name,
                        "status": "error",
                        "command": " ".join(command),
                        "error": f"Command not found: {command[0]}"
                    }
                )
