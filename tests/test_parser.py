from upwork_alerts.parser import extract_job_alerts, normalize_url


def test_extracts_job_anchor_and_removes_tracking_query() -> None:
    html = """
    <a href="https://www.upwork.com/jobs/~012345?source=alert">AI Voice Agent Engineer</a>
    """
    alerts = extract_job_alerts("m1", "New jobs", "", html)

    assert len(alerts) == 1
    assert alerts[0].title == "AI Voice Agent Engineer"
    assert alerts[0].url == "https://www.upwork.com/jobs/~012345"


def test_normalize_url_removes_query_and_fragment() -> None:
    assert normalize_url("https://www.upwork.com/jobs/~01abc?x=1#top") == (
        "https://www.upwork.com/jobs/~01abc"
    )

