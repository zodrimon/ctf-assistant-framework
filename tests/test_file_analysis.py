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
