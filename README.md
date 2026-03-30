# Fleet Report Bot

Telegram bot for fleet reporting based on Google Sheets.

## Features
- reply keyboard fixed at the bottom with:
  - `📊 Raport`
  - `🔧 Serwis samochodów`
- full report from sheets:
  - `Toyoty`
  - `rowery`
  - `skutery`
  - `CITI`
- counts statuses from column `F`
- reads update date from `G1`
- weekly auto-report every Tuesday at 10:00 Europe/Warsaw
- access control from sheet `users`

## Users sheet format
Create a sheet named `users` with columns:

```text
telegram_id\trole\tactive
5643220428\tadmin\tTRUE
```

Only users with `active = TRUE` can use the bot.

## Install
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Files you need
Put your Google service account file in the project root:

```text
service_account.json
```

## Run
```bash
export BOT_TOKEN="YOUR_BOT_TOKEN"
python3 bot.py
```

Or use variables from `.env.example` in your deployment environment.

## Git quick push
```bash
git init
git add .
git commit -m "Initial fleet report bot"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main --force
```
