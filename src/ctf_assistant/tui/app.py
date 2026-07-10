from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, RichLog, Label, TabbedContent, TabPane, ListView, ListItem
from textual.containers import Horizontal, Vertical
from textual import work
import sys
import json
from pathlib import Path

from ctf_assistant.modules import MODULES
from ctf_assistant.engine.session import Session
from ctf_assistant.engine.workflow import WorkflowRunner

class CTFAssistantApp(App):
    """A Textual app for CTF Assistant."""
    
    CSS = """
    #input_container {
        height: auto;
        padding: 1;
    }
    #log_view {
        height: 1fr;
        border: solid green;
    }
    #session_list {
        width: 1fr;
        border: solid blue;
    }
    #session_detail_view {
        width: 2fr;
        border: solid yellow;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="investigation_tab"):
            with TabPane("Investigation", id="investigation_tab"):
                with Vertical():
                    with Horizontal(id="input_container"):
                        yield Input(placeholder="Enter file path to investigate...", id="file_input")
                        yield Button("Start Triage", id="start_btn", variant="primary")
                    yield RichLog(id="log_view", highlight=True, markup=True)
            with TabPane("Session Browser", id="session_tab"):
                with Horizontal():
                    yield ListView(id="session_list")
                    yield RichLog(id="session_detail_view", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self.load_sessions()

    def load_sessions(self) -> None:
        session_list = self.query_one("#session_list", ListView)
        session_list.clear()
        
        sessions_dir = Path(".ctf-assistant/sessions")
        if not sessions_dir.exists():
            return
            
        for path in sorted(sessions_dir.glob("*.json"), reverse=True):
            item = ListItem(Label(path.name), id=f"session_{path.stem}")
            # Attach the path so we can read it later
            item.session_path = path
            session_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "session_list":
            detail_view = self.query_one("#session_detail_view", RichLog)
            detail_view.clear()
            
            path = getattr(event.item, "session_path", None)
            if path and path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        formatted_json = json.dumps(data, indent=2)
                        detail_view.write(formatted_json)
                except Exception as e:
                    detail_view.write(f"[red]Error loading session: {e}[/red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start_btn":
            file_path = self.query_one("#file_input", Input).value
            if not file_path:
                self.query_one("#log_view", RichLog).write("[red]Please enter a file path.[/red]")
                return
            
            target_path = Path(file_path).resolve()
            if not target_path.exists():
                self.query_one("#log_view", RichLog).write(f"[red]File not found: {target_path}[/red]")
                return

            event.button.disabled = True
            self.query_one("#log_view", RichLog).clear()
            self.query_one("#log_view", RichLog).write(f"[blue]Starting investigation on {target_path}[/blue]")
            self.run_investigation(target_path)

    @work(thread=True)
    def run_investigation(self, target_path: Path) -> None:
        log = self.query_one("#log_view", RichLog)
        
        def write_log(text: str):
            self.call_from_thread(log.write, text)
            
        def enable_button():
            btn = self.query_one("#start_btn", Button)
            btn.disabled = False
            
        write_log("Running module detection...")
        
        matched_module = None
        matched_result = None
        
        # 1. Detect matching module
        for name, module_cls in MODULES.items():
            module = module_cls()
            result = module.analyze(target_path)
            if result.get("confidence") == "high":
                matched_module = module
                matched_result = result
                break
                
        # 2. Fallback logic
        if not matched_module:
            write_log("[yellow]No high-confidence module match found. Falling back to File Analysis.[/yellow]")
            from ctf_assistant.modules.forensics.file_analysis.module import FileAnalysisModule
            matched_module = FileAnalysisModule()
            matched_result = matched_module.analyze(target_path)
            
        write_log(f"[bold green]Selected Module: {matched_module.get_name()}[/bold green]")
        
        # 3. Resolve workflow path
        module_file = sys.modules[matched_module.__class__.__module__].__file__
        workflow_path = Path(module_file).parent / "workflow.yaml"
        
        if not workflow_path.exists():
            write_log(f"[bold red]Workflow file not found at {workflow_path}[/bold red]")
            self.call_from_thread(enable_button)
            return
            
        # 4. Setup Session and Runner
        session = Session(mode="auto")
        session.add_finding(matched_module.get_name(), matched_result)
        runner = WorkflowRunner(session)
        
        def workflow_callback(event_type, data):
            if event_type == "start_step":
                self.call_from_thread(log.write, f"\n[bold cyan]=== Step: {data['step_name']} ===[/bold cyan]")
                self.call_from_thread(log.write, f"[cyan]$ {data['command']}[/cyan]")
            elif event_type == "output":
                self.call_from_thread(log.write, data.rstrip())
            elif event_type == "end_step":
                status = data.get('status')
                if status == "error":
                    self.call_from_thread(log.write, f"[bold red]Error:[/bold red] {data.get('error')}")
                else:
                    self.call_from_thread(log.write, "[bold green]Step completed successfully.[/bold green]")
                    
        try:
            write_log("[bold magenta]Starting Workflow Execution...[/bold magenta]")
            runner.execute(workflow_path, context={"target": str(target_path)}, callback=workflow_callback)
            write_log("\n[bold green]Investigation Complete![/bold green]")
        except Exception as e:
            write_log(f"\n[bold red]Workflow execution failed: {e}[/bold red]")
            
        self.call_from_thread(self.load_sessions)
        self.call_from_thread(enable_button)

def run_tui():
    app = CTFAssistantApp()
    app.run()
