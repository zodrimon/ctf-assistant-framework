from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.detector import Detector
from ctf_assistant.modules.base import Module


class MemoryModule:
    """
    Analyzes raw memory dumps (e.g. .raw, .vmem, .dmp).
    """

    def get_name(self) -> str:
        return "Memory Forensics"

    def analyze(self, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Identify if the file is a memory dump.
        Uses magic bytes, file command output, and user confirmation for ambiguous files.
        """
        path = Path(evidence_path)
        if not path.exists():
            return {"type": "error", "message": f"File not found: {evidence_path}"}
        
        detector = Detector()
        identification_results = detector.identify(evidence_path)
        magic = identification_results.get("magic_bytes", "").lower()
        file_cmd = identification_results.get("file_command", "").lower()

        is_memory = False
        confidence = "none"

        # High confidence signatures
        # "PAGEDU64" (50 41 47 45 44 55 36 34)
        # "MDMP" (4d 44 4d 50)
        if magic.startswith("5041474544553634") or magic.startswith("4d444d50"):
            is_memory = True
            confidence = "high"
        elif "crash dump" in file_cmd or "minidump" in file_cmd or "pagedump" in file_cmd:
            is_memory = True
            confidence = "high"
        
        if not is_memory:
            # Check extension as a weak signal. Memory dumps often lack magic bytes.
            ext = path.suffix.lower()
            if ext in [".raw", ".vmem", ".dmp", ".mem", ".img", ".bin"]:
                print(f"\n[?] File '{path.name}' has extension '{ext}' but no definitive memory dump signature.")
                try:
                    ans = input("Treat this file as a Memory Dump? [y/N]: ")
                    if ans.lower().strip() == 'y':
                        is_memory = True
                        confidence = "manual"
                except OSError:
                    # In case stdin is not available (e.g., in some test environments)
                    pass
            
        return {
            "type": "memory_identification",
            "target": str(evidence_path),
            "is_memory": is_memory,
            "confidence": confidence,
            "identification": identification_results
        }

# Verify at type-check time that MemoryModule conforms to the Module protocol
_verify_protocol: Module = MemoryModule()
