#!/usr/bin/env python3
"""
Property Finder Monitor for Dubai Creek Harbour
Checks for 1BR apartments under 1.8M AED
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional

# Search criteria
CRITERIA = {
    "location": "Creek Harbour",
    "city": "Dubai",
    "bedrooms": 1,
    "max_price": 1_800_000,  # AED
    "min_size": 740,  # sqft
    "status": "ready"  # Not off-plan
}

# PropertyFinder API (web scraping fallback)
PROPERTYFINDER_URL = (
    "https://www.propertyfinder.ae/en/search"
    "?c=1&beds_in=1&fu=0&ob=mr&pf=740&pr=1800000"
    "&q=%22Creek%20Harbour%22&rp=y&t=1"
)

# Storage for seen listings
SEEN_LISTINGS_FILE = "seen_listings.json"


class PropertyMonitor:
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
    
    async def fetch_listings(self) -> List[Dict]:
        """
        Fetch listings from PropertyFinder
        Note: PropertyFinder blocks scraping, so this is a template
        for manual check or API integration
        """
        listings = []
        
        # TODO: Implement actual scraping or use PropertyFinder API if available
        # For now, this is a placeholder that returns empty list
        # In production, you could use:
        # - Playwright/Selenium for browser automation
        # - PropertyFinder API (if they offer one)
        # - Manual entry via Telegram bot
        
        return listings
    
    def filter_new_listings(self, listings: List[Dict]) -> List[Dict]:
        """Filter out already seen listings"""
        new_listings = []
        for listing in listings:
            listing_id = listing.get('id') or listing.get('url')
            if listing_id and listing_id not in self.seen_listings:
                new_listings.append(listing)
                self.seen_listings.add(listing_id)
        
        if new_listings:
            self._save_seen_listings()
        
        return new_listings
    
    def format_notification(self, listing: Dict) -> str:
        """Format listing for Telegram notification"""
        return f"""🏠 **Новое предложение в Creek Harbour!**

💰 **Цена:** {listing.get('price', 'N/A'):,} AED
📐 **Площадь:** {listing.get('size', 'N/A')} sqft
🏢 **Здание:** {listing.get('building', 'N/A')}
🛏️ **Комнаты:** {listing.get('bedrooms', 1)} BR
📍 **Локация:** {listing.get('location', 'Dubai Creek Harbour')}

🔗 [Открыть на PropertyFinder]({listing.get('url', '#')})

⏰ Проверено: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


async def main():
    """Main entry point"""
    monitor = PropertyMonitor()
    
    print(f"[{datetime.now()}] Starting property check...")
    
    listings = await monitor.fetch_listings()
    new_listings = monitor.filter_new_listings(listings)
    
    if new_listings:
        print(f"Found {len(new_listings)} new listings!")
        for listing in new_listings:
            notification = monitor.format_notification(listing)
            print(notification)
            # TODO: Send to Telegram via bot API
    else:
        print("No new listings found.")
    
    print(f"[{datetime.now()}] Check complete.")


if __name__ == "__main__":
    asyncio.run(main())
