# Upwork MCP Job Alert Automation

Triage official Upwork job-alert emails every 15 minutes, notify on likely matches,
then run the full Upwork MCP review manually before applying.

## What it does

1. Reads official Upwork job-alert emails through the Gmail API.
2. Extracts job titles and Upwork links from the email.
3. Applies configurable niche, budget, and hard-rejection rules.
4. Optionally uses the OpenAI Responses API for a second-pass judgment.
5. Sends promising matches to Telegram or Slack.
6. Labels processed emails in Gmail to prevent duplicate alerts.

The notification is deliberately marked **preliminary**. Email alerts do not include
enough information to verify client spend, hire rate, payment status, interviews,
invites, or complete hiring history.

## Compliance boundary

This project does **not**:

- scrape Upwork pages
- refresh or poll Upwork in the background
- call the Upwork MCP unattended
- submit proposals or messages
- boost bids or perform account actions

Upwork warns that background job watchers, page monitors, auto-refresh tools, and
idle requests can trigger enforcement. Use Upwork's official alerts for detection,
then perform the full MCP review and proposal submission manually.

- [Upwork automation policy](https://support.upwork.com/hc/en-us/articles/43342677368467-Use-bots-and-other-automation-properly)
- [Upwork instant job alerts](https://support.upwork.com/hc/en-us/articles/36001273797907-How-to-get-instant-job-alerts)

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp config/profile.example.yaml config/profile.yaml
pytest -q
```

Customize `config/profile.yaml` with your positioning, proof, keywords, and budget
floors. The example is ready for Mujtaba's current Agentic AI positioning.

## Gmail setup

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Configure the OAuth consent screen.
4. Create an OAuth client with application type **Desktop app**.
5. Download the file as `client_secret.json` in this repository.
6. Run:

```bash
python scripts/google_oauth.py
```

The command prints a compact authorized-user JSON object. Save the entire value as
the GitHub Actions secret `GMAIL_TOKEN_JSON`. The token uses Gmail's `modify` scope
because the automation adds an `upwork-ai-reviewed` label after processing.

Never commit `client_secret.json` or the generated token.

## OpenAI setup

OpenAI scoring is optional. Without it, deterministic rules still run.

Add the repository secret `OPENAI_API_KEY` and repository variable `OPENAI_MODEL`.
Choose a current model available to your API project. Structured Outputs keep the
classification machine-readable.

## Notifications

Configure at least one channel.

### Telegram

Add these repository secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Slack

Add the repository secret `SLACK_WEBHOOK_URL`.

When neither channel is configured, results are written only to the Actions log.

## GitHub Actions variables

Optional repository variables:

- `AUTOMATION_ENABLED`: set to `true` only after configuration is complete
- `OPENAI_MODEL`: model used for second-pass scoring
- `GMAIL_QUERY`: custom Gmail search query

The default Gmail query is:

```text
from:(upwork.com) newer_than:2d -label:upwork-ai-reviewed
```

Adjust it if your Upwork alert sender or Gmail filtering differs.

The scheduled workflow remains disabled until `AUTOMATION_ENABLED` is set to
`true`, preventing failed runs before the required secrets are configured.

## Review workflow

When the automation sends a `REVIEW` notification:

1. Open the job manually.
2. Run the Upwork MCP five-step gate.
3. Verify worldwide eligibility, qualification, active competition, client quality,
   payment history, and hiring behavior.
4. Classify it as Apply, Consider, or Skip.
5. Draft and submit the proposal manually.

## Local run

```bash
export GMAIL_TOKEN_JSON='{"token":"..."}'
export TELEGRAM_BOT_TOKEN='...'
export TELEGRAM_CHAT_ID='...'
upwork-alert-triage
```

## License

MIT
