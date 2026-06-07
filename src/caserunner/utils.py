"""
utils.py — Utility functions for CaseRunner data persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

from caserunner.models import Session, TestCase

_DATA_DIR = Path.cwd() / ".caserunner"
SESSIONS_FILE = _DATA_DIR / "sessions.json"
LAST_FILE_PATH = _DATA_DIR / "last_file.txt"

def is_initialized() -> bool:
    return _DATA_DIR.exists() and _DATA_DIR.is_dir()

def initialize_workspace() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_FILE.exists():
        SESSIONS_FILE.write_text("{}", encoding="utf-8")

def load_sessions() -> dict[str, Session]:
    """Load all sessions from sessions.json. Returns empty dict if not initialized."""
    if not is_initialized() or not SESSIONS_FILE.exists():
        return {}
        
    try:
        raw: dict = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
        return {fp: Session.from_dict(s) for fp, s in raw.items()}
    except (json.JSONDecodeError, ValueError):
        return {}

def save_sessions(sessions: dict[str, Session]) -> None:
    """Save sessions. Fails silently if not initialized."""
    if not is_initialized():
        return
        
    data = {fp: s.to_dict() for fp, s in sessions.items()}
    SESSIONS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def get_or_create_session(sessions: dict[str, Session], file_path: str) -> Session:
    """Gets existing session or creates a new one for the file path."""
    if file_path not in sessions:
        sessions[file_path] = Session(file_path=file_path)
    return sessions[file_path]

def load_last_file() -> str | None:
    if is_initialized() and LAST_FILE_PATH.exists():
        content = LAST_FILE_PATH.read_text(encoding="utf-8").strip()
        if content:
            return content
    return None

def save_last_file(file_path: str) -> None:
    if is_initialized():
        LAST_FILE_PATH.write_text(file_path, encoding="utf-8")

def normalize_output(s: str) -> str:
    """Normalizes whitespace for strict comparisons."""
    return "\\n".join(line.rstrip() for line in s.splitlines()).rstrip()
