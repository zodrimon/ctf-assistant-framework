import argparse
import sys
from pathlib import Path

from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner
from ctf_assistant.engine.report import ReportRenderer
from ctf_assistant.modules.forensics.file_analysis.module import FileAnalysisModule
from ctf_assistant.rag.ingest import ingest_file
from ctf_assistant.rag.retriever import retrieve_notes


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


def ingest(args):
    target_file = Path(args.file).resolve()
    ingest_file(target_file)


def search(args):
    print(f"[*] Searching for: '{args.query}'")
    notes = retrieve_notes(args.query, n_results=3)
    
    if not notes:
        print("No relevant notes found.")
        return
        
    for i, note in enumerate(notes, 1):
        print(f"\n--- Result {i} (Distance: {note['distance']:.4f}) ---")
        print(f"Source: {note['metadata'].get('source', 'Unknown')} (Chunk {note['metadata'].get('chunk_index', 0)})")
        print(note['text'])
        print("-" * 50)


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

    # `ingest` command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest a file into the RAG knowledge base"
    )
    ingest_parser.add_argument("file", help="Path to the document (.md, .txt, .pdf) to ingest")

    # `search` command
    search_parser = subparsers.add_parser(
        "search", help="Search the RAG knowledge base"
    )
    search_parser.add_argument("query", help="Text to search for")

    args = parser.parse_args()

    if args.command == "investigate":
        investigate(args)
    elif args.command == "ingest":
        ingest(args)
    elif args.command == "search":
        search(args)

if __name__ == "__main__":
    main()
