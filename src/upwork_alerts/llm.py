from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .models import JobAlert, TriageResult

SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "recommendation": {"type": "string", "enum": ["REVIEW", "IGNORE"]},
        "score": {"type": "integer", "minimum": 0, "maximum": 10},
        "lane": {"type": "string"},
        "reason": {"type": "string"},
        "proof": {"type": "string"},
        "risks": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["recommendation", "score", "lane", "reason", "proof", "risks"],
    "additionalProperties": False,
}


def llm_triage(alert: JobAlert, config: dict[str, Any], baseline: TriageResult) -> TriageResult:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    if not api_key or not model:
        return baseline

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        store=False,
        instructions=(
            "You triage official Upwork job-alert email content for a senior agentic AI engineer. "
            "This is preliminary screening only. Never claim that client quality, competition, "
            "interviews, invites, payment verification, or hire rate passed because those fields "
            "are not available. Return REVIEW only when the work and budget appear relevant."
        ),
        input=json.dumps(
            {
                "job": {"title": alert.title, "body": alert.body[:12000], "url": alert.url},
                "profile": config,
                "rule_baseline": baseline.__dict__,
            }
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "upwork_alert_triage",
                "strict": True,
                "schema": SCHEMA,
            },
            "verbosity": "low",
        },
    )
    data = json.loads(response.output_text)
    return TriageResult(**data, source="openai")

