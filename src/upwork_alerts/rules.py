from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .models import JobAlert, TriageResult

HOURLY_RE = re.compile(r"\$(\d+(?:\.\d+)?)\s*(?:-|to)\s*\$(\d+(?:\.\d+)?)\s*(?:/hr|hourly)", re.IGNORECASE)
FIXED_RE = re.compile(r"(?:fixed(?:-price)?|budget)\D{0,20}\$(\d[\d,]*(?:\.\d+)?)", re.IGNORECASE)


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def rule_triage(alert: JobAlert, config: dict[str, Any]) -> TriageResult:
    haystack = f"{alert.title}\n{alert.body}".lower()
    rejects = [term for term in config.get("hard_reject", []) if term.lower() in haystack]
    if rejects:
        return TriageResult(
            recommendation="IGNORE",
            score=0,
            lane="none",
            reason=f"Hard-reject term found: {', '.join(rejects[:3])}.",
            proof="",
            risks=rejects,
        )

    best_lane = "none"
    best_matches: list[str] = []
    best_proof = ""
    for lane, details in config.get("lanes", {}).items():
        matches = [keyword for keyword in details.get("keywords", []) if keyword.lower() in haystack]
        if len(matches) > len(best_matches):
            best_lane = lane
            best_matches = matches
            best_proof = details.get("proof", "")

    score = min(8, len(best_matches) * 2)
    risks: list[str] = []
    thresholds = config.get("thresholds", {})

    hourly = HOURLY_RE.search(haystack)
    if hourly:
        maximum = float(hourly.group(2))
        if maximum < float(thresholds.get("minimum_hourly", 30)):
            risks.append(f"Hourly ceiling ${maximum:g} is below the configured floor.")
            score -= 3

    fixed = FIXED_RE.search(haystack)
    if fixed:
        budget = float(fixed.group(1).replace(",", ""))
        if budget < float(thresholds.get("minimum_fixed", 750)):
            risks.append(f"Fixed budget ${budget:g} is below the configured floor.")
            score -= 3

    score = max(0, min(10, score))
    threshold = int(thresholds.get("review_score", 5))
    recommendation = "REVIEW" if score >= threshold and best_lane != "none" else "IGNORE"
    reason = (
        f"Matched {len(best_matches)} signals in {best_lane}: {', '.join(best_matches[:5])}."
        if best_matches
        else "No focused positioning lane matched the alert."
    )
    return TriageResult(
        recommendation=recommendation,
        score=score,
        lane=best_lane,
        reason=reason,
        proof=best_proof,
        risks=risks,
    )

