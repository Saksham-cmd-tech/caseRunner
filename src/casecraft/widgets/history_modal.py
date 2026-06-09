"""
widgets/history_modal.py — Modal dialog showing recent execution history.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from history import ExecutionHistory


class HistoryModal(ModalScreen):
    """Display execution history entries."""

    CSS = """
    HistoryModal {
        align: center middle;
        background: transparent;
    }

    #history-outer {
        width: 90;
        height: auto;
        background: #1e222a;
        border: solid #e5c07b;
        padding: 1 2;
    }

    #history-title {
        text-align: center;
        color: #e5c07b;
        text-style: bold;
        margin-bottom: 1;
    }

    #history-content {
        height: 24;
        overflow-y: auto;
        background: #282c34;
        border: solid #3e4452;
        padding: 1;
        color: #abb2bf;
        margin-bottom: 1;
    }

    #history-footer {
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

    def __init__(self, history: ExecutionHistory) -> None:
        super().__init__()
        self.history = history

    def compose(self) -> ComposeResult:
        with Vertical(id="history-outer"):
            yield Label("🕒 Execution History", id="history-title")
            history_content = Static("", id="history-content")
            yield history_content

            if not self.history.entries:
                history_content.update("No history available yet.")
            else:
                lines: list[str] = []
                for entry in reversed(self.history.get_recent(30)):
                    lines.append(
                        f"[{entry.timestamp}] {entry.test_case_label} — "
                        f"{entry.verdict} "
                        f"({entry.runtime_ms:.0f}ms)"
                    )
                history_content.update("\n".join(lines))

            yield Button("Close  (esc)", id="btn-close")

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
