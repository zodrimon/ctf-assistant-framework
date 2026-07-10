from pathlib import Path

from ctf_assistant.engine.report import ReportRenderer
from ctf_assistant.engine.session import Session


def test_report_renderer_basic(tmp_path: Path):
    session = Session(session_id="test-123")
    session.update_state("target", "10.0.0.1")
    session.add_finding("Nmap", {"port": 22, "status": "open"})
    session.add_finding(
        "Strings",
        {"output": "password123\nadmin_token\n"}
    )
    
    renderer = ReportRenderer()
    report = renderer.render(session)
    
    # Assert expected pieces are in the Markdown string
    assert "test-123" in report
    assert "10.0.0.1" in report
    assert "### Nmap" in report
    assert "- **port:** 22" in report
    assert "```text\npassword123" in report
    
    # Test save
    out_file = tmp_path / "report.md"
    renderer.save(session, out_file)
    assert out_file.exists()
    assert "test-123" in out_file.read_text(encoding="utf-8")
