from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Label, Button

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        # Filter out hidden files/directories (starting with .)
        return [p for p in paths if not p.name.startswith(".")]

class FileTreeModal(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Vertical(id="file-tree-dialog"):
            yield Label("[b #e5c07b]Select Problem File[/]", id="file-tree-title")
            yield FilteredDirectoryTree(str(Path.cwd()), id="problem-tree")
            yield Label("[dim]Press Enter to select, Escape to cancel.[/dim]")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(str(event.path))
        
    def on_key(self, event):
        if event.key == "escape":
            self.dismiss(None)
