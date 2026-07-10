import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict

from ctf_assistant.engine.detector import Detector
from ctf_assistant.modules.base import Module


def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


class SteganographyModule:
    """
    Analyzes media files (images, audio) for potential steganography payloads.
    """

    def get_name(self) -> str:
        return "Steganography Analysis"

    def analyze(self, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        path = Path(evidence_path)
        if not path.exists():
            return {"type": "error", "message": f"File not found: {evidence_path}"}
        
        detector = Detector()
        identification_results = detector.identify(evidence_path)
        magic = identification_results.get("magic_bytes", "").lower()
        file_cmd = identification_results.get("file_command", "").lower()

        is_candidate = False
        media_type = "unknown"

        # Image signatures (PNG, JPEG, GIF, BMP)
        if magic.startswith("89504e47"):
            is_candidate = True
            media_type = "png"
        elif magic.startswith("ffd8ff"):
            is_candidate = True
            media_type = "jpeg"
        elif magic.startswith("47494638"):
            is_candidate = True
            media_type = "gif"
        elif magic.startswith("424d"):
            is_candidate = True
            media_type = "bmp"
        # Audio signatures (WAV)
        elif magic.startswith("52494646") and "WAVE" in file_cmd:
            is_candidate = True
            media_type = "wav"
        # Fallback to file command
        elif "image data" in file_cmd:
            is_candidate = True
            media_type = "image"
        elif "audio" in file_cmd:
            is_candidate = True
            media_type = "audio"

        entropy = 0.0
        if is_candidate:
            try:
                # Read file to calculate entropy.
                # CTF stego files are usually small enough to fit in memory.
                data = path.read_bytes()
                entropy = calculate_entropy(data)
            except Exception as e:
                pass

        return {
            "type": "steganography_identification",
            "target": str(evidence_path),
            "is_stego_candidate": is_candidate,
            "media_type": media_type,
            "entropy": entropy,
            "identification": identification_results
        }

# Verify at type-check time that SteganographyModule conforms to the Module protocol
_verify_protocol: Module = SteganographyModule()
