import json
from pathlib import Path
from ctf_assistant.engine.session import Session


def test_session_creation():
    session = Session()
    assert session.session_id is not None
    assert session.state == {}
    assert session.findings == {}


def test_session_save_and_load(tmp_path: Path):
    session = Session(session_id="test-session")
    session.update_state("target", "192.168.1.1")
    session.add_finding("nmap", {"port": 80, "state": "open"})
    
    file_path = tmp_path / "session.json"
    session.save(file_path)
    
    assert file_path.exists()
    
    loaded_session = Session.load(file_path)
    assert loaded_session.session_id == "test-session"
    assert loaded_session.state["target"] == "192.168.1.1"
    assert loaded_session.findings["nmap"][0]["port"] == 80
