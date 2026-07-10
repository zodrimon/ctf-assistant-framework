from pathlib import Path
from ctf_assistant.engine.detector import Detector, MissingToolError


def test_detector_magic_bytes(tmp_path: Path):
    detector = Detector()
    test_file = tmp_path / "test.bin"
    # Write "MZ" (Windows PE executable magic bytes)
    test_file.write_bytes(b"MZ\x90\x00")
    
    magic = detector.get_magic_bytes(test_file, num_bytes=2)
    assert magic == "4d5a"  # Hex for "MZ"


def test_detector_identify_structure(tmp_path: Path):
    detector = Detector()
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello CTF")
    
    result = detector.identify(test_file)
    assert "magic_bytes" in result
    assert "file_command" in result
