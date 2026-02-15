#!/usr/bin/env python3
"""
Cron-compatible runner for property monitor
Can be run manually or scheduled via cron
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor import PropertyMonitor, CRITERIA


async def send_telegram_notification(bot_token: str, chat_id: str, message: str):
    """Send notification via Telegram"""
    import aiohttp
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return response.status == 200


async def main():
    """Main cron entry point"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notify_on_empty = os.getenv("NOTIFY_ON_EMPTY", "false").lower() == "true"
    
    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required")
        sys.exit(1)
    
    monitor = PropertyMonitor()
    
    print(f"[{datetime.now()}] Checking PropertyFinder...")
    
    try:
        listings = await monitor.fetch_listings()
        new_listings = monitor.filter_new_listings(listings)
        
        if new_listings:
            print(f"Found {len(new_listings)} new listings!")
            for listing in new_listings:
                notification = monitor.format_notification(listing)
                success = await send_telegram_notification(
                    bot_token, chat_id, notification
                )
                if success:
                    print(f"  ✓ Sent notification for {listing.get('id', 'unknown')}")
                else:
                    print(f"  ✗ Failed to send notification")
        else:
            print("No new listings found.")
            if notify_on_empty:
                await send_telegram_notification(
                    bot_token, chat_id,
                    "🏠 Проверка Creek Harbour: новых предложений не найдено."
                )
        
        print(f"[{datetime.now()}] Done.")
        
    except Exception as e:
        print(f"Error: {e}")
        await send_telegram_notification(
            bot_token, chat_id,
            f"⚠️ Ошибка при проверке PropertyFinder: {str(e)[:200]}"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
