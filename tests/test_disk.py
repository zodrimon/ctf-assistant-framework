"""
Disk Module Tests

How to generate a reproducible synthetic disk image fixture manually:
$ dd if=/dev/zero of=sample.img bs=1M count=5
$ parted -s sample.img mklabel msdos
$ parted -s sample.img mkpart primary ext4 1MiB 100%
$ mkfs.ext4 -F -E offset=1048576 sample.img
"""
import subprocess
from pathlib import Path

from ctf_assistant.modules.forensics.disk.module import DiskModule
from ctf_assistant.engine.workflow import WorkflowRunner
from ctf_assistant.engine.session import Session


def test_disk_module_e01_detection(tmp_path: Path):
    module = DiskModule()
    
    # Create a mock E01 file
    e01_file = tmp_path / "image.E01"
    # E01 Magic: EVF\x09
    e01_magic = b"\x45\x56\x46\x09\x0D\x0A\xFF\x00"
    e01_file.write_bytes(e01_magic + b"fake_e01_data")
    
    result = module.analyze(str(e01_file))
    
    assert result["is_disk"] is True
    assert result["confidence"] == "high"
    assert result["disk_type"] == "e01"


def test_disk_module_interactive_fallback(tmp_path: Path, monkeypatch):
    module = DiskModule()
    
    # Raw file with no magic bytes but .dd extension
    raw_file = tmp_path / "image.dd"
    raw_file.write_bytes(b"\x00" * 20)
    
    # Mock input to return "y"
    monkeypatch.setattr("builtins.input", lambda prompt: "y")
    
    # Mock subprocess.run to prevent 'file' command from breaking on Windows
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] == "file":
            class MockProcess:
                stdout = "data"
                stderr = ""
                returncode = 0
            return MockProcess()
        return original_run(command, *args, **kwargs)
    monkeypatch.setattr("subprocess.run", mock_run)
    
    result = module.analyze(str(raw_file))
    assert result["is_disk"] is True
    assert result["confidence"] == "manual"
    assert result["disk_type"] == "raw"


def test_disk_workflow_e2e(monkeypatch, tmp_path: Path):
    fixture_path = tmp_path / "image.dd"
    fixture_path.write_bytes(b"\x00" * 20)
    
    # Mock shutil.which so tools appear to be installed
    monkeypatch.setattr("shutil.which", lambda tool: f"/mocked/bin/{tool}")
    
    # Mock subprocess.run for tool execution
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] in ["mmls", "foremost", "file"]:
            class MockProcess:
                stdout = f"Mocked output for {' '.join(command)}"
                stderr = ""
                returncode = 0
            return MockProcess()
        return original_run(command, *args, **kwargs)
        
    monkeypatch.setattr("subprocess.run", mock_run)

    # 1. Setup Session in Auto mode
    session = Session(mode="auto")
    
    # 2. Run Workflow via WorkflowRunner
    runner = WorkflowRunner(session)
    workflow_path = Path("src/ctf_assistant/modules/forensics/disk/workflow.yaml").resolve()
    
    runner.execute(workflow_path, context={"target": str(fixture_path)})

    # 3. Verify Session Findings
    findings = session.findings.get("Disk Forensics Workflow", [])
    
    assert len(findings) == 2, f"Expected 2 tools to run, got {len(findings)}"
    
    command_strings = [f["command"] for f in findings]
    assert any("mmls" in cmd for cmd in command_strings)
    assert any("foremost" in cmd for cmd in command_strings)
