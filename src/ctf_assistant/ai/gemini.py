import os
import json
from typing import Dict, Any, Optional

try:
    from google import genai
except ImportError:
    genai = None

from ctf_assistant.ai.base import AIProvider


class GeminiProvider(AIProvider):
    """
    Google Gemini implementation of the AIProvider.
    Uses the GEMINI_API_KEY environment variable.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key and genai:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-1.5-flash'
        else:
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    def analyze_findings(self, findings: Dict[str, Any]) -> Optional[str]:
        if not self.is_available():
            return None
            
        prompt = (
            "You are an expert CTF assistant and forensic analyst. "
            "Review the following automated triage findings and suggest "
            "the best manual next steps or potential flags/vulnerabilities to look for. "
            "Be concise, highly technical, and focus on actionable intelligence.\n\n"
            f"Findings:\n{json.dumps(findings, indent=2)}"
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"\n[!] AI Provider Error (Gemini): {e}")
            return None
