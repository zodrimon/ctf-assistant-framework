import argparse
import sys
from pathlib import Path

from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner
from ctf_assistant.engine.report import ReportRenderer
from ctf_assistant.modules.forensics.file_analysis.module import FileAnalysisModule


def investigate(args):
    target_file = Path(args.file).resolve()
    if not target_file.exists():
        print(f"Error: Target file not found: {target_file}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Starting investigation on: {target_file.name}")
    session = Session()

    # Step 1: Module Analysis (which internally uses Detector)
    print("[*] Running initial analysis (Detector)...")
    module = FileAnalysisModule()
    analysis_result = module.analyze(target_file)
    session.add_finding(module.get_name(), analysis_result)

    # Step 2: Workflow Runner
    print("[*] Executing baseline triage workflow...")
    runner = WorkflowRunner(session)
    # Locate the workflow.yaml relative to this script
    workflow_path = (
        Path(__file__).parent / "modules" / "forensics" / "file_analysis" / "workflow.yaml"
    )
    
    if not workflow_path.exists():
        print(f"Error: Workflow file not found at {workflow_path}", file=sys.stderr)
        sys.exit(1)
        
    runner.execute(workflow_path, context={"target": str(target_file)})

    # Step 3: Print Findings
    print("\n" + "="*50)
    print("INVESTIGATION REPORT")
    print("="*50 + "\n")
    
    renderer = ReportRenderer()
    report_md = renderer.render(session)
    print(report_md)


def main():
    parser = argparse.ArgumentParser(
        description="CTF Assistant Framework - Interactive Forensics"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")

    # `investigate` command
    investigate_parser = subparsers.add_parser(
        "investigate", help="Run initial detection and triage workflows on a file"
    )
    investigate_parser.add_argument("file", help="Path to the evidence file to analyze")

    args = parser.parse_args()

    if args.command == "investigate":
        investigate(args)

if __name__ == "__main__":
    main()
