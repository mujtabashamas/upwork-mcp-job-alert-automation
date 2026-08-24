from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def main() -> None:
    credentials_file = Path("client_secret.json")
    if not credentials_file.exists():
        raise SystemExit("Place your Google OAuth desktop credentials at client_secret.json first.")

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
    credentials = flow.run_local_server(port=0)
    print(json.dumps(json.loads(credentials.to_json()), separators=(",", ":")))


if __name__ == "__main__":
    main()

