from pathlib import Path
from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner


def test_workflow_runner_execution(tmp_path: Path):
    session = Session()
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
    session = Session()
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
