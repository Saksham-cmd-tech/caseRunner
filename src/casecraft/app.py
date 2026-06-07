"""
app.py — CaseCraft 2.0 (3-pane layout with Taproom colors).
"""

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Static, Input, Label, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen

from casecraft.models import Session, TestCase, TestResult, Verdict, WorkspaceState
from casecraft.runner import run_all_test_cases_async
from casecraft.utils import (
    is_initialized, 
    initialize_workspace, 
    load_sessions, 
    save_sessions, 
    get_or_create_session, 
    load_last_file, 
    save_last_file
)
from casecraft.widgets.add_modal import AddTestCaseModal

CSS = """
Screen {
    background: #282c34;
    color: #abb2bf;
    padding: 1 2;
}

#top-bar {
    height: 3;
    layout: horizontal;
    margin-bottom: 1;
}

#search-box {
    width: 1fr;
    border: round #e5c07b;
    height: 3;
    background: #282c34;
    color: #abb2bf;
}
#search-box:focus {
    border: round #98c379;
}

#viewing-box {
    width: 30;
    border: round #e5c07b;
    height: 3;
    content-align: center middle;
    margin-left: 1;
}

#main-container {
    height: 1fr;
    layout: horizontal;
}

#left-column {
    width: 35%;
    height: 1fr;
    border: round #e5c07b;
    background: #282c34;
}

#prob-table {
    height: 40%;
    border-bottom: hkey #e5c07b;
    background: #282c34;
}

#tc-table {
    height: 60%;
    background: #282c34;
}

#right-panel {
    width: 65%;
    height: 1fr;
    border: round #e5c07b;
    padding: 0 1;
    margin-left: 1;
    overflow-y: auto;
}

DataTable > .datatable--header {
    background: #282c34;
    color: #e5c07b;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #3e4452;
    color: #ffffff;
}

DataTable:focus > .datatable--cursor {
    background: #e5c07b;
    color: #282c34;
    text-style: bold;
}

#footer-block {
    height: 4;
    margin-top: 1;
    color: #abb2bf;
}

/* Modals */
PromptModal, InitModal {
    align: center middle;
    background: rgba(40,44,52,0.85);
}
#prompt-dialog {
    width: 60;
    height: auto;
    background: #282c34;
    border: round #e5c07b;
    padding: 1 2;
}
#init-dialog {
    width: 50;
    height: auto;
    background: #282c34;
    border: round #e5c07b;
    padding: 1 2;
    align: center middle;
}
#init-dialog Button {
    margin-top: 1;
    width: 100%;
}
"""

class InitModal(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        with Vertical(id="init-dialog"):
            yield Label("[b #e5c07b]Not Initialized[/b]\n")
            yield Label("CaseCraft is not initialized in this directory.")
            yield Label("Would you like to initialize it by creating a `.casecraft` folder?")
            yield Button("Initialize Workspace", id="btn-init", variant="success")
            yield Button("Quit", id="btn-quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-init":
            self.dismiss(True)
        else:
            self.dismiss(False)


class PromptModal(ModalScreen[str | None]):
    def __init__(self, title: str, placeholder: str = ""):
        super().__init__()
        self.title_text = title
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt-dialog"):
            yield Label(self.title_text, classes="prompt-title")
            yield Input(placeholder=self.placeholder, id="prompt-input")
            yield Label("[dim]Press Enter to confirm, Escape to cancel.[/dim]")

    def on_mount(self):
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted):
        self.dismiss(event.value)
        
    def on_key(self, event):
        if event.key == "escape":
            self.dismiss(None)


class CaseCraftApp(App):
    CSS = CSS
    TITLE = "CaseCraft ~ Taproom UI (3-Pane)"

    BINDINGS = [
        Binding("space", "run_all", "Run All", show=False),
        Binding("p", "add_problem", "Add Prob", show=False),
        Binding("a", "add_test_case", "Add TC", show=False),
        Binding("e", "edit_test_case", "Edit TC", show=False),
        Binding("d", "delete_selected", "Delete", show=False),
        Binding("q", "quit", "Quit", show=False),
        Binding("slash", "focus_search", "Search", show=False),
        Binding("escape", "clear_search", "Clear Search", show=False),
    ]

    active_problem = reactive(None)
    active_test_case = reactive(None)
    search_query = reactive("", init=False)

    def __init__(self):
        super().__init__()
        # We load workspace empty initially, will populate after mount if initialized
        self.workspace = WorkspaceState(sessions={})
        self.results: dict[str, TestResult] = {}

    def compose(self) -> ComposeResult:
        with Horizontal(id="top-bar"):
            yield Input(placeholder="/ Search test cases...", id="search-box")
            yield Static("Viewing: All", id="viewing-box")
            
        with Horizontal(id="main-container"):
            with Vertical(id="left-column"):
                yield DataTable(id="prob-table", cursor_type="row")
                yield DataTable(id="tc-table", cursor_type="row")
            yield Static("Select a test case to view details...", id="right-panel")
            
        yield Static(
            "General       : [b #e5c07b]q/ctrl+c[/]: quit   [b #e5c07b]space[/]: run tests   [b #e5c07b]/[/]: search   [b #e5c07b]Esc[/]: clear search\n"
            "Management    : [b #e5c07b]a[/]: add test case   [b #e5c07b]e[/]: edit test case   [b #e5c07b]d[/]: delete\n"
            "Workspace     : [b #e5c07b]p[/]: load problem file   [b #e5c07b]tab[/]: switch focus",
            id="footer-block"
        )

    def on_mount(self):
        prob_table = self.query_one("#prob-table", DataTable)
        prob_table.add_column("Problem File")
        
        tc_table = self.query_one("#tc-table", DataTable)
        tc_table.add_columns("Verdict", "Test Case", "Time")

        if not is_initialized():
            def check_init(result: bool):
                if result:
                    initialize_workspace()
                    self._load_workspace_data()
                else:
                    self.exit()
            self.push_screen(InitModal(), check_init)
        else:
            self._load_workspace_data()

    def _load_workspace_data(self):
        self.workspace = WorkspaceState(
            sessions=load_sessions(),
            active_file=load_last_file()
        )
        self.refresh_problems()
        prob_table = self.query_one("#prob-table", DataTable)
        if self.workspace.active_file and self.workspace.active_file in self.workspace.sessions:
            self._select_problem_by_path(self.workspace.active_file)
            prob_table.focus()
        else:
            prob_table.focus()

    def _select_problem_by_path(self, fp: str):
        pt = self.query_one("#prob-table", DataTable)
        for i, row_key in enumerate(pt.rows):
            if row_key.value == fp:
                pt.move_cursor(row=i)
                self.active_problem = fp
                break

    def refresh_problems(self):
        pt = self.query_one("#prob-table", DataTable)
        pt.clear()
        
        q = self.search_query.lower()
        for fp in sorted(self.workspace.sessions.keys()):
            name = Path(fp).name
            if q and q not in name.lower():
                tc_match = any(q in tc.label.lower() for tc in self.workspace.sessions[fp].test_cases)
                if not tc_match:
                    continue
            pt.add_row(name, key=fp)

    def refresh_test_cases(self):
        tc_table = self.query_one("#tc-table", DataTable)
        tc_table.clear()
        
        if not self.active_problem:
            return
            
        session = self.workspace.sessions.get(self.active_problem)
        if not session:
            return
            
        q = self.search_query.lower()
        for tc in session.test_cases:
            if q and q not in tc.label.lower() and q not in Path(self.active_problem).name.lower():
                continue
                
            res = self.results.get(tc.id)
            verdict = res.verdict.value if res else Verdict.PENDING.value
            
            if verdict == Verdict.ACCEPTED.value:
                verdict_str = f"[#98c379]{verdict}[/]"
            elif verdict in (Verdict.PENDING.value, Verdict.RUNNING.value):
                verdict_str = f"[#61afef]{verdict}[/]"
            else:
                verdict_str = f"[#e06c75]{verdict}[/]"
                
            time_str = f"{res.runtime_ms:.0f}ms" if res and res.runtime_ms else "—"
            tc_table.add_row(verdict_str, tc.label, time_str, key=tc.id)

    def watch_active_problem(self, old_val, new_val):
        if new_val:
            self.workspace.active_file = new_val
            save_last_file(new_val)
            self.query_one("#viewing-box", Static).update(f"Viewing: {Path(new_val).name}")
        self.active_test_case = None
        self.refresh_test_cases()
        self.update_diff_view()
        
        tc_table = self.query_one("#tc-table", DataTable)
        if tc_table.row_count > 0:
            tc_table.move_cursor(row=0)
            self.active_test_case = tc_table.coordinate_to_cell_key(tc_table.cursor_coordinate).row_key.value

    def watch_active_test_case(self, old_val, new_val):
        self.update_diff_view()

    def watch_search_query(self, old_val, new_val):
        self.refresh_problems()
        self.refresh_test_cases()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "search-box":
            self.search_query = event.value

    def update_diff_view(self):
        panel = self.query_one("#right-panel", Static)
        
        if not self.active_problem or not self.active_test_case:
            panel.update("Select a test case to view details...")
            return
            
        session = self.workspace.sessions.get(self.active_problem)
        if not session:
            return
            
        tc = next((t for t in session.test_cases if t.id == self.active_test_case), None)
        if tc:
            res = self.results.get(tc.id)
            prob_name = Path(self.active_problem).name
            
            exp = tc.expected_output.strip() or "(empty)"
            
            if res:
                act = res.actual_output.strip() or "(empty)"
                err = res.error.strip() if res.error else ""
                
                color = "#98c379" if res.verdict == Verdict.ACCEPTED else "#e06c75"
                if res.verdict in (Verdict.PENDING, Verdict.RUNNING):
                    color = "#61afef"
                
                text = f"[b #e5c07b]▣ {tc.label}[/]\n"
                text += f"Problem: {prob_name}\n"
                text += f"Status: [{color}]{res.verdict.value}[/]\n"
                text += f"Runtime: {res.runtime_ms:.0f}ms\n"
                text += f"File: {self.active_problem}\n\n"
                
                text += f"────────────────────────────────\n\n"
                text += f"[b #e5c07b]Expected Output:[/]\n[#abb2bf]{exp}[/]\n\n"
                text += f"[b #e5c07b]Actual Output:[/]\n[{color}]{act}[/]\n"
                
                if err:
                    text += f"\n[b #e06c75]Stderr/Error:[/]\n[#d19a66]{err}[/]\n"
                panel.update(text)
            else:
                text = f"[b #e5c07b]▣ {tc.label}[/]\n"
                text += f"Problem: {prob_name}\n"
                text += f"Status: [#61afef]—[/]\n"
                text += f"File: {self.active_problem}\n\n"
                text += f"────────────────────────────────\n\n"
                text += f"[b #e5c07b]Expected Output:[/]\n[#abb2bf]{exp}[/]\n\n"
                text += f"[dim]Press space to run test case and see actual output.[/]"
                panel.update(text)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        if event.data_table.id == "prob-table" and event.row_key:
            self.active_problem = str(event.row_key.value)
        elif event.data_table.id == "tc-table" and event.row_key:
            self.active_test_case = str(event.row_key.value)

    def action_focus_search(self):
        self.query_one("#search-box", Input).focus()

    def action_clear_search(self):
        sb = self.query_one("#search-box", Input)
        if sb.has_focus:
            sb.value = ""
            self.query_one("#tc-table", DataTable).focus()
        else:
            self.query_one("#tc-table", DataTable).focus()

    async def action_add_problem(self):
        def check_reply(fp: str | None):
            if fp:
                path = Path(fp)
                if not path.is_absolute():
                    path = Path.cwd() / path
                path_str = str(path.resolve())
                if path_str not in self.workspace.sessions:
                    get_or_create_session(self.workspace.sessions, path_str)
                    save_sessions(self.workspace.sessions)
                    self.refresh_problems()
                self._select_problem_by_path(path_str)
        self.push_screen(PromptModal("Enter file path to load (e.g. main.py):"), check_reply)

    async def action_add_test_case(self):
        if not self.active_problem:
            return
            
        def check_reply(tc: TestCase | None):
            if tc:
                self.workspace.sessions[self.active_problem].test_cases.append(tc)
                save_sessions(self.workspace.sessions)
                self.refresh_test_cases()
        self.push_screen(AddTestCaseModal(), check_reply)

    async def action_edit_test_case(self):
        if not self.active_problem or not self.active_test_case:
            return
            
        session = self.workspace.sessions.get(self.active_problem)
        tc = next((t for t in session.test_cases if t.id == self.active_test_case), None)
        if not tc:
            return
            
        def check_reply(updated_tc: TestCase | None):
            if updated_tc:
                idx = next((i for i, t in enumerate(session.test_cases) if t.id == updated_tc.id), None)
                if idx is not None:
                    session.test_cases[idx] = updated_tc
                save_sessions(self.workspace.sessions)
                self.refresh_test_cases()
                self.update_diff_view()
                
        self.push_screen(AddTestCaseModal(existing=tc), check_reply)

    async def action_delete_selected(self):
        focused = self.focused
        if focused and focused.id == "prob-table":
            if self.active_problem in self.workspace.sessions:
                del self.workspace.sessions[self.active_problem]
                save_sessions(self.workspace.sessions)
                self.active_problem = None
                self.refresh_problems()
        elif focused and focused.id == "tc-table":
            if self.active_problem and self.active_test_case:
                session = self.workspace.sessions.get(self.active_problem)
                if session:
                    session.test_cases = [t for t in session.test_cases if t.id != self.active_test_case]
                    save_sessions(self.workspace.sessions)
                    self.active_test_case = None
                    self.refresh_test_cases()

    async def action_run_all(self):
        if not self.active_problem:
            return
            
        session = self.workspace.sessions.get(self.active_problem)
        if not session or not session.test_cases:
            return
            
        for tc in session.test_cases:
            self.results[tc.id] = TestResult(tc, Verdict.RUNNING, 0, "", "", False)
        self.refresh_test_cases()
        
        def progress(res: TestResult):
            self.results[res.test_case.id] = res
            self.refresh_test_cases()
            self.update_diff_view()
            
        results = await run_all_test_cases_async(self.active_problem, session.test_cases, progress_callback=progress)

if __name__ == "__main__":
    app = CaseCraftApp()
    app.run()
