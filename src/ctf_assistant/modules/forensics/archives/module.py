from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.detector import Detector
from ctf_assistant.modules.base import Module


class ArchivesModule:
    """
    A module that performs detection and initial analysis on archive files.
    
    It detects zip, tar, gzip, rar, and 7z formats via magic bytes
    and standard file identification, conforming to the Module protocol.
    """
    
    def get_name(self) -> str:
        return "Archives Analysis"
        
    def analyze(self, evidence_path: str | Path, **kwargs: Any) -> Dict[str, Any]:
        """
        Analyze the given evidence file using the engine's Detector.
        """
        detector = Detector()
        identification_results = detector.identify(evidence_path)
        
        magic = identification_results.get("magic_bytes", "").lower()
        file_cmd = identification_results.get("file_command", "").lower()
        
        archive_type = None
        if magic.startswith("504b0304"):
            archive_type = "zip"
        elif magic.startswith("1f8b"):
            archive_type = "gzip"
        elif magic.startswith("377abaf81d11"):
            archive_type = "7z"
        elif magic.startswith("52617221"):
            archive_type = "rar"
        elif "tar archive" in file_cmd:
            archive_type = "tar"
        
        return {
            "type": "archive_identification",
            "target": str(evidence_path),
            "is_archive": archive_type is not None,
            "archive_type": archive_type,
            "identification": identification_results
        }

# Verify at type-check time that ArchivesModule conforms to the Module protocol
_verify_protocol: Module = ArchivesModule()
