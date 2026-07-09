from pathlib import Path

from ctf_assistant.modules.forensics.file_analysis.module import FileAnalysisModule


def test_file_analysis_module_basic(tmp_path: Path):
    module = FileAnalysisModule()
    
    assert module.get_name() == "File Analysis"
    
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    
    result = module.analyze(test_file)
    
    assert result["type"] == "basic_file_identification"
    assert result["target"] == str(test_file)
    assert "identification" in result
    assert "magic_bytes" in result["identification"]
    assert "file_command" in result["identification"]


def test_file_analysis_e2e(monkeypatch):
    import subprocess
    from ctf_assistant.engine.session import Session
    from ctf_assistant.engine.workflow import WorkflowRunner

    fixture_path = Path("tests/fixtures/sample.bin").resolve()
    assert fixture_path.exists(), "Fixture file missing"
    
    # Mock shutil.which so the tools appear to be installed
    monkeypatch.setattr("shutil.which", lambda tool: f"/mocked/bin/{tool}")
    
    # Mock subprocess.run to simulate successful command execution
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        tool = command[0]
        if tool in ["file", "exiftool", "strings"]:
            class MockProcess:
                stdout = f"Mocked output for {tool}"
                stderr = ""
            return MockProcess()
        return original_run(command, *args, **kwargs)
        
    monkeypatch.setattr("subprocess.run", mock_run)

    # 1. Run Module Analysis
    module = FileAnalysisModule()
    analysis_result = module.analyze(fixture_path)
    
    # 2. Setup Session and WorkflowRunner
    session = Session()
    session.add_finding("File Analysis", analysis_result)
    
    runner = WorkflowRunner(session)
    workflow_path = Path("src/ctf_assistant/modules/forensics/file_analysis/workflow.yaml").resolve()
    runner.execute(workflow_path, context={"target": str(fixture_path)})
    
    # 3. Verify Module Results
    assert analysis_result["type"] == "basic_file_identification"
    assert "Mocked output for file" in analysis_result["identification"]["file_command"]

    # 4. Verify Workflow Results
    findings = session.findings.get("File Analysis Triage", [])
    assert len(findings) == 3, "Workflow should produce exactly 3 findings"
    
    tools_run = [f["command"].split()[0] for f in findings]
    assert tools_run == ["file", "exiftool", "strings"]
    
    for finding in findings:
        assert finding["status"] == "success"
        assert "Mocked output" in finding["output"]
