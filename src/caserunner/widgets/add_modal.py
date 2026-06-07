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

from caserunner.models import TestCase


class AddTestCaseModal(ModalScreen[TestCase | None]):
    """
    A modal dialog for creating or editing a TestCase.
    Returns the new/updated TestCase on save, or None on cancel.
    """

    # ── Tokyo Night modal CSS ─────────────────────────────────────────────────
    CSS = """
    AddTestCaseModal {
        align: center middle;
        background: rgba(26,27,38,0.85);
    }

    #modal-outer {
        width: 72;
        height: auto;
        background: #1f2335;
        border: solid #7aa2f7;
        padding: 1 2;
    }

    #modal-title {
        text-align: center;
        color: #7aa2f7;
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        color: #565f89;
        margin-top: 1;
        height: 1;
    }

    #input-label {
        background: #1a1b26;
        border: tall #292e42;
        color: #a9b1d6;
        height: 3;
    }

    #input-label:focus {
        border: tall #7aa2f7;
    }

    #input-data {
        background: #1a1b26;
        border: solid #292e42;
        color: #a9b1d6;
        height: 7;
        margin-bottom: 0;
    }

    #input-data:focus {
        border: solid #7aa2f7;
    }

    #input-expected {
        background: #1a1b26;
        border: solid #292e42;
        color: #a9b1d6;
        height: 7;
        margin-bottom: 0;
    }

    #input-expected:focus {
        border: solid #7aa2f7;
    }

    #btn-row {
        margin-top: 1;
        height: 3;
        align: right middle;
    }

    #btn-save {
        background: #1a2e12;
        color: #9ece6a;
        border: tall #3d6b1a;
        margin-right: 1;
    }

    #btn-save:hover {
        background: #243d1a;
    }

    #btn-cancel {
        background: #2d1020;
        color: #f7768e;
        border: tall #6b2040;
    }

    #btn-cancel:hover {
        background: #3d1428;
    }
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
