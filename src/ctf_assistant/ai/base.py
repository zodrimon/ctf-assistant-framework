from typing import Protocol, Optional, Dict, Any

class AIProvider(Protocol):
    """
    Base protocol that all AI providers must implement.
    This ensures that the main engine can swap out different AIs (Gemini, Ollama, etc.)
    without changing any core logic.
    """
    
    def is_available(self) -> bool:
        """
        Check if this AI provider is properly configured and available to use.
        """
        ...
        
    def analyze_findings(self, findings: Dict[str, Any]) -> Optional[str]:
        """
        Analyzes the investigation findings and returns human-readable advice or next steps.
        If an error occurs, it should handle it gracefully and return None.
        """
        ...
