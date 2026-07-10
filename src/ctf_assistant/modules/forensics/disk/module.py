from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.detector import Detector
from ctf_assistant.modules.base import Module


class DiskModule:
    """
    Analyzes files to determine if they are disk images (Raw/DD, E01, ISO, etc.).
    Uses interactive fallback for raw images with no magic bytes.
    """

    def get_name(self) -> str:
        return "Disk Forensics"

    def analyze(self, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        path = Path(evidence_path)
        if not path.exists():
            return {"type": "error", "message": f"File not found: {evidence_path}"}

        detector = Detector()
        identification = detector.identify(evidence_path)
        magic = identification.get("magic_bytes", "").lower()
        file_cmd = identification.get("file_command", "").lower()

        is_disk = False
        confidence = "low"
        disk_type = "unknown"

        # 1. E01 (Expert Witness Format)
        if magic.startswith("45564609"):
            is_disk = True
            confidence = "high"
            disk_type = "e01"
            
        # 2. ISO 9660 CD-ROM filesystem
        elif "iso 9660" in file_cmd:
            is_disk = True
            confidence = "high"
            disk_type = "iso"
            
        # 3. MBR / Boot sector (usually Raw/DD)
        elif "boot sector" in file_cmd or "dos/mbr" in file_cmd or "partition table" in file_cmd:
            is_disk = True
            confidence = "high"
            disk_type = "raw"
            
        # 4. Fallback for raw files with no clear filesystem headers
        elif path.suffix.lower() in [".dd", ".img", ".raw", ".bin"]:
            print(f"\n[?] File '{path.name}' has extension '{path.suffix}' but no definitive disk signature.")
            try:
                ans = input("Treat this file as a Disk Image? [y/N]: ").strip().lower()
                if ans in ["y", "yes"]:
                    is_disk = True
                    confidence = "manual"
                    disk_type = "raw"
            except OSError:
                pass # Running in non-interactive mode

        return {
            "type": "disk_identification",
            "target": str(evidence_path),
            "is_disk": is_disk,
            "confidence": confidence,
            "disk_type": disk_type,
            "identification": identification
        }

_verify_protocol: Module = DiskModule()
