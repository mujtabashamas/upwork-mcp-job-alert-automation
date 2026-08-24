from __future__ import annotations

import os

import requests

from .models import JobAlert, TriageResult


def format_notification(alert: JobAlert, result: TriageResult) -> str:
    risks = f"\nRisks: {'; '.join(result.risks)}" if result.risks else ""
    return (
        f"Upwork job needs review ({result.score}/10)\n\n"
        f"{alert.title}\n"
        f"Lane: {result.lane}\n"
        f"Why: {result.reason}\n"
        f"Proof: {result.proof or 'Select during the full review.'}"
        f"{risks}\n\n"
        f"{alert.url}\n\n"
        "Preliminary match only. Run the manual Upwork MCP five-step gate before applying."
    )


def notify(message: str) -> None:
    sent = False
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_token and telegram_chat:
        response = requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={"chat_id": telegram_chat, "text": message, "disable_web_page_preview": True},
            timeout=20,
        )
        response.raise_for_status()
        sent = True

    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    if slack_webhook:
        response = requests.post(slack_webhook, json={"text": message}, timeout=20)
        response.raise_for_status()
        sent = True

    if not sent:
        print(message)

