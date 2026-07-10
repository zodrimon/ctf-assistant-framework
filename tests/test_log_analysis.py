import subprocess
from pathlib import Path

from ctf_assistant.modules.forensics.log_analysis.module import LogAnalysisModule
from ctf_assistant.engine.workflow import WorkflowRunner
from ctf_assistant.engine.session import Session


def test_log_module_apache_detection(tmp_path: Path):
    module = LogAnalysisModule()
    
    # Create a mock apache log with misleading extension
    apache_file = tmp_path / "access.bin"
    log_content = '192.168.1.10 - - [10/Oct/2000:13:55:36 -0700] "GET /admin HTTP/1.0" 200 2326\n'
    apache_file.write_text(log_content, encoding="utf-8")
    
    result = module.analyze(str(apache_file))
    
    assert result["is_log"] is True
    assert result["confidence"] == "high"
    assert result["log_type"] == "web_access"


def test_log_module_syslog_detection(tmp_path: Path):
    module = LogAnalysisModule()
    
    # Create a mock syslog file with misleading extension
    syslog_file = tmp_path / "auth.bin"
    log_content = "Jan 14 10:20:30 host sshd[123]: Failed password for root from 192.168.1.5 port 22 ssh2\n"
    syslog_file.write_text(log_content, encoding="utf-8")
    
    result = module.analyze(str(syslog_file))
    
    assert result["is_log"] is True
    assert result["confidence"] == "high"
    assert result["log_type"] == "syslog"


def test_log_workflow_e2e(monkeypatch, tmp_path: Path):
    fixture_path = tmp_path / "auth.log"
    log_content = "Jan 14 10:20:30 host sshd[123]: Failed password for root from 192.168.1.5 port 22 ssh2\n"
    fixture_path.write_text(log_content, encoding="utf-8")
    
    # Mock shutil.which so tools appear to be installed
    monkeypatch.setattr("shutil.which", lambda tool: f"/mocked/bin/{tool}")
    
    # Mock subprocess.run for tool execution
    original_run = subprocess.run
    def mock_run(command, *args, **kwargs):
        if command[0] in ["grep", "python"]:
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
    workflow_path = Path("src/ctf_assistant/modules/forensics/log_analysis/workflow.yaml").resolve()
    
    runner.execute(workflow_path, context={"target": str(fixture_path)})

    # 3. Verify Session Findings
    findings = session.findings.get("Log Analysis Workflow", [])
    
    assert len(findings) == 3, f"Expected 3 tools to run, got {len(findings)}"
    
    command_strings = [f.get("command", "") for f in findings]
    assert any("grep" in cmd and "failed|invalid|error" in cmd for cmd in command_strings)
    assert any("grep" in cmd and "([0-9]{1,3}" in cmd for cmd in command_strings)
    assert any("python" in cmd and "timeline" in cmd for cmd in command_strings)
