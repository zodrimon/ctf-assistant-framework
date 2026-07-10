from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.detector import Detector
from ctf_assistant.modules.base import Module


class PcapModule:
    """
    Analyzes PCAP and PCAPNG network capture files.
    """

    def get_name(self) -> str:
        return "Network Forensics (PCAP)"

    def analyze(self, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Identify if the file is a PCAP or PCAPNG file.
        Returns a dictionary containing the findings.
        """
        path = Path(evidence_path)
        if not path.exists():
            return {"type": "error", "message": f"File not found: {evidence_path}"}
        
        # Rely on the centralized Detector
        detector = Detector()
        identification_results = detector.identify(evidence_path)
        magic = identification_results.get("magic_bytes", "").lower()
        file_cmd = identification_results.get("file_command", "").lower()

        is_pcap = False
        pcap_type = None

        # PCAP magic bytes (including nanosecond variations and different endianness)
        pcap_magics = ("a1b2c3d4", "d4c3b2a1", "a1b23c4d", "4d3cb2a1")
        
        if any(magic.startswith(m) for m in pcap_magics):
            is_pcap = True
            pcap_type = "pcap"
        elif magic.startswith("0a0d0d0a"):
            is_pcap = True
            pcap_type = "pcapng"
        elif "pcap capture" in file_cmd or "pcapng capture" in file_cmd:
            is_pcap = True
            pcap_type = "pcapng" if "pcapng" in file_cmd else "pcap"
            
        return {
            "type": "pcap_identification",
            "target": str(evidence_path),
            "is_pcap": is_pcap,
            "pcap_type": pcap_type,
            "identification": identification_results
        }

# Verify at type-check time that PcapModule conforms to the Module protocol
_verify_protocol: Module = PcapModule()
