"""
widgets/import_modal.py — Modal for importing test cases from text blocks.
Supports bulk input/output format and custom parsing.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea

from casecraft.models import TestCase


class ImportTestsModal(ModalScreen[list[TestCase] | None]):
    """Modal for importing multiple test cases from a text block."""

    CSS = """
    ImportTestsModal {
        align: center middle;
        background: transparent;
    }

    #import-outer {
        width: 90;
        height: auto;
        background: #1e222a;
        border: solid #e5c07b;
        padding: 1 2;
    }

    #import-title {
        text-align: center;
        color: #e5c07b;
        text-style: bold;
        margin-bottom: 1;
    }

    .import-label {
        color: #5c6370;
        margin-top: 1;
        height: 1;
    }

    #import-help {
        color: #5c6370;
        height: 2;
        font-size: 10;
        margin-bottom: 1;
    }

    #import-area {
        background: #282c34;
        border: solid #3e4452;
        color: #abb2bf;
        height: 15;
        margin-bottom: 1;
    }

    #import-area:focus {
        border: solid #e5c07b;
    }

    #btn-row {
        height: 3;
        align: right middle;
    }

    #btn-import {
        background: #1a2e12;
        color: #98c379;
        border: tall #3d6b1a;
        margin-right: 1;
    }

    #btn-import:hover {
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
        Binding("ctrl+s", "import", "Import", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="import-outer"):
            yield Label("Import Test Cases", id="import-title")

            yield Label(
                "Paste test cases (Bulk format: Input\\nExpected Output\\n\\nInput\\nExpected...)",
                id="import-help",
            )

            yield TextArea(
                text="",
                id="import-area",
            )

            with Horizontal(id="btn-row"):
                yield Button("Import  ctrl+s", id="btn-import")
                yield Button("Cancel  esc", id="btn-cancel")

    def action_import(self) -> None:
        self._commit()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-import":
            self._commit()
        else:
            self.dismiss(None)

    def _commit(self) -> None:
        """Parse the text and create TestCase objects."""
        text_area = self.query_one("#import-area", TextArea)
        content = text_area.text.strip()

        if not content:
            self.dismiss(None)
            return

        test_cases = self._parse_tests(content)
        self.dismiss(test_cases if test_cases else None)

    def _parse_tests(self, content: str) -> list[TestCase]:
        """Parse bulk-style test format."""
        lines = content.strip().split("\n")
        test_cases = []
        i = 0
        case_num = 1

        while i < len(lines):
            # Skip empty lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break

            # Collect input
            input_lines = []
            while i < len(lines) and lines[i].strip():
                input_lines.append(lines[i])
                i += 1

            # Skip separator (empty line)
            while i < len(lines) and not lines[i].strip():
                i += 1

            # Collect expected output
            output_lines = []
            while i < len(lines) and lines[i].strip():
                output_lines.append(lines[i])
                i += 1

            if input_lines and output_lines:
                tc = TestCase(
                    label=f"Test {case_num}",
                    input_data="\n".join(input_lines),
                    expected_output="\n".join(output_lines),
                )
                test_cases.append(tc)
                case_num += 1

        return test_cases
