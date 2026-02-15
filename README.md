# Property Finder Monitor

Automated monitoring for PropertyFinder.ae listings in Dubai Creek Harbour.

## Search Criteria

- **Location:** Dubai Creek Harbour
- **Type:** 1 bedroom apartment
- **Status:** Ready (resale/secondary market, NOT off-plan)
- **Max Price:** 1,800,000 AED
- **Min Size:** 740 sqft

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

2. Copy `.env.example` to `.env` and fill in:
```bash
cp .env.example .env
```

3. Run manually:
```bash
python monitor.py
```

4. Or run with cron:
```bash
python cron_runner.py
```

## Deployment

### Docker
```bash
docker build -t property-finder-monitor .
docker run -d --env-file .env property-finder-monitor
```

### Systemd Service
```bash
sudo cp property-monitor.service /etc/systemd/system/
sudo systemctl enable property-monitor
sudo systemctl start property-monitor
```

## Features

- Automatic listing detection
- Duplicate filtering (remembers seen listings)
- Telegram notifications
- Docker support
- Cron-compatible
