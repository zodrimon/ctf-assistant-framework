from pathlib import Path

from ctf_assistant.engine.report import ReportRenderer
from ctf_assistant.engine.session import Session


def test_report_export_html_and_pdf(tmp_path: Path):
    session = Session(session_id="test-export")
    session.update_state("target", "10.0.0.1")
    session.add_finding("Nmap", {"port": 22, "status": "open"})
    
    renderer = ReportRenderer()
    
    # Test HTML
    html_content = renderer.render_html(session)
    assert "<html" in html_content.lower()
    assert "test-export" in html_content
    assert "10.0.0.1" in html_content
    
    html_file = tmp_path / "report.html"
    html_file.write_text(html_content, encoding="utf-8")
    assert html_file.exists()
    
    # Test PDF
    pdf_file = tmp_path / "report.pdf"
    success = renderer.render_pdf(session, pdf_file)
    
    assert success is True
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0
    
    # Check magic bytes for PDF
    with open(pdf_file, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF"
