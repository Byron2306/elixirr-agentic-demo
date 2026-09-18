"""Shared output contract for the interview integration harness."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any, Literal

Mode = Literal["live", "replay", "unavailable"]
Status = Literal["ready", "running", "pass", "refuse", "needs_you", "fail"]

@dataclass
class DemoEnvelope:
    act: str
    mode: Mode
    status: Status
    trace_id: str
    authority: str
    summary: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    source_provenance: list[dict[str, str]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
