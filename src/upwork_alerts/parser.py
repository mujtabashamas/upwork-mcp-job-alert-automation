from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit

from .models import JobAlert

UPWORK_JOB_RE = re.compile(r"https?://(?:www\.)?upwork\.com/(?:jobs|freelance-jobs/apply)/[^\s\"'<>]+")


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._href: str | None = None
        self._text: list[str] = []
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._href = dict(attrs).get("href")
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.anchors.append((self._href, " ".join(self._text).strip()))
            self._href = None
            self._text = []


def normalize_url(url: str) -> str:
    parts = urlsplit(url.rstrip(".,);]"))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def extract_job_alerts(
    message_id: str,
    subject: str,
    text_body: str,
    html_body: str = "",
    received_at: str = "",
) -> list[JobAlert]:
    candidates: list[tuple[str, str]] = []
    if html_body:
        parser = _AnchorParser()
        parser.feed(html_body)
        candidates.extend(
            (normalize_url(url), title)
            for url, title in parser.anchors
            if UPWORK_JOB_RE.match(url)
        )

    candidates.extend((normalize_url(url), "") for url in UPWORK_JOB_RE.findall(text_body))

    unique: dict[str, str] = {}
    for url, title in candidates:
        if url not in unique or (title and not unique[url]):
            unique[url] = clean_title(title)

    fallback_title = clean_title(subject)
    return [
        JobAlert(
            message_id=message_id,
            title=title or fallback_title,
            url=url,
            body=text_body,
            received_at=received_at,
        )
        for url, title in unique.items()
    ]


def clean_title(value: str) -> str:
    value = re.sub(r"^(new job|job alert|upwork job alert)\s*[:\-]\s*", "", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip() or "Upwork job alert"

