# Upwork MCP Job Alert Automation

Checks official Upwork alert emails every 15 minutes and notifies you when a job
looks relevant.

It reads email only. It does not scrape Upwork, auto-apply, send proposals, or run
the Upwork MCP in the background.

## Setup

### 1. Get a Gmail token

In Google Cloud:

1. Enable the Gmail API.
2. Create **Desktop app** OAuth credentials.
3. Download them as `client_secret.json` into this folder.

Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
python scripts/google_oauth.py
```

Copy the JSON printed by the last command.

### 2. Add GitHub secrets

Open the repository's **Settings > Secrets and variables > Actions**.

Required:

```text
GMAIL_TOKEN_JSON
```

Choose at least one notification channel:

```text
DISCORD_WEBHOOK_URL
SLACK_WEBHOOK_URL
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Optional AI scoring:

```text
OPENAI_API_KEY
```

### 3. Turn it on

Add these GitHub Actions variables:

```text
AUTOMATION_ENABLED=true
OPENAI_MODEL=your-model-name
```

`OPENAI_MODEL` is only needed when `OPENAI_API_KEY` is configured.

Done. GitHub Actions now checks every 15 minutes. You can run it immediately from
**Actions > Triage Upwork job alerts > Run workflow**.

## Change the matching rules

Edit [`config/profile.example.yaml`](config/profile.example.yaml) to change keywords,
minimum budgets, rejected job types, and portfolio proof.

## After an alert

Open the job, run the full Upwork MCP check, and submit manually. Email cannot verify
client history, hire rate, interviews, invites, or payment status.

## Test

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
```

## License

MIT
