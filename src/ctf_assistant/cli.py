import argparse
import sys
from pathlib import Path

from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner
from ctf_assistant.engine.report import ReportRenderer
from ctf_assistant.modules.forensics.file_analysis.module import FileAnalysisModule
from ctf_assistant.rag.ingest import ingest_file
from ctf_assistant.rag.retriever import retrieve_notes
from ctf_assistant.ai.gemini import GeminiProvider

def report(args):
    if not args.action == "export":
        print(f"Unknown report action: {args.action}", file=sys.stderr)
        sys.exit(1)
        
    session_file = Path(args.session).resolve()
    if not session_file.exists():
        print(f"Error: Session file not found: {session_file}", file=sys.stderr)
        sys.exit(1)
        
    try:
        session = Session.load(session_file)
    except Exception as e:
        print(f"Error loading session: {e}", file=sys.stderr)
        sys.exit(1)
        
    renderer = ReportRenderer()
    format_type = args.format.lower()
    
    if format_type == "md":
        output_str = renderer.render_markdown(session)
        out_path = session_file.with_suffix(".md")
        out_path.write_text(output_str, encoding="utf-8")
        print(f"[*] Exported Markdown report to: {out_path}")
    elif format_type == "html":
        output_str = renderer.render_html(session)
        out_path = session_file.with_suffix(".html")
        out_path.write_text(output_str, encoding="utf-8")
        print(f"[*] Exported HTML report to: {out_path}")
    elif format_type == "pdf":
        out_path = session_file.with_suffix(".pdf")
        success = renderer.render_pdf(session, out_path)
        if success:
            print(f"[*] Exported PDF report to: {out_path}")
        else:
            print(f"Error generating PDF.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unsupported format: {format_type}", file=sys.stderr)
        sys.exit(1)

def investigate(args):
    target_file = Path(args.file).resolve()
    if not target_file.exists():
        print(f"Error: Target file not found: {target_file}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Starting investigation on: {target_file.name}")
    session = Session(mode=args.mode)

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

    # Step 3: AI Analysis (if requested)
    if hasattr(args, 'ai') and args.ai == "gemini":
        print("\n[*] Initializing Gemini AI Provider...")
        ai_provider = GeminiProvider()
        
        if not ai_provider.is_available():
            print("\n" + "="*60)
            print("🤖 AI Feature Requested but API Key is Missing!")
            print("="*60)
            print("You selected the 'gemini' AI provider, but the 'GEMINI_API_KEY'")
            print("environment variable was not found.")
            print("\nDon't worry! You can use this for FREE by getting an API key:")
            print("1. Go to: https://aistudio.google.com/app/apikey")
            print("2. Generate a free key.")
            print("3. Run this in your terminal before starting:")
            print("   export GEMINI_API_KEY='your_key'       (Linux/macOS)")
            print("   $env:GEMINI_API_KEY='your_key'         (Windows PowerShell)")
            print("\nThe framework will proceed locally WITHOUT the AI analysis.")
            print("="*60 + "\n")
        else:
            print("[*] Asking AI for advice based on findings...")
            advice = ai_provider.analyze_findings(session.findings)
            if advice:
                session.add_finding("AI_Advisor", {"step": "Analysis", "status": "success", "advice": advice})
                print("[+] AI advice added to the report.")

    # Step 4: Print Findings
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
    investigate_parser.add_argument("--mode", help="Investigation mode (auto or manual)", choices=["auto", "manual"], default="manual")
    investigate_parser.add_argument("--ai", help="Select an optional AI provider to analyze findings", choices=["gemini"])

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

    # `tui` command
    tui_parser = subparsers.add_parser(
        "tui", help="Launch the interactive Terminal User Interface (TUI)"
    )

    # `report` command
    report_parser = subparsers.add_parser(
        "report", help="Manage and export investigation reports"
    )
    report_subparsers = report_parser.add_subparsers(dest="action", required=True)
    
    export_parser = report_subparsers.add_parser("export", help="Export a session report")
    export_parser.add_argument("session", help="Path to the session .json file")
    export_parser.add_argument("--format", choices=["md", "html", "pdf"], required=True, help="Export format")

    args = parser.parse_args()

    if args.command == "investigate":
        investigate(args)
    elif args.command == "ingest":
        ingest(args)
    elif args.command == "search":
        search(args)
    elif args.command == "tui":
        from ctf_assistant.tui.app import run_tui
        run_tui()
    elif args.command == "report":
        report(args)

if __name__ == "__main__":
    main()
