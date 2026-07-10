import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class Session:
    """
    Represents an active investigation session.

    The session stores context, state, and findings across multiple tool and
    workflow executions. It can be saved to and loaded from a JSON file,
    providing full resumability if the investigation is interrupted.
    """

    def __init__(self, session_id: str | None = None, mode: str = "manual") -> None:
        """
        Initialize a new or existing investigation session.

        Args:
            session_id: An optional unique identifier. If not provided,
                        a new UUID will be generated.
            mode: Investigation mode, either "auto" or "manual".
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.mode = mode
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.state: Dict[str, Any] = {}
        self.findings: Dict[str, Any] = {}

    def update_state(self, key: str, value: Any) -> None:
        """Update the internal session state with a given key and value."""
        self.state[key] = value
        self.updated_at = datetime.utcnow().isoformat()

    def add_finding(self, module_name: str, data: Any) -> None:
        """
        Store a finding from a specific module.

        Args:
            module_name: The name of the module or workflow producing the finding.
            data: The analysis results.
        """
        if module_name not in self.findings:
            self.findings[module_name] = []
        self.findings[module_name].append(data)
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the session to a dictionary."""
        return {
            "session_id": self.session_id,
            "mode": getattr(self, "mode", "manual"),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state,
            "findings": self.findings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Deserialize a session from a dictionary."""
        session = cls(session_id=data.get("session_id"), mode=data.get("mode", "manual"))
        session.created_at = data.get("created_at", session.created_at)
        session.updated_at = data.get("updated_at", session.updated_at)
        session.state = data.get("state", {})
        session.findings = data.get("findings", {})
        return session

    def save(self, file_path: str | Path) -> None:
        """
        Save the current session state to a JSON file.

        Args:
            file_path: The filesystem path where the JSON file should be saved.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, file_path: str | Path) -> "Session":
        """
        Load a session from a JSON file.

        Args:
            file_path: The filesystem path to the saved JSON file.

        Returns:
            A reconstructed Session object.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
