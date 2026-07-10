import os
import tempfile
import yaml
from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.workflow import WorkflowRunner


class MemoryWorkflow:
    """
    Workflow for analyzing memory dumps using Volatility 3.
    Demonstrates branching logic: runs 'windows.info' first to detect the profile.
    If successful, proceeds to run standard Windows plugins like pslist and pstree.
    """

    def get_name(self) -> str:
        return "Memory Forensics Workflow"

    def run(self, session: Any, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        # Helper to execute a single step via WorkflowRunner to leverage interactive checks
        def _run_step(name: str, command: list) -> bool:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
                yaml.dump({
                    "name": self.get_name(),
                    "steps": [{"name": name, "command": command}]
                }, f)
                temp_yaml = f.name
            try:
                runner = WorkflowRunner(session)
                runner.execute(Path(temp_yaml), context={"target": evidence_path})
                # Check if it succeeded by looking at the last finding for this workflow
                findings = session.findings.get(self.get_name(), [])
                if findings:
                    last_finding = findings[-1]
                    return last_finding.get("status") == "success"
                return False
            finally:
                os.remove(temp_yaml)

        # 1. Profile Detection (windows.info)
        print("\n[*] Detecting OS Profile (Windows)...")
        success = _run_step("Volatility: OS Info (Windows)", ["vol", "-f", "{target}", "windows.info"])
        
        if success:
            print("[*] Windows profile detected. Running standard Windows plugins...")
            # 2. pslist
            _run_step("Volatility: Process List (pslist)", ["vol", "-f", "{target}", "windows.pslist"])
            # 3. pstree
            _run_step("Volatility: Process Tree (pstree)", ["vol", "-f", "{target}", "windows.pstree"])
        else:
            print("[!] Failed to detect Windows profile. Other profiles (Linux/Mac) not yet implemented in baseline.")
            session.add_finding(self.get_name(), {
                "step": "Profile Detection",
                "status": "error",
                "message": "Failed to identify Windows memory profile. File may not be a memory dump or requires a Linux/Mac profile."
            })
            
        return {"status": "completed"}
