from pathlib import Path
from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner


def test_workflow_runner_execution(tmp_path: Path):
    session = Session(mode="auto")
    runner = WorkflowRunner(session)
    
    # Create a dummy workflow file
    workflow_yaml = """
name: "Test Workflow"
steps:
  - name: "Echo Test"
    # use echo which works in most environments
    command: ["python", "-c", "print('hello {target}')"]
"""
    yaml_file = tmp_path / "test_workflow.yaml"
    yaml_file.write_text(workflow_yaml)
    
    # Execute
    runner.execute(yaml_file, context={"target": "world"})
    
    # Check results in session
    assert "Test Workflow" in session.findings
    findings = session.findings["Test Workflow"]
    
    assert len(findings) == 1
    assert findings[0]["step"] == "Echo Test"
    assert findings[0]["status"] == "success"
    assert findings[0]["output"] == "hello world"


def test_workflow_missing_context(tmp_path: Path):
    session = Session(mode="auto")
    runner = WorkflowRunner(session)
    
    workflow_yaml = """
name: "Error Workflow"
steps:
  - name: "Bad Step"
    command: ["echo", "{missing_var}"]
"""
    yaml_file = tmp_path / "error_workflow.yaml"
    yaml_file.write_text(workflow_yaml)
    
    runner.execute(yaml_file, context={})
    
    findings = session.findings["Error Workflow"]
    assert findings[0]["status"] == "error"
    assert "Missing context variable" in findings[0]["error"]


def test_workflow_missing_tool_declined(tmp_path: Path, monkeypatch):
    session = Session(mode="auto")
    runner = WorkflowRunner(session)
    
    workflow_yaml = """
name: "Missing Tool Workflow"
steps:
  - name: "Fake Tool Step"
    command: ["this_tool_does_not_exist_123", "arg"]
"""
    yaml_file = tmp_path / "missing_tool.yaml"
    yaml_file.write_text(workflow_yaml)
    
    # Mock input to return 'N' (decline installation)
    monkeypatch.setattr('builtins.input', lambda _: 'N')
    
    runner.execute(yaml_file, context={})
    
    findings = session.findings["Missing Tool Workflow"]
    assert findings[0]["status"] == "error"
    assert "user declined installation" in findings[0]["error"]


def test_workflow_manual_mode_prompt(tmp_path: Path, monkeypatch):
    session = Session(mode="manual")
    runner = WorkflowRunner(session)
    
    workflow_yaml = """
name: "Manual Mode Workflow"
steps:
  - name: "Step 1"
    command: ["python", "-c", "print('hello')"]
  - name: "Step 2"
    command: ["python", "-c", "print('world')"]
"""
    yaml_file = tmp_path / "manual_workflow.yaml"
    yaml_file.write_text(workflow_yaml)
    
    # Provide 'n' for first step, 'y' for second step
    inputs = iter(['n', 'y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    runner.execute(yaml_file, context={})
    
    findings = session.findings["Manual Mode Workflow"]
    assert len(findings) == 2
    
    assert findings[0]["step"] == "Step 1"
    assert findings[0]["status"] == "skipped"
    
    assert findings[1]["step"] == "Step 2"
    assert findings[1]["status"] == "success"
    assert findings[1]["output"] == "world"


def test_workflow_auto_mode_no_prompt(tmp_path: Path, monkeypatch):
    session = Session(mode="auto")
    runner = WorkflowRunner(session)
    
    workflow_yaml = """
name: "Auto Mode Workflow"
steps:
  - name: "Step 1"
    command: ["python", "-c", "print('auto hello')"]
"""
    yaml_file = tmp_path / "auto_workflow.yaml"
    yaml_file.write_text(workflow_yaml)
    
    # If auto mode incorrectly calls input(), this will fail the test
    def fail_input(_):
        raise RuntimeError("input() should not be called in auto mode")
    monkeypatch.setattr('builtins.input', fail_input)
    
    runner.execute(yaml_file, context={})
    
    findings = session.findings["Auto Mode Workflow"]
    assert len(findings) == 1
    assert findings[0]["step"] == "Step 1"
    assert findings[0]["status"] == "success"
    assert findings[0]["output"] == "auto hello"
