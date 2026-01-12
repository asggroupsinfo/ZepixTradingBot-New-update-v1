"""
Telegram Module - V5 Hybrid Plugin Architecture

Multi-Telegram System with 3 specialized bots:
1. Controller Bot - Commands and system control
2. Notification Bot - Trade alerts and notifications
3. Analytics Bot - Reports and statistics

Part of Document 01: Project Overview - Multi-Telegram System
"""

from .multi_telegram_manager import MultiTelegramManager

__all__ = [
    "MultiTelegramManager",
]
