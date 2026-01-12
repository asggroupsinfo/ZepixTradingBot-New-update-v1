#!/usr/bin/env python3
"""
Standalone bot launcher - runs without web server
"""
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import lifespan, app

async def run_bot():
    """Run bot in standalone mode"""
    print("="*70)
    print("ZEPIX TRADING BOT - STANDALONE MODE")
    print("="*70)
    
    bot_running = True
    
    while bot_running:
        try:
            async with lifespan(app):
                # Keep the bot running indefinitely
                print("\n[STANDALONE] Bot is running. Press Ctrl+C to stop.\n")
                try:
                    while True:
                        await asyncio.sleep(3600)  # Check every hour
                except KeyboardInterrupt:
                    print("\n[STANDALONE] Received Ctrl+C, shutting down...")
                    bot_running = False
                except asyncio.CancelledError:
                    print("\n[STANDALONE] Task cancelled - attempting restart in 5 seconds...")
                    await asyncio.sleep(5)
                    if bot_running:
                        print("[STANDALONE] Restarting bot...")
                        continue
        except KeyboardInterrupt:
            print("\n[INFO] Bot stopped by user")
            bot_running = False
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            if bot_running:
                print("[STANDALONE] Restarting in 10 seconds...")
                await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n[INFO] Shutdown complete")
