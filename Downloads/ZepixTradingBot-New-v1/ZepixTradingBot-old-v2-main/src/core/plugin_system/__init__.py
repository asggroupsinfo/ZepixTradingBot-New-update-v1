"""
Plugin system for Zepix Trading Bot.

Enables multiple independent trading logics to coexist.
"""

from .base_plugin import BaseLogicPlugin
from .plugin_registry import PluginRegistry

__all__ = ["BaseLogicPlugin", "PluginRegistry"]
