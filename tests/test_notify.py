from __future__ import annotations

import importlib

notifications = importlib.import_module("upwork_alerts.notify")


class FakeResponse:
    def raise_for_status(self) -> None:
        return None


def clear_notification_env(monkeypatch) -> None:
    for name in (
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "SLACK_WEBHOOK_URL",
        "DISCORD_WEBHOOK_URL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_sends_slack_webhook(monkeypatch) -> None:
    clear_notification_env(monkeypatch)
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/example")
    calls = []
    monkeypatch.setattr(
        notifications.requests,
        "post",
        lambda url, **kwargs: calls.append((url, kwargs)) or FakeResponse(),
    )

    notifications.notify("Review this job")

    assert calls[0][0] == "https://hooks.slack.test/example"
    assert calls[0][1]["json"] == {"text": "Review this job"}


def test_sends_discord_webhook(monkeypatch) -> None:
    clear_notification_env(monkeypatch)
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.test/webhook")
    calls = []
    monkeypatch.setattr(
        notifications.requests,
        "post",
        lambda url, **kwargs: calls.append((url, kwargs)) or FakeResponse(),
    )

    notifications.notify("Review this job")

    assert calls[0][0] == "https://discord.test/webhook"
    assert calls[0][1]["json"] == {"content": "Review this job"}
