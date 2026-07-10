import sys
import re
from pathlib import Path

def build_timeline(file_path: str):
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        print(f"Error: Cannot read {file_path}")
        sys.exit(1)

    # Patterns to match timestamp at the start of a line
    # Apache: 127.0.0.1 - - [10/Oct/2000:13:55:36 -0700]
    apache_pattern = re.compile(r'\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} [+\-]\d{4})\]')
    # Syslog: Jan 14 10:20:30
    syslog_pattern = re.compile(r'^([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})')
    # ISO8601: 2023-10-14T10:20:30Z
    iso_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*?)\s+')

    events = []

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                timestamp = None
                
                # Check patterns
                syslog_match = syslog_pattern.match(line)
                if syslog_match:
                    timestamp = syslog_match.group(1)
                else:
                    iso_match = iso_pattern.match(line)
                    if iso_match:
                        timestamp = iso_match.group(1)
                    else:
                        apache_match = apache_pattern.search(line)
                        if apache_match:
                            timestamp = apache_match.group(1)
                
                if timestamp:
                    events.append((timestamp, line_no, line))
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if not events:
        print("No recognized timestamps found in log file.")
        sys.exit(0)

    # Log files are typically already chronological. We will extract and display
    # the structured events in the order they were found.
    print(f"--- Timeline for {path.name} ({len(events)} events) ---")
    
    # Show first 20 and last 20 if large, otherwise all
    if len(events) > 50:
        for ts, line_no, content in events[:25]:
            print(f"[{ts}] (Line {line_no}): {content}")
        print("\n... [ Truncated ] ...\n")
        for ts, line_no, content in events[-25:]:
            print(f"[{ts}] (Line {line_no}): {content}")
    else:
        for ts, line_no, content in events:
            print(f"[{ts}] (Line {line_no}): {content}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python timeline.py <log_file>")
        sys.exit(1)
        
    build_timeline(sys.argv[1])
