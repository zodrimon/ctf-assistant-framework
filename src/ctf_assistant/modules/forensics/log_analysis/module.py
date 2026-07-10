import re
from pathlib import Path
from typing import Any, Dict

from ctf_assistant.modules.base import Module

class LogAnalysisModule:
    """
    Analyzes files to determine if they are log files (e.g. syslog, apache, auth.log)
    by inspecting their content patterns, rather than relying on file extensions.
    """

    def get_name(self) -> str:
        return "Log Analysis"

    def analyze(self, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        path = Path(evidence_path)
        if not path.exists():
            return {"type": "error", "message": f"File not found: {evidence_path}"}
            
        if not path.is_file():
            return {"type": "error", "message": f"Not a file: {evidence_path}"}

        # Regex patterns for common log types
        # Apache/Nginx: 127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET / HTTP/1.0" 200 2326
        apache_pattern = re.compile(
            r'^\d{1,3}(?:\.\d{1,3}){3}.*?\[\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} [+\-]\d{4}\] ".*?" \d{3}'
        )
        
        # Syslog/Auth: Jan 14 10:20:30 hostname process[123]: message
        # Or: 2023-10-14T10:20:30Z hostname ...
        syslog_pattern = re.compile(
            r'^([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*?)\s+\S+\s+'
        )
        
        is_log = False
        log_type = "unknown"
        confidence = "low"
        
        # Try reading the first few lines as text
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for _ in range(10):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line.strip())
                    
                # Check lines against patterns
                for line in lines:
                    if not line:
                        continue
                    if apache_pattern.match(line):
                        is_log = True
                        log_type = "web_access"
                        confidence = "high"
                        break
                    elif syslog_pattern.match(line):
                        is_log = True
                        log_type = "syslog"
                        confidence = "high"
                        break
                        
        except Exception:
            pass # Probably binary or unreadable

        # Fallback: if it has a .log extension but didn't match patterns
        if not is_log and path.suffix.lower() == ".log":
            # Just because it ends in .log doesn't mean it's a standard log format,
            # but we can flag it as a generic log.
            is_log = True
            log_type = "generic"
            confidence = "medium"

        return {
            "type": "log_identification",
            "target": str(evidence_path),
            "is_log": is_log,
            "confidence": confidence,
            "log_type": log_type
        }

_verify_protocol: Module = LogAnalysisModule()
