"""
widgets/search_modal.py — Modal for searching and filtering test cases.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static


class SearchModal(ModalScreen[str | None]):
    """Modal for searching test cases by name or content."""

    CSS = """
    SearchModal {
        align: center middle;
        background: rgba(26,27,38,0.85);
    }

    #search-outer {
        width: 70;
        height: auto;
        background: #1f2335;
        border: solid #7aa2f7;
        padding: 1 2;
    }

    #search-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }

    #search-input {
        background: #1a1b26;
        border: tall #7aa2f7;
        color: #a9b1d6;
        height: 3;
        margin-bottom: 1;
    }

    #search-input:focus {
        border: tall #7aa2f7;
    }

    #search-help {
        color: #565f89;
        height: 2;
        font-size: 9;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("enter", "confirm", "Search", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.search_query = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="search-outer"):
            yield Label("🔍 Search Test Cases", id="search-title")

            yield Input(
                placeholder="Type to search by name or content...",
                id="search-input",
            )

            yield Static(
                "[#565f89]enter[/] search · [#565f89]esc[/] cancel",
                id="search-help",
            )

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_confirm(self) -> None:
        search_input = self.query_one("#search-input", Input)
        self.search_query = search_input.value.strip().lower()
        self.dismiss(self.search_query if self.search_query else None)

    def action_cancel(self) -> None:
        self.dismiss(None)
