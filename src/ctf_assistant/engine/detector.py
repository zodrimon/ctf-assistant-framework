import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict


class MissingToolError(Exception):
    """Raised when a required system tool is not installed."""
    pass


class Detector:
    """
    Stub implementation for detecting file types.
    
    Currently relies on magic bytes and the 'file' command.
    Future iterations will implement multi-signal confidence scoring.
    """

    def _check_tool(self, tool_name: str) -> bool:
        """Check if a required tool is available in the system PATH."""
        return shutil.which(tool_name) is not None

    def get_magic_bytes(self, file_path: str | Path, num_bytes: int = 8) -> str:
        """
        Read the first few bytes of a file and return as a hex string.
        """
        path = Path(file_path)
        if not path.is_file():
            return ""

        try:
            with open(path, "rb") as f:
                header = f.read(num_bytes)
                return header.hex()
        except Exception:
            return ""

    def get_file_command_output(self, file_path: str | Path) -> str:
        """
        Run the Linux 'file' command on the target file.
        """
        if not self._check_tool("file"):
            # The engine must not install tools directly without prompting.
            # We raise an error so the UI/CLI layer can catch it and prompt the user.
            raise MissingToolError("Required tool 'file' is not installed.")

        try:
            result = subprocess.run(
                ["file", "-b", str(file_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error running file command: {e.stderr}"

    def identify(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Identify the file type using multiple basic signals.

        Returns:
            A dictionary containing the detected signals (no confidence scoring yet).
        """
        magic = self.get_magic_bytes(file_path)
        
        try:
            file_output = self.get_file_command_output(file_path)
        except MissingToolError as e:
            file_output = f"Error: {str(e)}"

        return {
            "magic_bytes": magic,
            "file_command": file_output
        }
