#!/usr/bin/env python3
"""
Wrapper script to run the bot and keep it alive
"""
import sys
import os
import time
import signal
import subprocess
import threading

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

bot_process = None
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    print(f"[WRAPPER] Received signal {signum}, shutting down...")
    shutdown_event.set()
    if bot_process:
        try:
            bot_process.terminate()
            bot_process.wait(timeout=5)
        except:
            bot_process.kill()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_bot():
    """Run the bot process"""
    global bot_process
    
    while not shutdown_event.is_set():
        try:
            print("[WRAPPER] Starting bot process...")
            # Use uvicorn directly for better stability
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "src.main:app", 
                "--host", "127.0.0.1", 
                "--port", "8000",
                "--log-level", "info"
            ]
            
            bot_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
                bufsize=1
            )
            
            # Wait for process to complete
            returncode = bot_process.wait()
            print(f"[WRAPPER] Bot process exited with code {returncode}")
            
            if shutdown_event.is_set():
                break
            
            # If process exited unexpectedly, wait before restarting
            print("[WRAPPER] Waiting 5 seconds before restart...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("[WRAPPER] Interrupted")
            shutdown_event.set()
            break
        except Exception as e:
            print(f"[WRAPPER] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("[WRAPPER] Bot wrapper starting...")
    try:
        run_bot()
    finally:
        print("[WRAPPER] Wrapper shutting down")
