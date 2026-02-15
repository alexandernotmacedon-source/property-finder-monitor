# Property Finder Monitor

Automated monitoring for PropertyFinder.ae listings in Dubai Creek Harbour.
Uses Playwright with stealth mode to bypass bot detection.

## Search Criteria

- **Location:** Dubai Creek Harbour
- **Type:** 1 bedroom apartment (1BR)
- **Status:** Ready (resale/secondary market, NOT off-plan)
- **Max Price:** 1,800,000 AED
- **Min Size:** 740 sqft

## Features

- ✅ **Stealth Mode**: Playwright + stealth plugins to bypass bot detection
- ✅ **Human-like Behavior**: Random delays, realistic scrolling, proper viewport
- ✅ **Duplicate Filtering**: Remembers seen listings in `seen_listings.json`
- ✅ **Pagination Support**: Checks multiple pages
- ✅ **Telegram Notifications**: Instant alerts for new properties
- ✅ **Docker Support**: Easy deployment

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Telegram bot token and chat ID
```

### 3. Run Test (Visible Browser)

```bash
python cron_runner.py --visible --test
```

### 4. Run Production (Headless)

```bash
python cron_runner.py
```

## Usage

### Manual Run

```bash
# Headless mode (production)
python cron_runner.py

# Visible browser (debugging)
python cron_runner.py --visible

# Test mode (no Telegram notifications)
python cron_runner.py --visible --test
```

### Cron Schedule

Add to crontab (every 4 hours):

```bash
0 */4 * * * cd /path/to/property-finder-monitor && /usr/bin/python3 cron_runner.py >> /var/log/property-monitor.log 2>&1
```

Or use the provided systemd service.

## Docker Deployment

### Build

```bash
docker build -t property-finder-monitor .
```

### Run

```bash
docker run -d \
  --env-file .env \
  -v $(pwd)/seen_listings.json:/app/seen_listings.json \
  property-finder-monitor
```

### Docker Compose

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token (from @BotFather) | Required |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | Required |
| `NOTIFY_ON_EMPTY` | Send notification even if no listings found | `false` |
| `MAX_PRICE` | Maximum price in AED | `1800000` |
| `MIN_SIZE` | Minimum size in sqft | `740` |

### Getting Telegram Chat ID

1. Message @userinfobot on Telegram
2. It will reply with your chat ID

## Architecture

```
property-finder-monitor/
├── scraper.py          # Main scraper with stealth mode
├── cron_runner.py      # CLI runner with Telegram integration
├── monitor.py          # Simple monitor (legacy)
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker image
├── docker-compose.yml # Docker Compose config
├── .env.example       # Environment template
├── .gitignore         # Git ignore rules
└── seen_listings.json # Database of seen listings (auto-created)
```

## Anti-Detection Measures

The scraper uses multiple techniques to avoid detection:

1. **Stealth Mode**: `playwright-stealth` patches automation indicators
2. **Realistic Viewport**: Full HD resolution, proper color scheme
3. **Human-like Delays**: Random delays between actions (2-8 seconds)
4. **Natural Scrolling**: Gradual page scrolling with pauses
5. **Geolocation**: Dubai coordinates and timezone
6. **Browser Args**: Disables automation flags that detectors look for

## Troubleshooting

### CAPTCHA / Blocked

- Increase delays in `scraper.py` (`human_like_delay`)
- Use `--visible` mode to see what's happening
- Check if IP is rate-limited (wait 1 hour)
- Consider using residential proxy

### No Listings Found

- Check if selectors changed (inspect PropertyFinder HTML)
- Verify search URL is correct
- Use `--visible --test` to debug

### Playwright Not Installed

```bash
playwright install chromium
# Or for all browsers:
playwright install
```

## Legal Notice

This tool is for personal use only. Respect PropertyFinder's Terms of Service and robots.txt. Use reasonable request rates (max once per hour recommended).

## License

MIT
