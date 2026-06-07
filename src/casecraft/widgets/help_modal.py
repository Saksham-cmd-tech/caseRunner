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
        background: rgba(26,27,38,0.85);
    }

    #help-outer {
        width: 100;
        height: auto;
        background: #1f2335;
        border: solid #7aa2f7;
        padding: 1 2;
    }

    #help-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }

    #help-content {
        height: 30;
        overflow-y: auto;
        background: #1a1b26;
        border: solid #292e42;
        padding: 1;
        color: #a9b1d6;
        margin-bottom: 1;
    }

    #help-footer {
        text-align: right;
    }

    #btn-close {
        background: #0d1a3a;
        color: #7aa2f7;
        border: tall #7aa2f7;
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

            help_text = """[#7aa2f7 bold]FILE OPERATIONS[/]
[#9ece6a]ctrl+o[/]    Open file browser
[#9ece6a]ctrl+s[/]    Save (auto-save enabled)
[#9ece6a]ctrl+g[/]    Show run history
[#9ece6a]q[/]         Quit app

[#7aa2f7 bold]TEST CASE MANAGEMENT[/]
[#9ece6a]a[/]         Add new test case
[#9ece6a]e[/]         Edit selected test case
[#9ece6a]d[/]         Delete selected test case
[#9ece6a]y[/]         Duplicate selected test case
[#9ece6a]/[/]         Search/filter test cases
[#9ece6a]tab[/]       Switch between panels

[#7aa2f7 bold]RUNNING TESTS[/]
[#9ece6a]ctrl+r[/]    Run all test cases
[#9ece6a]enter[/]     Run selected test case (in TC list)
[#9ece6a]ctrl+w[/]    Toggle watch mode (auto-run on file change)

[#7aa2f7 bold]IMPORT & EXPORT[/]
[#9ece6a]ctrl+i[/]    Import test cases from text
[#9ece6a]ctrl+e[/]    Export results as markdown

[#7aa2f7 bold]COMPARE & DIAGNOSTICS[/]
[#9ece6a]ctrl+x[/]    Compare with another solution

[#7aa2f7 bold]OTHER[/]
[#9ece6a]?[/]  or  [#9ece6a]ctrl+h[/]    Show this help
"""

            yield Static(help_text, id="help-content")

            yield Button("Close  (esc)", id="btn-close")

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
