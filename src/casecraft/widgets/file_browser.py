"""
widgets/file_browser.py — File browser modal for selecting Python files.
Allows navigating directories and selecting .py files.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Static

from models import TestCase


class FileBrowserModal(ModalScreen[str | None]):
    """
    A modal dialog for selecting a Python file.
    Returns the selected file path as a string, or None on cancel.
    """

    CSS = """
    FileBrowserModal {
        align: center middle;
        background: transparent;
    }

    #browser-outer {
        width: 80;
        height: auto;
        background: #1e222a;
        border: solid #e5c07b;
        padding: 1 2;
    }

    #browser-title {
        text-align: center;
        color: #e5c07b;
        text-style: bold;
        margin-bottom: 1;
    }

    .browser-label {
        color: #5c6370;
        margin-top: 1;
        height: 1;
    }

    #current-path {
        background: #282c34;
        border: tall #3e4452;
        color: #7dcfff;
        height: 3;
    }

    #current-path:focus {
        border: tall #e5c07b;
    }

    #path-status {
        color: #e5c07b;
        height: 1;
        margin-bottom: 1;
    }

    #file-table {
        height: 12;
        background: #282c34;
        border: solid #3e4452;
        scrollbar-background: #282c34;
        scrollbar-color: #3e4452;
        scrollbar-color-hover: #3d4466;
    }

    #btn-row {
        margin-top: 1;
        height: 3;
        align: right middle;
    }

    #btn-select {
        background: #1a2e12;
        color: #98c379;
        border: tall #3d6b1a;
        margin-right: 1;
    }

    #btn-select:hover {
        background: #243d1a;
    }

    #btn-cancel {
        background: #2d1020;
        color: #e06c75;
        border: tall #6b2040;
    }

    #btn-cancel:hover {
        background: #3d1428;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("enter", "select", "Select", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.current_dir = Path.home()

    def compose(self) -> ComposeResult:
        with Vertical(id="browser-outer"):
            yield Label("Select Python File", id="browser-title")

            yield Label("Current Directory / Paste file path", classes="browser-label")
            yield Input(
                value=str(self.current_dir),
                id="current-path",
                placeholder="Paste full directory or .py path and press Enter",
            )
            yield Static("Press Enter to navigate or select a Python file.", id="path-status")

            yield Label("Files & Directories", classes="browser-label")
            yield DataTable(
                id="file-table",
                cursor_type="row",
                show_header=False,
                zebra_stripes=False,
            )

            with Vertical(id="btn-row"):
                yield Button("Select  enter", id="btn-select")
                yield Button("Cancel  esc",  id="btn-cancel")

    def on_mount(self) -> None:
        """Initialize the file table."""
        table = self.query_one("#file-table", DataTable)
        table.add_columns(" ")
        self._refresh_file_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle pasted path or entered path in the browser input."""
        if event.input.id != "current-path":
            return

        target = Path(event.value.strip())
        status = self.query_one("#path-status", Static)

        if target.exists():
            if target.is_dir():
                self.current_dir = target
                self._refresh_file_list()
                status.update("Navigated to directory.")
            elif target.suffix == ".py":
                self.dismiss(str(target.resolve()))
            else:
                status.update("[#e0af68]Path exists but is not a .py file.[/]")
        else:
            status.update("[#e06c75]Path not found. Check the spelling and try again.[/]")

    def action_select(self) -> None:
        """Select the highlighted item or go into directory."""
        table = self.query_one("#file-table", DataTable)
        if table.row_count == 0:
            return

        row_key = table.cursor_row
        if row_key is None:
            return

        items = self._get_items()
        if 0 <= row_key < len(items):
            item_path = items[row_key]
            if item_path.is_dir():
                self.current_dir = item_path
                self._refresh_file_list()
            elif item_path.suffix == ".py":
                self.dismiss(str(item_path.resolve()))

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-select":
            self.action_select()
        else:
            self.dismiss(None)

    def on_data_table_row_selected(
        self, event: DataTable.RowSelected
    ) -> None:
        """Enter on file table → open directory or select file."""
        self.action_select()

    # ── internals ─────────────────────────────────────────────────────────────

    def _get_items(self) -> list[Path]:
        """Return sorted list of dirs + .py files in current directory."""
        try:
            items = []
            # Add parent directory (..)
            if self.current_dir.parent != self.current_dir:
                items.append(self.current_dir.parent)
            # Add subdirectories
            items.extend(
                sorted(
                    [p for p in self.current_dir.iterdir() if p.is_dir()],
                    key=lambda x: x.name,
                )
            )
            # Add .py files
            items.extend(
                sorted(
                    [p for p in self.current_dir.iterdir() if p.suffix == ".py"],
                    key=lambda x: x.name,
                )
            )
            return items
        except PermissionError:
            return []

    def _refresh_file_list(self) -> None:
        """Rebuild the file table from current directory."""
        table = self.query_one("#file-table", DataTable)
        table.clear()

        path_input = self.query_one("#current-path", Input)
        path_input.value = str(self.current_dir)

        items = self._get_items()
        for item in items:
            if item == self.current_dir.parent:
                label = "📁 .."
            elif item.is_dir():
                label = f"📁 {item.name}"
            else:
                label = f"🐍 {item.name}"

            table.add_row(label, key=str(item))
