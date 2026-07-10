import subprocess
from pathlib import Path

from ctf_assistant.modules.forensics.pcap.module import PcapModule
from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner


def test_pcap_module_basic(tmp_path: Path):
    module = PcapModule()
    
    assert module.get_name() == "Network Forensics (PCAP)"
    
    # Test valid pcap magic bytes
    pcap_file = tmp_path / "valid.pcap"
    pcap_file.write_bytes(b"\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00")
    
    result = module.analyze(pcap_file)
    assert result["type"] == "pcap_identification"
    assert result["is_pcap"] is True
    assert result["pcap_type"] == "pcap"


def test_pcap_module_pcapng(tmp_path: Path):
    module = PcapModule()
    pcapng_file = tmp_path / "valid.pcapng"
    pcapng_file.write_bytes(b"\x0a\x0d\x0d\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    
    result = module.analyze(pcapng_file)
    assert result["is_pcap"] is True
    assert result["pcap_type"] == "pcapng"


def test_pcap_workflow_e2e(monkeypatch):
    fixture_path = Path("tests/fixtures/sample.pcap").resolve()
    assert fixture_path.exists(), "PCAP fixture missing"

    # Mock shutil.which so 'tshark' appears to be installed
    monkeypatch.setattr("shutil.which", lambda tool: f"/mocked/bin/{tool}")
    
    # Mock subprocess.run for tshark execution
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] in ["tshark", "file"]:
            class MockProcess:
                stdout = f"Mocked output for {' '.join(command)}"
                stderr = ""
            return MockProcess()
        # Let python -c commands run so directories can be created
        return original_run(command, *args, **kwargs)
        
    monkeypatch.setattr("subprocess.run", mock_run)

    # 1. Run Module
    module = PcapModule()
    analysis_result = module.analyze(fixture_path)
    assert analysis_result["is_pcap"] is True

    # 2. Setup Session and WorkflowRunner
    session = Session(mode="auto")
    session.add_finding("PCAP Analysis", analysis_result)
    
    runner = WorkflowRunner(session)
    workflow_path = Path("src/ctf_assistant/modules/forensics/pcap/workflow.yaml").resolve()
    runner.execute(workflow_path, context={"target": str(fixture_path)})

    # 3. Verify Session Findings
    findings = session.findings.get("PCAP Analysis Workflow", [])
    assert len(findings) == 3, "Workflow should execute 3 steps"
    
    # Verify the commands executed
    assert findings[0]["command"].startswith("tshark")
    assert "phs" in findings[0]["command"]
    
    assert findings[1]["command"].startswith("python")
    
    assert findings[2]["command"].startswith("tshark")
    assert "--export-objects" in findings[2]["command"]

    # Verify the export directory was actually created by the python command
    export_dir = Path(f"{fixture_path}_http_objects")
    assert export_dir.exists(), "Export directory should have been created"
    
    # Cleanup export directory created by the python command
    export_dir.rmdir()
