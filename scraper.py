#!/usr/bin/env python3
"""
Property Finder Scraper with Stealth Mode
Bypasses bot detection using Playwright + stealth plugins
"""

import os
import json
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Playwright imports
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright_stealth import stealth_async

# Search criteria
CRITERIA = {
    "location": "Creek Harbour",
    "city": "Dubai", 
    "bedrooms": 1,
    "max_price": 1_800_000,
    "min_size": 740,
    "status": "ready"
}

# PropertyFinder search URL
PROPERTYFINDER_URL = (
    "https://www.propertyfinder.ae/en/search"
    "?c=1&beds_in=1&fu=0&ob=mr&pf=740&pr=1800000"
    "&q=%22Creek%20Harbour%22&rp=y&t=1"
)

SEEN_LISTINGS_FILE = "seen_listings.json"


@dataclass
class PropertyListing:
    """Property listing data structure"""
    id: str
    title: str
    price: int
    price_display: str
    size: int
    size_display: str
    bedrooms: int
    bathrooms: int
    building: str
    location: str
    url: str
    image_url: Optional[str] = None
    agent_name: Optional[str] = None
    agent_phone: Optional[str] = None
    listing_date: Optional[str] = None
    scraped_at: str = ""
    
    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


class StealthPropertyScraper:
    """
    PropertyFinder scraper with anti-detection measures
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
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
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
        )
        
        # Create context with realistic viewport and locale
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Asia/Dubai',
            geolocation={'latitude': 25.2048, 'longitude': 55.2708},  # Dubai
            permissions=['geolocation'],
            color_scheme='light',
        )
        
        # Add init script to hide automation
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        """)
        
        self.page = await self.context.new_page()
        
        # Apply stealth mode
        await stealth_async(self.page)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def human_like_delay(self, min_seconds: float = 2, max_seconds: float = 5):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def scroll_page(self):
        """Scroll page like a human"""
        if not self.page:
            return
        
        # Scroll in steps
        for _ in range(random.randint(3, 7)):
            await self.page.mouse.wheel(0, random.randint(300, 800))
            await self.human_like_delay(0.5, 1.5)
    
    async def fetch_listings(self) -> List[PropertyListing]:
        """
        Fetch listings from PropertyFinder with stealth mode
        """
        listings = []
        
        try:
            print(f"[{datetime.now()}] Opening PropertyFinder...")
            
            # Navigate to search page
            response = await self.page.goto(
                PROPERTYFINDER_URL,
                wait_until='networkidle',
                timeout=60000
            )
            
            if response.status != 200:
                print(f"Warning: Got status {response.status}")
            
            # Random delay
            await self.human_like_delay(3, 6)
            
            # Check for CAPTCHA or block
            if await self._is_blocked():
                print("Warning: Possible bot detection triggered")
                return listings
            
            # Scroll to load lazy content
            await self.scroll_page()
            
            # Extract listings
            print(f"[{datetime.now()}] Extracting listings...")
            listings = await self._extract_listings()
            
            print(f"[{datetime.now()}] Found {len(listings)} listings")
            
            # Handle pagination if needed
            current_page = 1
            max_pages = 3  # Limit to avoid too many requests
            
            while current_page < max_pages:
                has_next = await self._has_next_page()
                if not has_next:
                    break
                
                print(f"[{datetime.now()}] Going to page {current_page + 1}...")
                
                if await self._go_to_next_page():
                    await self.human_like_delay(4, 8)
                    await self.scroll_page()
                    
                    page_listings = await self._extract_listings()
                    listings.extend(page_listings)
                    print(f"  Found {len(page_listings)} more listings")
                    
                    current_page += 1
                else:
                    break
            
        except Exception as e:
            print(f"Error fetching listings: {e}")
        
        return listings
    
    async def _is_blocked(self) -> bool:
        """Check if we've been blocked or hit CAPTCHA"""
        try:
            # Check for common block indicators
            page_content = await self.page.content()
            block_indicators = [
                'captcha',
                'robot',
                'blocked',
                'access denied',
                '429',
                'too many requests'
            ]
            
            content_lower = page_content.lower()
            for indicator in block_indicators:
                if indicator in content_lower:
                    return True
            
            # Check if we're on the expected page
            if 'propertyfinder' not in self.page.url:
                return True
            
            return False
        except:
            return True
    
    async def _extract_listings(self) -> List[PropertyListing]:
        """Extract property listings from current page"""
        listings = []
        
        try:
            # Wait for listings to load
            await self.page.wait_for_selector('[data-testid="property-card"]', timeout=10000)
            
            # Extract all cards
            cards = await self.page.query_selector_all('[data-testid="property-card"]')
            
            for card in cards:
                try:
                    listing = await self._parse_card(card)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    print(f"Error parsing card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error extracting listings: {e}")
        
        return listings
    
    async def _parse_card(self, card) -> Optional[PropertyListing]:
        """Parse a single property card"""
        try:
            # Extract price
            price_elem = await card.query_selector('[data-testid="property-price"]')
            price_text = await price_elem.inner_text() if price_elem else ""
            price = self._parse_price(price_text)
            
            # Extract title
            title_elem = await card.query_selector('[data-testid="property-title"]')
            title = await title_elem.inner_text() if title_elem else ""
            
            # Extract size
            size_elem = await card.query_selector('[data-testid="property-area"]')
            size_text = await size_elem.inner_text() if size_elem else ""
            size = self._parse_size(size_text)
            
            # Extract bedrooms/bathrooms
            beds_elem = await card.query_selector('[data-testid="property-beds"]')
            beds_text = await beds_elem.inner_text() if beds_elem else "1"
            beds = self._parse_number(beds_text)
            
            baths_elem = await card.query_selector('[data-testid="property-baths"]')
            baths_text = await baths_elem.inner_text() if baths_elem else "1"
            baths = self._parse_number(baths_text)
            
            # Extract URL
            link_elem = await card.query_selector('a')
            href = await link_elem.get_attribute('href') if link_elem else ""
            url = f"https://www.propertyfinder.ae{href}" if href.startswith('/') else href
            
            # Extract ID from URL
            listing_id = self._extract_id_from_url(url)
            
            # Extract building name from title
            building = self._extract_building(title)
            
            # Extract image
            img_elem = await card.query_selector('img')
            img_url = await img_elem.get_attribute('src') if img_elem else None
            
            return PropertyListing(
                id=listing_id,
                title=title,
                price=price,
                price_display=price_text.strip(),
                size=size,
                size_display=size_text.strip(),
                bedrooms=beds,
                bathrooms=baths,
                building=building,
                location="Dubai Creek Harbour",
                url=url,
                image_url=img_url
            )
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> int:
        """Extract numeric price from text"""
        import re
        # Remove non-numeric characters except dots
        numbers = re.findall(r'[\d,]+', price_text.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return 0
    
    def _parse_size(self, size_text: str) -> int:
        """Extract size in sqft from text"""
        import re
        numbers = re.findall(r'[\d,]+', size_text.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return 0
    
    def _parse_number(self, text: str) -> int:
        """Extract number from text"""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
    
    def _extract_id_from_url(self, url: str) -> str:
        """Extract listing ID from URL"""
        import re
        match = re.search(r'-(\d+)\.html', url)
        return match.group(1) if match else url.split('/')[-1]
    
    def _extract_building(self, title: str) -> str:
        """Extract building name from title"""
        # Common building patterns in Creek Harbour
        buildings = [
            '17 Icon Bay', 'Harbour Gate', 'Dubai Creek Residences',
            'Creek Horizon', 'The Cove', 'Summer', 'Creek Edge',
            'Palace Residences', 'Creek Beach', 'Grove',
            'Lotus', 'Orchid', 'Bayshore'
        ]
        
        for building in buildings:
            if building.lower() in title.lower():
                return building
        
        # Fallback: extract first few words
        words = title.split()[:3]
        return ' '.join(words) if words else "Unknown"
    
    async def _has_next_page(self) -> bool:
        """Check if there's a next page"""
        try:
            next_btn = await self.page.query_selector('[data-testid="pagination-next"]')
            if next_btn:
                is_disabled = await next_btn.get_attribute('disabled')
                return not is_disabled
            return False
        except:
            return False
    
    async def _go_to_next_page(self) -> bool:
        """Navigate to next page"""
        try:
            next_btn = await self.page.query_selector('[data-testid="pagination-next"]')
            if next_btn:
                await next_btn.click()
                await self.page.wait_for_load_state('networkidle')
                return True
            return False
        except Exception as e:
            print(f"Error going to next page: {e}")
            return False
    
    def filter_new_listings(self, listings: List[PropertyListing]) -> List[PropertyListing]:
        """Filter out already seen listings"""
        new_listings = []
        for listing in listings:
            if listing.id not in self.seen_listings:
                # Apply criteria filter
                if (listing.price <= CRITERIA['max_price'] and 
                    listing.size >= CRITERIA['min_size'] and
                    listing.bedrooms == CRITERIA['bedrooms']):
                    new_listings.append(listing)
                    self.seen_listings.add(listing.id)
        
        if new_listings:
            self._save_seen_listings()
        
        return new_listings
    
    def format_notification(self, listing: PropertyListing) -> str:
        """Format listing for Telegram notification"""
        return f"""🏠 **Новое предложение в Creek Harbour!**

💰 **Цена:** {listing.price_display or f'{listing.price:,} AED'}
📐 **Площадь:** {listing.size_display or f'{listing.size} sqft'}
🏢 **Здание:** {listing.building}
🛏️ **Комнаты:** {listing.bedrooms} BR | 🛁 {listing.bathrooms} BA
📍 **Локация:** {listing.location}

🔗 [Открыть на PropertyFinder]({listing.url})

⏰ Проверено: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


async def test_scraper():
    """Test the scraper"""
    async with StealthPropertyScraper(headless=False) as scraper:
        print("Starting scraper test...")
        listings = await scraper.fetch_listings()
        print(f"\nTotal listings found: {len(listings)}")
        
        for i, listing in enumerate(listings[:3], 1):
            print(f"\n--- Listing {i} ---")
            print(f"Title: {listing.title}")
            print(f"Price: {listing.price_display}")
            print(f"Size: {listing.size_display}")
            print(f"Building: {listing.building}")
            print(f"URL: {listing.url}")


if __name__ == "__main__":
    asyncio.run(test_scraper())
