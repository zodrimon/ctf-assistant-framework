import os
import tempfile
import yaml
from pathlib import Path
from typing import Any, Dict, List

from ctf_assistant.engine.workflow import WorkflowRunner


class SteganographyWorkflow:
    """
    Workflow for analyzing media files for steganography.
    Provides an interactive menu for alternative tool paths based on media type.
    """

    def get_name(self) -> str:
        return "Steganography Analysis Workflow"

    def run(self, session: Any, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        # Retrieve the media type from the previous analysis
        findings = session.findings.get("Steganography Analysis", [])
        if not findings:
            return {"status": "error", "message": "No Steganography Analysis finding in session."}
        
        last_finding = findings[-1]
        if not last_finding.get("is_stego_candidate"):
            print("[*] File is not identified as a steganography candidate. Skipping stego workflow.")
            return {"status": "skipped"}
            
        media_type = last_finding.get("media_type", "unknown")
        
        # Define available tools
        available_tools = [
            {"name": "Strings Analysis", "command": ["strings", "-n", "10", "{target}"]},
            {"name": "Exiftool Metadata", "command": ["exiftool", "{target}"]},
            {"name": "Binwalk Extraction", "command": ["binwalk", "-e", "{target}"]},
        ]
        
        # Add format-specific tools
        if media_type in ["png", "bmp"]:
            available_tools.append({
                "name": "Zsteg (LSB Steganography)", 
                "command": ["zsteg", "-a", "{target}"]
            })
        elif media_type == "jpeg":
            available_tools.append({
                "name": "Steghide (Empty Password)", 
                "command": ["steghide", "extract", "-sf", "{target}", "-p", ""]
            })
            
        selected_tools = available_tools
            
        # Interactive Menu for Manual Mode
        if getattr(session, "mode", "manual") == "manual":
            print("\n" + "=" * 50)
            print("🔍 STEGANOGRAPHY ALTERNATIVE PATHS")
            print("=" * 50)
            print(f"Target: {evidence_path} (Type: {media_type.upper()})")
            print("Select the tools you want to run:")
            
            for idx, tool in enumerate(available_tools, 1):
                print(f"[{idx}] {tool['name']}")
            print("[a] Run all applicable tools")
            print("[q] Quit / Skip Steganography Workflow")
            
            while True:
                try:
                    choice = input("\nEnter selection (e.g., '1,3', 'a', 'q'): ").strip().lower()
                    if choice == 'q':
                        print("[*] Skipping steganography workflow.")
                        return {"status": "skipped"}
                    if choice == 'a' or choice == 'all':
                        selected_tools = available_tools
                        break
                    
                    indices = [int(x.strip()) for x in choice.split(",") if x.strip().isdigit()]
                    if not indices:
                        print("Invalid input. Please enter numbers separated by commas, 'a', or 'q'.")
                        continue
                        
                    selected_tools = []
                    for idx in indices:
                        if 1 <= idx <= len(available_tools):
                            selected_tools.append(available_tools[idx - 1])
                    
                    if selected_tools:
                        break
                    else:
                        print("Invalid selection. Try again.")
                except OSError:
                    # In test environments without stdin
                    selected_tools = available_tools
                    break
        
        if not selected_tools:
            return {"status": "skipped"}
            
        print(f"\n[*] Executing {len(selected_tools)} selected steganography tool(s)...")
        
        # Build dynamic YAML for selected tools
        steps = []
        for tool in selected_tools:
            steps.append({
                "name": tool["name"],
                "command": tool["command"]
            })
            
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
            yaml.dump({
                "name": self.get_name(),
                "steps": steps
            }, f)
            temp_yaml = f.name
            
        try:
            runner = WorkflowRunner(session)
            runner.execute(Path(temp_yaml), context={"target": evidence_path})
        finally:
            os.remove(temp_yaml)
            
        return {"status": "completed"}
