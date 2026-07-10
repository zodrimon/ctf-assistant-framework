import subprocess
from pathlib import Path

from ctf_assistant.modules.forensics.steganography.module import SteganographyModule
from ctf_assistant.modules.forensics.steganography.workflow import SteganographyWorkflow
from ctf_assistant.engine.session import Session


def test_stego_module_png_detection(tmp_path: Path, monkeypatch):
    module = SteganographyModule()
    
    # Create a mock PNG file with appended string
    png_file = tmp_path / "secret.png"
    # PNG Magic: 89 50 4E 47 0D 0A 1A 0A
    png_magic = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
    png_file.write_bytes(png_magic + b"IEND\xae\x42\x60\x82" + b"super_secret_flag{hidden}")
    
    # Mock subprocess.run to prevent 'file' command from breaking on Windows
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] == "file":
            class MockProcess:
                stdout = "image data"
                stderr = ""
                returncode = 0
            return MockProcess()
        return original_run(command, *args, **kwargs)
    monkeypatch.setattr("subprocess.run", mock_run)
    
    result = module.analyze(str(png_file))
    
    assert result["is_stego_candidate"] is True
    assert result["media_type"] == "png"
    assert result["entropy"] > 0.0


def test_stego_workflow_e2e(monkeypatch, tmp_path: Path):
    fixture_path = tmp_path / "secret.png"
    fixture_path.write_bytes(b"\x89\x50\x4E\x47")
    
    # Mock shutil.which so tools appear to be installed
    monkeypatch.setattr("shutil.which", lambda tool: f"/mocked/bin/{tool}")
    
    # Mock subprocess.run for tool execution
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] in ["strings", "exiftool", "binwalk", "zsteg", "file"]:
            class MockProcess:
                stdout = f"Mocked output for {' '.join(command)}"
                stderr = ""
                returncode = 0
            return MockProcess()
        return original_run(command, *args, **kwargs)
        
    monkeypatch.setattr("subprocess.run", mock_run)

    # 1. Setup Session in Auto mode
    session = Session(mode="auto")
    session.add_finding("Steganography Analysis", {
        "is_stego_candidate": True,
        "media_type": "png"
    })
    
    # 2. Run Workflow
    workflow = SteganographyWorkflow()
    workflow.run(session, str(fixture_path))

    # 3. Verify Session Findings
    findings = session.findings.get(workflow.get_name(), [])
    
    # In auto mode, it should run all applicable tools for PNG:
    # strings, exiftool, binwalk, zsteg
    assert len(findings) == 4, f"Expected 4 tools to run, got {len(findings)}"
    
    assert any("zsteg" in f["command"] for f in findings)
    assert not any("steghide" in f["command"] for f in findings), "steghide should not run on PNGs"
