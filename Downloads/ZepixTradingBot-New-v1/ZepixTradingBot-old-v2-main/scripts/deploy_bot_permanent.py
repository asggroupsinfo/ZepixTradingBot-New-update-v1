#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Bot Permanently - Runs until stopped
"""
import sys
import os
import io
import uvicorn
import signal

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def signal_handler(sig, frame):
    print("\n\nBot shutdown requested...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("="*70)
    print("DEPLOYING ZEPIX TRADING BOT v2.0 - PERMANENT MODE")
    print("="*70)
    print("Server: http://0.0.0.0:5000")
    print("Webhook: http://localhost:5000/webhook")
    print("Status: http://localhost:5000/status")
    print("\nBot will run until stopped (Ctrl+C)")
    print("="*70)
    print("\nStarting server...\n")
    
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=5000,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

