import sys
import inspect
import os

# Add current directory to path just in case
sys.path.insert(0, os.getcwd())

try:
    from src.clients.telegram_bot import TelegramBot
    print("--- DIAGNOSTIC START ---")
    print(f"CWD: {os.getcwd()}")
    print(f"Python Executable: {sys.executable}")
    
    file_path = inspect.getfile(TelegramBot)
    print(f"TelegramBot File: {file_path}")

    print("--- SOURCE OF handle_start ---")
    try:
        source = inspect.getsource(TelegramBot.handle_start)
        print(source[:1000]) # First 1000 chars to cover the method
    except Exception as e:
        print(f"Could not get source: {e}")

    print("--- DIAGNOSTIC END ---")

except ImportError as e:
    print(f"Import Error: {e}")
    # Try finding it
    import glob
    print("Searching for telegram_bot.py:")
    print(glob.glob("**/telegram_bot.py", recursive=True))
