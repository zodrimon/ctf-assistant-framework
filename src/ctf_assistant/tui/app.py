from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from ctf_assistant.modules import MODULES

class CTFAssistantApp(App):
    """A Textual app for CTF Assistant."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("Available Forensic Modules:", id="title")
        
        items = []
        for name, _ in MODULES.items():
            items.append(ListItem(Label(f"Module: {name}")))
            
        yield ListView(*items, id="module_list")
        yield Footer()

def run_tui():
    app = CTFAssistantApp()
    app.run()
