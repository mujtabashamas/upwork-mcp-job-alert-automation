from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from email.header import decode_header, make_header
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


@dataclass(frozen=True)
class GmailMessage:
    message_id: str
    subject: str
    text_body: str
    html_body: str
    received_at: str


class GmailClient:
    def __init__(self) -> None:
        token_json = os.environ["GMAIL_TOKEN_JSON"]
        credentials = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
        self.service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def fetch_unprocessed(self, query: str, limit: int = 20) -> list[GmailMessage]:
        response = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=limit)
            .execute()
        )
        return [self._get_message(item["id"]) for item in response.get("messages", [])]

    def mark_processed(self, message_id: str, label_name: str) -> None:
        label_id = self._get_or_create_label(label_name)
        (
            self.service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"addLabelIds": [label_id]})
            .execute()
        )

    def _get_message(self, message_id: str) -> GmailMessage:
        message = (
            self.service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        headers = {
            header["name"].lower(): header["value"]
            for header in message.get("payload", {}).get("headers", [])
        }
        subject = str(make_header(decode_header(headers.get("subject", "Upwork job alert"))))
        text_body, html_body = _extract_bodies(message.get("payload", {}))
        return GmailMessage(
            message_id=message_id,
            subject=subject,
            text_body=text_body or message.get("snippet", ""),
            html_body=html_body,
            received_at=headers.get("date", ""),
        )

    def _get_or_create_label(self, name: str) -> str:
        labels = self.service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"] == name:
                return label["id"]
        created = (
            self.service.users()
            .labels()
            .create(
                userId="me",
                body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"},
            )
            .execute()
        )
        return created["id"]


def _extract_bodies(payload: dict[str, Any]) -> tuple[str, str]:
    text_parts: list[str] = []
    html_parts: list[str] = []

    def walk(part: dict[str, Any]) -> None:
        mime_type = part.get("mimeType", "")
        data = part.get("body", {}).get("data")
        if data:
            decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode(
                "utf-8", errors="replace"
            )
            if mime_type == "text/plain":
                text_parts.append(decoded)
            elif mime_type == "text/html":
                html_parts.append(decoded)
        for child in part.get("parts", []):
            walk(child)

    walk(payload)
    return "\n".join(text_parts), "\n".join(html_parts)

