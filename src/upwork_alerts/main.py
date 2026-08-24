from __future__ import annotations

import os
from pathlib import Path

from .gmail import GmailClient
from .llm import llm_triage
from .notify import format_notification, notify
from .parser import extract_job_alerts
from .rules import load_config, rule_triage


def run() -> None:
    config_path = Path(os.getenv("PROFILE_CONFIG", "config/profile.yaml"))
    if not config_path.exists():
        config_path = Path("config/profile.example.yaml")
    config = load_config(config_path)

    label = os.getenv("GMAIL_PROCESSED_LABEL", "upwork-ai-reviewed")
    default_query = f"from:(upwork.com) newer_than:2d -label:{label}"
    query = os.getenv("GMAIL_QUERY") or default_query
    gmail = GmailClient()

    messages = gmail.fetch_unprocessed(query, int(os.getenv("MAX_EMAILS_PER_RUN", "20")))
    print(f"Found {len(messages)} unprocessed Upwork alert email(s).")

    for message in messages:
        alerts = extract_job_alerts(
            message.message_id,
            message.subject,
            message.text_body,
            message.html_body,
            message.received_at,
        )
        for alert in alerts:
            baseline = rule_triage(alert, config)
            result = llm_triage(alert, config, baseline)
            print(f"{result.recommendation} {result.score}/10: {alert.title} ({result.source})")
            if result.recommendation == "REVIEW":
                notify(format_notification(alert, result))
        gmail.mark_processed(message.message_id, label)


if __name__ == "__main__":
    run()
