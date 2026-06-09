"""
widgets/help_modal.py — Help modal showing all keyboard shortcuts and features.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class HelpModal(ModalScreen):
    """Display help and keyboard shortcuts."""

    CSS = """
    HelpModal {
        align: center middle;
        background: transparent;
    }

    #help-outer {
        width: 100;
        height: auto;
        background: #1e222a;
        border: solid #e5c07b;
        padding: 1 2;
    }

    #help-title {
        text-align: center;
        color: #e5c07b;
        text-style: bold;
        margin-bottom: 1;
    }

    #help-content {
        height: 30;
        overflow-y: auto;
        background: #282c34;
        border: solid #3e4452;
        padding: 1;
        color: #abb2bf;
        margin-bottom: 1;
    }

    #help-footer {
        text-align: right;
    }

    #btn-close {
        background: #0d1a3a;
        color: #e5c07b;
        border: tall #e5c07b;
    }

    #btn-close:hover {
        background: #1a2a4a;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-outer"):
            yield Label("⌨ CaseCraft Keyboard Shortcuts", id="help-title")

            help_text = """[#e5c07b bold]FILE OPERATIONS[/]
[#98c379]ctrl+o[/]    Open file browser
[#98c379]ctrl+s[/]    Save (auto-save enabled)
[#98c379]ctrl+g[/]    Show run history
[#98c379]q[/]         Quit app

[#e5c07b bold]TEST CASE MANAGEMENT[/]
[#98c379]a[/]         Add new test case
[#98c379]e[/]         Edit selected test case
[#98c379]d[/]         Delete selected test case
[#98c379]y[/]         Duplicate selected test case
[#98c379]/[/]         Search/filter test cases
[#98c379]tab[/]       Switch between panels

[#e5c07b bold]RUNNING TESTS[/]
[#98c379]ctrl+r[/]    Run all test cases
[#98c379]enter[/]     Run selected test case (in TC list)
[#98c379]ctrl+w[/]    Toggle watch mode (auto-run on file change)

[#e5c07b bold]IMPORT & EXPORT[/]
[#98c379]ctrl+i[/]    Import test cases from text
[#98c379]ctrl+e[/]    Export results as markdown

[#e5c07b bold]COMPARE & DIAGNOSTICS[/]
[#98c379]ctrl+x[/]    Compare with another solution

[#e5c07b bold]OTHER[/]
[#98c379]?[/]  or  [#98c379]ctrl+h[/]    Show this help
"""

            yield Static(help_text, id="help-content")

            yield Button("Close  (esc)", id="btn-close")

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
