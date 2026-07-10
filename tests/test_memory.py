import subprocess
from pathlib import Path

from ctf_assistant.modules.forensics.memory.module import MemoryModule
from ctf_assistant.modules.forensics.memory.workflow import MemoryWorkflow
from ctf_assistant.engine.session import Session


def test_memory_module_high_confidence(tmp_path: Path):
    module = MemoryModule()
    
    # Test valid memory magic bytes (MDMP)
    mem_file = tmp_path / "crash.dmp"
    mem_file.write_bytes(b"\x4d\x44\x4d\x50" + b"\x00" * 10)
    
    result = module.analyze(mem_file)
    assert result["is_memory"] is True
    assert result["confidence"] == "high"


def test_memory_module_interactive_fallback(tmp_path: Path, monkeypatch):
    module = MemoryModule()
    
    # Raw file with no magic bytes
    mem_file = tmp_path / "raw_dump.vmem"
    mem_file.write_bytes(b"\x00" * 20)
    
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
    
    result = module.analyze(mem_file)
    assert result["is_memory"] is True
    assert result["confidence"] == "manual"


def test_memory_workflow_e2e(monkeypatch, tmp_path: Path):
    fixture_path = tmp_path / "sample.vmem"
    fixture_path.write_bytes(b"\x00" * 20)

    # Mock shutil.which so 'vol' appears to be installed
    monkeypatch.setattr("shutil.which", lambda tool: f"/mocked/bin/{tool}")
    
    # Mock subprocess.run for vol execution
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] in ["vol", "file"]:
            class MockProcess:
                stdout = f"Mocked output for {' '.join(command)}"
                stderr = ""
                returncode = 0
            return MockProcess()
        return original_run(command, *args, **kwargs)
        
    monkeypatch.setattr("subprocess.run", mock_run)

    original_popen = subprocess.Popen
    def mock_popen(command, *args, **kwargs):
        if command[0] in ["vol", "file"]:
            class MockPopenProcess:
                def __init__(self):
                    self.stdout = [f"Mocked output for {' '.join(command)}\n"]
                    self.returncode = 0
                def wait(self): pass
            return MockPopenProcess()
        return original_popen(command, *args, **kwargs)
        
    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # 1. Setup Session
    session = Session(mode="auto")
    session.add_finding("Memory Forensics", {"is_memory": True})
    
    # 2. Run Workflow
    workflow = MemoryWorkflow()
    workflow.run(session, str(fixture_path))

    # 3. Verify Session Findings
    findings = session.findings.get(workflow.get_name(), [])
    
    # Should execute 3 steps: windows.info, windows.pslist, windows.pstree
    assert len(findings) == 3, "Workflow should execute 3 steps for Windows profile"
    
    assert findings[0]["command"].endswith("windows.info")
    assert findings[1]["command"].endswith("windows.pslist")
    assert findings[2]["command"].endswith("windows.pstree")
