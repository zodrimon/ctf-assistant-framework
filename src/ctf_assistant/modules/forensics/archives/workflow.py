import os
import tempfile
import yaml
from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.workflow import WorkflowRunner
from ctf_assistant.modules.base import Workflow
from ctf_assistant.modules.forensics.archives.module import ArchivesModule


class ArchivesWorkflow:
    """
    Workflow that recursively extracts archives (zip-in-zip, etc.).
    Uses the ArchivesModule to detect formats and dynamically creates
    YAML steps to leverage the engine's safe WorkflowRunner.
    """

    def get_name(self) -> str:
        return "Archives Recursive Extraction Workflow"

    def run(self, session: Any, evidence_path: str, max_depth: int = 5, **kwargs: Any) -> Dict[str, Any]:
        extracted_files = []
        runner = WorkflowRunner(session)
        module = ArchivesModule()

        def _extract_recursive(current_path: str, current_depth: int, out_dir: str):
            if current_depth > max_depth:
                session.add_finding(self.get_name(), {
                    "step": "Recursion Check",
                    "status": "warning",
                    "message": f"Max recursion depth ({max_depth}) reached for {current_path}"
                })
                return

            analysis = module.analyze(current_path)
            if not analysis.get("is_archive"):
                return

            archive_type = analysis["archive_type"]
            
            # Map archive types to extraction commands
            commands = {
                "zip": ["unzip", "-o", "-q", "{src}", "-d", "{dst}"],
                "tar": ["tar", "-xf", "{src}", "-C", "{dst}"],
                # Use python to extract gzip safely without shell redirection
                "gzip": [
                    "python", "-c", 
                    "import gzip, sys, os; "
                    "src=sys.argv[1]; "
                    "dst=os.path.join(sys.argv[2], os.path.basename(src)+'_extracted'); "
                    "open(dst, 'wb').write(gzip.decompress(open(src, 'rb').read()))", 
                    "{src}", "{dst}"
                ],
                "rar": ["unrar", "x", "-y", "{src}", "{dst}/"],
                "7z": ["7z", "x", "-y", "{src}", "-o{dst}"]
            }

            if archive_type not in commands:
                return

            cmd_template = commands[archive_type]
            
            # Create a dedicated temp dir for this extraction
            file_name = Path(current_path).name
            extract_dir = Path(out_dir) / f"extracted_depth_{current_depth}_{file_name}"
            extract_dir.mkdir(parents=True, exist_ok=True)

            step_name = f"Extract {archive_type} (depth {current_depth})"
            
            # Create dynamic yaml to reuse WorkflowRunner's safety/logging checks
            yaml_content = {
                "name": self.get_name(),
                "steps": [
                    {
                        "name": step_name,
                        "command": cmd_template
                    }
                ]
            }
            
            yaml_path = extract_dir / "temp_workflow.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(yaml_content, f)

            runner.execute(yaml_path, context={"src": str(current_path), "dst": str(extract_dir)})
            
            if yaml_path.exists():
                yaml_path.unlink()
            
            # Recursively check extracted files
            if extract_dir.exists():
                for root, _, files in os.walk(extract_dir):
                    for file in files:
                        filepath = Path(root) / file
                        extracted_files.append(str(filepath))
                        _extract_recursive(str(filepath), current_depth + 1, out_dir)

        # Create session scoped temp dir if not provided
        session_tmp = kwargs.get("temp_dir", tempfile.mkdtemp(prefix="ctf_archives_"))
        
        _extract_recursive(str(evidence_path), 1, session_tmp)

        return {
            "type": "archive_extraction",
            "extracted_files": extracted_files,
            "temp_dir": session_tmp
        }

# Verify protocol conformity
_verify_protocol: Workflow = ArchivesWorkflow()
