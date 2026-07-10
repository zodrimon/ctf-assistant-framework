import shutil
import subprocess
import zipfile
from pathlib import Path

from ctf_assistant.engine.session import Session
from ctf_assistant.modules.forensics.archives.workflow import ArchivesWorkflow


def test_archives_recursive_extraction(tmp_path, monkeypatch):
    session = Session(mode="auto")
    workflow = ArchivesWorkflow()
    
    fixture_path = Path("tests/fixtures/nested_archive.zip")
    
    # Mock shutil.which so WorkflowRunner thinks 'unzip' is installed
    original_which = shutil.which
    def mock_which(cmd, *args, **kwargs):
        if cmd == "unzip":
            return "/usr/bin/unzip"
        return original_which(cmd, *args, **kwargs)
    monkeypatch.setattr(shutil, "which", mock_which)
    
    # Mock subprocess.run to simulate unzip extracting files
    original_run = subprocess.run
    def mock_run(cmd, *args, **kwargs):
        if cmd[0] == "unzip":
            # cmd is ["unzip", "-o", "-q", "{src}", "-d", "{dst}"]
            src = cmd[3]
            dst = cmd[5]
            with zipfile.ZipFile(src, 'r') as z:
                z.extractall(dst)
            return subprocess.CompletedProcess(
                args=cmd, 
                returncode=0, 
                stdout="Simulated unzip output", 
                stderr=""
            )
        return original_run(cmd, *args, **kwargs)
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    result = workflow.run(session, str(fixture_path), temp_dir=str(tmp_path))
    
    assert "archive_extraction" == result["type"]
    
    # Verify it extracted the inner zip and then the secret text file
    extracted_names = [Path(p).name for p in result.get("extracted_files", [])]
    assert "inner.zip" in extracted_names
    assert "secret.txt" in extracted_names
