from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class JobAlert:
    message_id: str
    title: str
    url: str
    body: str
    received_at: str = ""


@dataclass(frozen=True)
class TriageResult:
    recommendation: str
    score: int
    lane: str
    reason: str
    proof: str
    risks: list[str] = field(default_factory=list)
    source: str = "rules"

