# Invite Challenge Bot

Telegram bot for running invite challenges with promo code rewards.

## Project Structure

```
invitebot/
├── main.py          # Bot logic & handlers
├── config.py        # Non-sensitive settings (edit to update promo codes, deadline, brand)
├── sheets.py        # Google Sheets integration
├── messages.py      # All bot messages in EN / IT / FR / ES
├── requirements.txt
├── Procfile         # Railway process definition
└── .gitignore
```

## Railway Environment Variables

Set these in your Railway project under **Variables**:

| Variable | Value |
|---|---|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `ADMIN_ID` | Your Telegram user ID (get from @userinfobot) |
| `GOOGLE_SHEET_ID` | The ID from your Google Sheet URL |
| `GOOGLE_CREDENTIALS_JSON` | The full contents of your service account `.json` file (paste as one line) |

> ⚠️ Never commit these values to GitHub.

## Updating Settings

To change promo codes, deadline, or brand name — edit `config.py` and push to GitHub. Railway will auto-redeploy.

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Select language |
| `invite` | Get unique invite link |
| `/status` | Check invite count & tier |
| `/claim` | Claim promo code |
| `/help` | Show instructions |
| `/adminstats` | (Admin only) View totals |

## Google Sheets Tabs

| Tab | Contents |
|---|---|
| Members | All users, their invite links & counts |
| Claims | Who claimed which promo code |
| Stats | Invite counts (updated live) |
| Config | Promo code values & deadline reference |
