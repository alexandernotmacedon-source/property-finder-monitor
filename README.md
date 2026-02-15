# Property Finder Monitor

Automated monitoring for PropertyFinder.ae listings in Dubai Creek Harbour.

## ⚠️ Important: Manual Checking Required

PropertyFinder.ae has strong anti-bot protection that blocks automated scraping. This project uses a **hybrid approach**:

- **Automated**: Cron job triggers every 4 hours
- **Manual**: AI agent checks the website manually via browser
- **Notifications**: New listings sent to Telegram bot @Property_Dubai_bot

## Search Criteria

- **Location:** Dubai Creek Harbour
- **Type:** 1 bedroom apartment (1BR)
- **Status:** Ready (resale/secondary market, NOT off-plan)
- **Max Price:** 1,800,000 AED
- **Min Size:** 740 sqft

## How It Works

1. **Every 4 hours** OpenClaw cron job wakes up
2. **AI agent** opens PropertyFinder in browser
3. **Checks** for new 1BR listings matching criteria
4. **Sends** Telegram notification if new listing found
5. **Tracks** seen listings to avoid duplicates

## Quick Links

- **Search URL:** https://www.propertyfinder.ae/en/search?c=1&beds_in=1&fu=0&ob=mr&pf=740&pr=1800000&q=%22Creek%20Harbour%22&rp=y&t=1
- **Telegram Bot:** @Property_Dubai_bot
- **Notifications to:** Chat ID 440261312

## Configuration

### Environment Variables

Create `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
NOTIFY_ON_EMPTY=false
```

### Getting Credentials

1. **Bot Token**: Message @BotFather → /newbot → copy token
2. **Chat ID**: Message @userinfobot → copy your ID

## Files

```
property-finder-monitor/
├── monitor.py          # Helper script for tracking seen listings
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration (not committed)
├── .env.example       # Environment template
├── seen_listings.json # Database of seen listings (auto-created)
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## Usage

### Manual Test

```bash
# Install dependencies
pip install -r requirements.txt

# Run helper script
python monitor.py
```

### Check Search URL Manually

Open this URL in browser:
```
https://www.propertyfinder.ae/en/search?c=1&beds_in=1&fu=0&ob=mr&pf=740&pr=1800000&q=%22Creek%20Harbour%22&rp=y&t=1
```

Look for:
- ✅ 1 bedroom
- ✅ Ready status (not off-plan)
- ✅ Price ≤ 1,800,000 AED
- ✅ Size ≥ 740 sqft

## Cron Schedule

Current schedule: **Every 4 hours**

Managed by OpenClaw cron jobs:
- Job ID: `9fee7622-3414-463b-b764-b6a0b7143a3f`
- Status: Active
- Next run: Automatic

## Last Found Listing

**17 Icon Bay**
- Price: 1,800,000 AED
- Size: 765 sqft
- Status: Ready (Resale)
- Date Found: 2026-02-15

## Troubleshooting

### No notifications received

1. Check bot @Property_Dubai_bot is running
2. Verify TELEGRAM_CHAT_ID is correct
3. Check if bot is blocked

### PropertyFinder shows CAPTCHA

This is expected. The AI agent handles this manually.

## Why Not Automated Scraping?

PropertyFinder uses:
- Cloudflare protection
- Rate limiting
- Bot detection
- CAPTCHA challenges

All automated scraping attempts return 403 Forbidden.

## License

MIT
