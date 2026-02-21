# Instagram Automation

Automatically scrape posts from source Instagram accounts and re-upload them to a target account. Runs on a daily schedule via GitHub Actions and sends Telegram notifications on success or failure.

## File Structure

```
automation/
├── .github/workflows/
│   └── insta_automation.yml  # Scheduling logic
├── downloads/                # Temp storage for media
├── main.py                   # Entry point
├── scraper.py                # Instaloader logic
├── uploader.py               # Instagrapi logic
├── storage.py                # Excel & History logic
├── notifier.py               # Telegram logic
├── requirements.txt          # Dependencies
├── README.md                 # Setup guide
└── .env.example              # Configuration template
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Pratham5734t/automation.git
cd automation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SOURCE_USERNAME` | Instagram username used for scraping |
| `SOURCE_PASSWORD` | Instagram password used for scraping |
| `TARGET_USERNAME` | Instagram username to upload content to |
| `TARGET_PASSWORD` | Instagram password to upload content to |
| `ACCOUNTS_TO_SCRAPE` | Comma-separated list of accounts to scrape |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (from @BotFather) |
| `TELEGRAM_CHAT_ID` | Telegram chat/channel ID to receive notifications |
| `MAX_POSTS_PER_ACCOUNT` | Maximum posts to process per account per run (default: 5) |
| `HISTORY_FILE` | Path to the Excel history file (default: `history.xlsx`) |

### 4. Run locally

```bash
python main.py
```

## GitHub Actions (Automated Scheduling)

The workflow in `.github/workflows/insta_automation.yml` runs automatically at **08:00 UTC every day**.

Add the following [repository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets):

- `SOURCE_USERNAME`
- `SOURCE_PASSWORD`
- `TARGET_USERNAME`
- `TARGET_PASSWORD`
- `ACCOUNTS_TO_SCRAPE`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

You can also trigger a run manually from the **Actions** tab using the *workflow_dispatch* event.

## How It Works

1. **Scraper** (`scraper.py`) – Uses [Instaloader](https://instaloader.github.io/) to log in and download recent posts (photos, videos, albums) from each account listed in `ACCOUNTS_TO_SCRAPE`.
2. **Storage** (`storage.py`) – Tracks uploaded posts in an Excel file (`history.xlsx`) to avoid re-uploading the same content.
3. **Uploader** (`uploader.py`) – Uses [Instagrapi](https://subzeroid.github.io/instagrapi/) to upload downloaded media to the target Instagram account.
4. **Notifier** (`notifier.py`) – Sends success/failure messages to a Telegram chat via the Bot API.
5. **Main** (`main.py`) – Orchestrates the above modules and logs a summary at the end of each run.