"""
widgets/add_modal.py — Modal screen for adding or editing a test case.
Fields: Label/Name, Input (stdin), Expected Output.
Dismiss with ctrl+s to save or Escape to cancel.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from casecraft.models import TestCase


class AddTestCaseModal(ModalScreen[TestCase | None]):
    """
    A modal dialog for creating or editing a TestCase.
    Returns the new/updated TestCase on save, or None on cancel.
    """

    # ── Taproom Tokyo Night modal CSS ─────────────────────────────────────────────────
    CSS = """
    AddTestCaseModal {
        align: center middle;
        background: rgba(40,44,52,0.85);
    }

    #modal-outer {
        width: 72;
        height: auto;
        background: #282c34;
        border: round #e5c07b;
        padding: 1 2;
    }

    #modal-title {
        text-align: center;
        color: #e5c07b;
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        color: #abb2bf;
        margin-top: 1;
        height: 1;
    }

    #input-label, #input-data, #input-expected {
        background: #282c34;
        border: round #5c6370;
        color: #abb2bf;
    }

    #input-label { height: 3; }
    #input-data { height: 7; margin-bottom: 0; }
    #input-expected { height: 7; margin-bottom: 0; }

    #input-label:focus, #input-data:focus, #input-expected:focus {
        border: round #98c379;
    }

    #btn-row {
        margin-top: 1;
        height: 3;
        align: right middle;
    }

    #btn-save {
        background: #282c34;
        color: #98c379;
        border: round #98c379;
        margin-right: 1;
    }
    #btn-save:hover { background: #98c379; color: #282c34; }

    #btn-cancel {
        background: #282c34;
        color: #e06c75;
        border: round #e06c75;
    }
    #btn-cancel:hover { background: #e06c75; color: #282c34; }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("ctrl+s", "save", "Save",    show=False),
    ]

    def __init__(self, existing: TestCase | None = None) -> None:
        super().__init__()
        self.existing = existing

    # ── composition ───────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        title = "Edit Test Case" if self.existing else "Add Test Case"
        with Vertical(id="modal-outer"):
            yield Label(title, id="modal-title")

            yield Label("Label / Name", classes="field-label")
            yield Input(
                value=self.existing.label if self.existing else "",
                placeholder="e.g. Basic case, Large input, Edge case…",
                id="input-label",
            )

            yield Label("Input  (stdin)", classes="field-label")
            yield TextArea(
                text=self.existing.input_data if self.existing else "",
                id="input-data",
            )

            yield Label("Expected Output", classes="field-label")
            yield TextArea(
                text=self.existing.expected_output if self.existing else "",
                id="input-expected",
            )

            with Horizontal(id="btn-row"):
                yield Button("Save  ctrl+s", id="btn-save")
                yield Button("Cancel  esc",  id="btn-cancel")

    # ── actions ───────────────────────────────────────────────────────────────

    def action_save(self) -> None:
        self._commit()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self._commit()
        else:
            self.dismiss(None)

    # ── internals ─────────────────────────────────────────────────────────────

    def _commit(self) -> None:
        """Validate fields and dismiss with a TestCase."""
        label    = self.query_one("#input-label",    Input).value.strip()
        in_data  = self.query_one("#input-data",     TextArea).text
        expected = self.query_one("#input-expected", TextArea).text

        # fall back to a generic label if blank
        if not label:
            label = "Test Case"

        if self.existing:
            tc = TestCase(
                id=self.existing.id,
                label=label,
                input_data=in_data,
                expected_output=expected,
            )
        else:
            tc = TestCase(label=label, input_data=in_data, expected_output=expected)

        self.dismiss(tc)
