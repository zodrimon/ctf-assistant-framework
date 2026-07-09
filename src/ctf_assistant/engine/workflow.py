import subprocess
from pathlib import Path
from typing import Any, Dict

import yaml

from ctf_assistant.engine.session import Session


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

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self.session.add_finding(
                    workflow_name,
                    {
                        "step": step_name,
                        "status": "success",
                        "command": " ".join(command),
                        "output": result.stdout.strip()
                    }
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
