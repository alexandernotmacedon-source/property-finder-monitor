#!/usr/bin/env python3
"""
Property Finder Monitor - Manual Check Helper
This script helps track seen listings but requires manual browser checks.
PropertyFinder.ae blocks automated scraping, so we use manual checks via cron jobs.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

# Search criteria
CRITERIA = {
    "location": "Dubai Creek Harbour",
    "bedrooms": 1,
    "max_price": 1_800_000,  # AED
    "min_size": 740,  # sqft
    "status": "ready"
}

SEEN_LISTINGS_FILE = "seen_listings.json"


class PropertyListing:
    """Simple property listing"""
    def __init__(self, listing_id: str, title: str, price: int, size: int, 
                 building: str, url: str, **kwargs):
        self.id = listing_id
        self.title = title
        self.price = price
        self.size = size
        self.building = building
        self.url = url
        self.scraped_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "size": self.size,
            "building": self.building,
            "url": self.url,
            "scraped_at": self.scraped_at
        }


class ManualPropertyMonitor:
    """
    Manual property monitor - tracks seen listings
    Actual checking is done manually via browser + cron jobs
    """
    
    def __init__(self):
        self.seen_listings = self._load_seen_listings()
    
    def _load_seen_listings(self) -> set:
        """Load previously seen listing IDs"""
        if os.path.exists(SEEN_LISTINGS_FILE):
            with open(SEEN_LISTINGS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('listings', []))
        return set()
    
    def _save_seen_listings(self):
        """Save seen listing IDs"""
        with open(SEEN_LISTINGS_FILE, 'w') as f:
            json.dump({
                'listings': list(self.seen_listings),
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def add_listing(self, listing_id: str) -> bool:
        """Add a listing to seen list"""
        if listing_id not in self.seen_listings:
            self.seen_listings.add(listing_id)
            self._save_seen_listings()
            return True
        return False
    
    def is_new(self, listing_id: str) -> bool:
        """Check if listing is new"""
        return listing_id not in self.seen_listings
    
    def format_notification(self, price: int, size: int, building: str, url: str) -> str:
        """Format a notification message"""
        return f"""🏠 **Новое предложение в Creek Harbour!**

💰 **Цена:** {price:,} AED
📐 **Площадь:** {size} sqft
🏢 **Здание:** {building}
🛏️ **Комнаты:** 1 BR
📍 **Локация:** Dubai Creek Harbour

🔗 [Открыть на PropertyFinder]({url})

⏰ Найдено: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


async def send_telegram_notification(bot_token: str, chat_id: str, message: str) -> bool:
    """Send notification via Telegram"""
    import aiohttp
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False


async def main():
    """Example usage"""
    monitor = ManualPropertyMonitor()
    
    # Example: Add a new listing
    listing_id = "example-123"
    if monitor.is_new(listing_id):
        monitor.add_listing(listing_id)
        notification = monitor.format_notification(
            price=1750000,
            size=780,
            building="17 Icon Bay",
            url="https://www.propertyfinder.ae/en/plp/example"
        )
        print(notification)
        
        # Send to Telegram (if configured)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if bot_token and chat_id:
            await send_telegram_notification(bot_token, chat_id, notification)


if __name__ == "__main__":
    print("Property Finder Monitor - Manual Check Helper")
    print("=" * 50)
    print(f"Criteria: {CRITERIA['bedrooms']}BR, max {CRITERIA['max_price']:,} AED, min {CRITERIA['min_size']} sqft")
    print(f"Location: {CRITERIA['location']}")
    print()
    print("Note: This script tracks seen listings.")
    print("Actual monitoring is done via OpenClaw cron jobs every 4 hours.")
    print()
    print(f"Search URL: https://www.propertyfinder.ae/en/search?c=1&beds_in=1&fu=0&ob=mr&pf=740&pr=1800000&q=%22Creek%20Harbour%22&rp=y&t=1")
