#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start Bot Live with Menu System
"""
import sys
import os
import uvicorn

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 70)
    print("STARTING ZEPIX TRADING BOT v2.0 WITH MENU SYSTEM")
    print("=" * 70)
    print("Server will start on: http://0.0.0.0:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    print("Status endpoint: http://localhost:5000/status")
    print("\n✅ Zero-Typing Menu System: ACTIVE")
    print("✅ /start command: Shows menu with buttons")
    print("✅ /dashboard command: Shows dashboard with menu button")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=5000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        import traceback
        traceback.print_exc()

