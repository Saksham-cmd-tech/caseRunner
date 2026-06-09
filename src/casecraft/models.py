"""
models.py — Data models for CaseCraft 2.0.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Verdict(str, Enum):
    ACCEPTED           = "AC"
    WRONG_ANSWER       = "WA"
    RUNTIME_ERROR      = "RE"
    TIME_LIMIT_EXCEEDED = "TLE"
    COMPILATION_ERROR  = "CE"
    PENDING            = "—"
    RUNNING            = "↻"


VERDICT_COLOR: dict[Verdict, str] = {
    Verdict.ACCEPTED:            "#98c379",
    Verdict.WRONG_ANSWER:        "#e06c75",
    Verdict.RUNTIME_ERROR:       "#bb9af7",
    Verdict.TIME_LIMIT_EXCEEDED: "#e0af68",
    Verdict.COMPILATION_ERROR:   "#e06c75",
    Verdict.PENDING:             "#5c6370",
    Verdict.RUNNING:             "#e5c07b",
}


@dataclass
class TestCase:
    label:           str
    input_data:      str
    expected_output: str
    id:              str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "label":           self.label,
            "input_data":      self.input_data,
            "expected_output": self.expected_output,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TestCase:
        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            label=data.get("label", "Test Case"),
            input_data=data.get("input_data", ""),
            expected_output=data.get("expected_output", ""),
        )


@dataclass
class TestResult:
    test_case:     TestCase
    verdict:       Verdict
    runtime_ms:    Optional[float]
    actual_output: str
    error:         Optional[str]
    timed_out:     bool


@dataclass
class Session:
    """Represents a specific problem or file."""
    file_path:   str
    test_cases:  list[TestCase] = field(default_factory=list)
    last_opened: str = ""

    def to_dict(self) -> dict:
        return {
            "file_path":   self.file_path,
            "last_opened": self.last_opened,
            "test_cases":  [tc.to_dict() for tc in self.test_cases],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Session:
        return cls(
            file_path=data["file_path"],
            last_opened=data.get("last_opened", ""),
            test_cases=[TestCase.from_dict(tc) for tc in data.get("test_cases", [])],
        )

@dataclass
class WorkspaceState:
    """Root state for the application."""
    sessions: dict[str, Session] = field(default_factory=dict)
    active_file: str | None = None
