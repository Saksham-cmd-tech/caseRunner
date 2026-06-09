"""
widgets/diff_viewer.py — Side-by-side diff panel for expected vs actual output.
Also shows runtime, exit code, and match status in a strip at the bottom.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static

from models import TestResult, Verdict


class DiffViewer(Widget):
    """
    Renders a split view of expected output vs actual output for the
    currently selected test case result.
    Call :meth:`update` whenever the selection changes.
    """

    DEFAULT_CSS = """
    DiffViewer {
        height: 14;
        border-top: solid #3e4452;
    }

    #diff-header {
        background: #16161e;
        color: #5c6370;
        height: 1;
        padding: 0 1;
        border-bottom: solid #3e4452;
    }

    #diff-cols {
        height: 9;
    }

    .diff-col {
        width: 1fr;
        padding: 0 1;
        border-right: solid #3e4452;
        overflow-y: auto;
    }

    .diff-col:last-of-type {
        border-right: none;
    }

    .diff-col-label {
        color: #5c6370;
        height: 1;
        text-style: bold;
    }

    #diff-strip {
        background: #16161e;
        height: 1;
        padding: 0 1;
        border-top: solid #3e4452;
        color: #5c6370;
    }

    #diff-strip-bottom {
        background: #16161e;
        height: 1;
        padding: 0 1;
        color: #5c6370;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("diff — no test selected", id="diff-header")
        with Horizontal(id="diff-cols"):
            with Vertical(classes="diff-col"):
                yield Static("EXPECTED", classes="diff-col-label")
                yield Static("", id="expected-content")
            with Vertical(classes="diff-col"):
                yield Static("ACTUAL", classes="diff-col-label")
                yield Static("", id="actual-content")
        yield Static("", id="diff-strip")
        yield Static("", id="diff-strip-bottom")

    # ── public API ────────────────────────────────────────────────────────────

    def update(
        self,
        result: TestResult | None,
        compare_result: TestResult | None = None,
        compare_label: str = "",
    ) -> None:
        """Refresh the viewer with *result* and optional comparison data."""
        header   = self.query_one("#diff-header",      Static)
        exp_box  = self.query_one("#expected-content", Static)
        act_box  = self.query_one("#actual-content",   Static)
        strip    = self.query_one("#diff-strip",       Static)
        strip_b  = self.query_one("#diff-strip-bottom",Static)

        if result is None:
            header.update("diff — no test selected")
            exp_box.update("")
            act_box.update("")
            strip.update("")
            strip_b.update("")
            return

        tc = result.test_case
        header.update(f"diff — {tc.label}")

        exp_text = tc.expected_output.strip() or "(empty)"
        act_text = result.actual_output.strip()

        match result.verdict:
            case Verdict.ACCEPTED:
                exp_box.update(f"[#98c379]{exp_text}[/]")
                act_box.update(f"[#98c379]{act_text or exp_text}[/]")
                match_indicator = "[#98c379]✓  match[/]"

            case Verdict.WRONG_ANSWER:
                exp_box.update(f"[#98c379]{exp_text}[/]")
                act_box.update(f"[#e06c75]{act_text or '(empty)'}[/]")
                match_indicator = "[#e06c75]✗  mismatch[/]"

            case Verdict.TIME_LIMIT_EXCEEDED:
                exp_box.update(f"[#5c6370]{exp_text}[/]")
                act_box.update("[#e0af68]— timed out[/]")
                match_indicator = "[#e0af68]⧗  TLE[/]"

            case Verdict.RUNTIME_ERROR:
                exp_box.update(f"[#5c6370]{exp_text}[/]")
                err = result.error or "runtime error"
                act_box.update(f"[#e06c75]{err}[/]")
                match_indicator = "[#bb9af7]⚡  runtime error[/]"

            case _:
                exp_box.update(f"[#5c6370]{exp_text}[/]")
                act_box.update("[#5c6370]—[/]")
                match_indicator = ""

        # ── bottom info strip ─────────────────────────────────────────────────
        runtime_str = (
            ">2000ms"
            if result.timed_out
            else f"{result.runtime_ms:.0f}ms"
            if result.runtime_ms is not None
            else "—"
        )
        exit_code = "0" if result.verdict == Verdict.ACCEPTED else "≠ 0"

        strip.update(
            f"runtime: [#abb2bf]{runtime_str}[/]   "
            f"exit: [#abb2bf]{exit_code}[/]   "
            f"stderr: [#abb2bf]{'yes' if result.error else 'none'}[/]"
        )

        if compare_result is None:
            strip_b.update(match_indicator)
            return

        compare_status = ""
        if compare_label:
            compare_status = f" | compare: {compare_label}"
        if result.actual_output == compare_result.actual_output and result.verdict == compare_result.verdict:
            compare_status += " [#98c379]same output[/]"
        else:
            compare_status += " [#e06c75]different output[/]"
        strip_b.update(f"{match_indicator}{compare_status}")
