from upwork_alerts.models import JobAlert
from upwork_alerts.rules import load_config, rule_triage

CONFIG = load_config("config/profile.example.yaml")


def alert(title: str, body: str) -> JobAlert:
    return JobAlert("m1", title, "https://www.upwork.com/jobs/~01", body)


def test_reviews_focused_voice_ai_job() -> None:
    result = rule_triage(
        alert(
            "Voice AI Engineer",
            "Build a Vapi and Twilio AI receptionist with appointment booking and CRM automation.",
        ),
        CONFIG,
    )

    assert result.recommendation == "REVIEW"
    assert result.lane == "voice_ai"
    assert result.score >= 5


def test_ignores_hard_reject_job() -> None:
    result = rule_triage(alert("Junior AI data entry intern", "Unpaid test required."), CONFIG)

    assert result.recommendation == "IGNORE"
    assert result.score == 0


def test_low_budget_reduces_score() -> None:
    result = rule_triage(
        alert("RAG and document intelligence", "Pinecone RAG build. Budget: $100 fixed-price."),
        CONFIG,
    )

    assert result.score < 5

