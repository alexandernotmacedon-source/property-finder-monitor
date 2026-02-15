#!/usr/bin/env python3
"""
Cron-compatible runner for property monitor
Uses StealthPropertyScraper with Playwright
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import StealthPropertyScraper, CRITERIA


async def send_telegram_notification(bot_token: str, chat_id: str, message: str) -> bool:
    """Send notification via Telegram Bot API"""
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
                if response.status == 200:
                    result = await response.json()
                    return result.get('ok', False)
                else:
                    print(f"Telegram API error: {response.status}")
                    return False
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False


async def main():
    """Main cron entry point"""
    parser = argparse.ArgumentParser(description='Property Finder Monitor')
    parser.add_argument('--headless', action='store_true', default=True, 
                        help='Run browser in headless mode')
    parser.add_argument('--visible', action='store_true',
                        help='Show browser window (for debugging)')
    parser.add_argument('--test', action='store_true',
                        help='Test mode - print listings but dont notify')
    args = parser.parse_args()
    
    headless = not args.visible if args.visible else args.headless
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notify_on_empty = os.getenv("NOTIFY_ON_EMPTY", "false").lower() == "true"
    
    if not args.test and (not bot_token or not chat_id):
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required")
        print("Set them as environment variables or in .env file")
        sys.exit(1)
    
    print(f"[{datetime.now()}] Starting PropertyFinder check...")
    print(f"Criteria: {CRITERIA['bedrooms']}BR, max {CRITERIA['max_price']:,} AED, min {CRITERIA['min_size']} sqft")
    
    try:
        async with StealthPropertyScraper(headless=headless) as scraper:
            # Fetch listings
            listings = await scraper.fetch_listings()
            
            # Filter new listings
            new_listings = scraper.filter_new_listings(listings)
            
            print(f"\n[{datetime.now()}] Results:")
            print(f"  Total listings found: {len(listings)}")
            print(f"  New matching listings: {len(new_listings)}")
            
            if new_listings:
                print(f"\n🎉 Found {len(new_listings)} new properties!")
                
                for listing in new_listings:
                    notification = scraper.format_notification(listing)
                    
                    if args.test:
                        print("\n--- Test Mode: Notification would be ---")
                        print(notification)
                        print("--- End ---\n")
                    else:
                        success = await send_telegram_notification(
                            bot_token, chat_id, notification
                        )
                        if success:
                            print(f"  ✓ Sent notification for {listing.building} - {listing.price_display}")
                        else:
                            print(f"  ✗ Failed to send notification for {listing.id}")
                        
                        # Small delay between messages
                        await asyncio.sleep(1)
            
            else:
                print("\nNo new listings matching criteria.")
                
                if notify_on_empty and not args.test:
                    await send_telegram_notification(
                        bot_token, chat_id,
                        "🏠 Проверка Creek Harbour: новых предложений под критерии не найдено."
                    )
        
        print(f"[{datetime.now()}] Check complete.")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при проверке PropertyFinder: {str(e)}"
        print(error_msg)
        
        if not args.test:
            await send_telegram_notification(bot_token, chat_id, error_msg)
        
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
