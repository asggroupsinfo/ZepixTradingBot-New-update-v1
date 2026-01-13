"""
Main Entry Point for Zepix Trading Bot V5
==========================================

This module initializes all core services and wires them together:
- VoiceAlertService: Voice notifications for trades
- ForexSessionManager: Session-based trading restrictions
- NotificationRouter: Multi-channel notification delivery
- DatabaseManager: Multi-DB routing for V3/V6 plugins

Author: Zepix Trading Bot Development Team
Version: 5.0
Created: 2026-01-12
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Core imports
from src.config import Config
from src.core.plugin_system.service_api import ServiceAPI

# Service imports
from src.modules.session_manager import SessionManager
from src.services.voice_alert_service import VoiceAlertService
from src.telegram.notification_system import NotificationRouter
from src.core.database_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceInitializer:
    """
    Initializes and wires all V5 services to the ServiceAPI.
    
    This class is responsible for:
    1. Creating service instances
    2. Wiring them to ServiceAPI class-level variables
    3. Providing health checks for all services
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the service initializer.
        
        Args:
            config: Optional Config instance (creates new if not provided)
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Service instances
        self._voice_service: Optional[VoiceAlertService] = None
        self._session_manager: Optional[SessionManager] = None
        self._notification_router: Optional[NotificationRouter] = None
        self._database_manager: Optional[DatabaseManager] = None
        
        self._initialized = False
    
    async def initialize_all_services(
        self,
        telegram_bot=None,
        voice_system=None
    ) -> bool:
        """
        Initialize all V5 services and wire them to ServiceAPI.
        
        Args:
            telegram_bot: Optional TelegramBot instance for notifications
            voice_system: Optional VoiceAlertSystem instance
            
        Returns:
            bool: True if all services initialized successfully
        """
        try:
            self.logger.info("Initializing V5 Services...")
            
            # 1. Initialize Session Manager
            self._session_manager = SessionManager(
                config_path=self.config.get("session_config_path", "data/session_settings.json")
            )
            self.logger.info("Session Manager initialized")
            
            # 2. Initialize Voice Alert Service
            self._voice_service = VoiceAlertService(
                voice_system=voice_system,
                config=self.config.get("voice_config", {})
            )
            self.logger.info("Voice Alert Service initialized")
            
            # 3. Initialize Notification Router
            self._notification_router = NotificationRouter(
                telegram_manager=telegram_bot,
                voice_service=self._voice_service,
                config=self.config.get("notification_config", {})
            )
            self.logger.info("Notification Router initialized")
            
            # 4. Initialize Database Manager
            v3_db_path = self.config.get("v3_database_path", "data/zepix_combined_v3.db")
            v6_db_path = self.config.get("v6_database_path", "data/zepix_price_action.db")
            self._database_manager = DatabaseManager(
                v3_path=v3_db_path,
                v6_path=v6_db_path
            )
            self.logger.info("Database Manager initialized")
            
            # 5. Wire services to ServiceAPI
            self._wire_services_to_api()
            
            self._initialized = True
            self.logger.info("All V5 Services initialized and wired successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _wire_services_to_api(self):
        """Wire all service instances to ServiceAPI class-level variables."""
        ServiceAPI._voice_service = self._voice_service
        ServiceAPI._session_manager = self._session_manager
        ServiceAPI._notification_router = self._notification_router
        ServiceAPI._database_manager = self._database_manager
        
        self.logger.info("Services wired to ServiceAPI:")
        self.logger.info(f"  - voice_service: {type(self._voice_service).__name__}")
        self.logger.info(f"  - session_manager: {type(self._session_manager).__name__}")
        self.logger.info(f"  - notification_router: {type(self._notification_router).__name__}")
        self.logger.info(f"  - database_manager: {type(self._database_manager).__name__}")
    
    def get_health_status(self) -> dict:
        """
        Get health status of all services.
        
        Returns:
            dict: Health status for each service
        """
        status = {
            "initialized": self._initialized,
            "services": {}
        }
        
        # Voice Service
        if self._voice_service:
            status["services"]["voice_alert"] = {
                "status": "healthy",
                "statistics": self._voice_service.get_statistics()
            }
        else:
            status["services"]["voice_alert"] = {"status": "not_initialized"}
        
        # Session Manager
        if self._session_manager:
            status["services"]["session_manager"] = {
                "status": "healthy",
                "current_session": self._session_manager.get_current_session(),
                "master_switch": self._session_manager.config.get("master_switch", True)
            }
        else:
            status["services"]["session_manager"] = {"status": "not_initialized"}
        
        # Notification Router
        if self._notification_router:
            status["services"]["notification_router"] = {
                "status": "healthy",
                "statistics": self._notification_router.get_statistics()
            }
        else:
            status["services"]["notification_router"] = {"status": "not_initialized"}
        
        # Database Manager
        if self._database_manager:
            status["services"]["database_manager"] = {
                "status": "healthy",
                "health_check": self._database_manager.health_check()
            }
        else:
            status["services"]["database_manager"] = {"status": "not_initialized"}
        
        return status
    
    @property
    def voice_service(self) -> Optional[VoiceAlertService]:
        """Get Voice Alert Service instance."""
        return self._voice_service
    
    @property
    def session_manager(self) -> Optional[SessionManager]:
        """Get Session Manager instance."""
        return self._session_manager
    
    @property
    def notification_router(self) -> Optional[NotificationRouter]:
        """Get Notification Router instance."""
        return self._notification_router
    
    @property
    def database_manager(self) -> Optional[DatabaseManager]:
        """Get Database Manager instance."""
        return self._database_manager


# Global service initializer instance
_service_initializer: Optional[ServiceInitializer] = None


def get_service_initializer() -> ServiceInitializer:
    """
    Get or create the global ServiceInitializer instance.
    
    Returns:
        ServiceInitializer: The global service initializer
    """
    global _service_initializer
    if _service_initializer is None:
        _service_initializer = ServiceInitializer()
    return _service_initializer


async def initialize_v5_services(
    config: Optional[Config] = None,
    telegram_bot=None,
    voice_system=None
) -> bool:
    """
    Convenience function to initialize all V5 services.
    
    This should be called during bot startup, after TelegramBot
    and VoiceAlertSystem are created but before TradingEngine.
    
    Args:
        config: Optional Config instance
        telegram_bot: TelegramBot instance
        voice_system: VoiceAlertSystem instance
        
    Returns:
        bool: True if initialization successful
    """
    global _service_initializer
    _service_initializer = ServiceInitializer(config)
    return await _service_initializer.initialize_all_services(
        telegram_bot=telegram_bot,
        voice_system=voice_system
    )


def get_v5_health_status() -> dict:
    """
    Get health status of all V5 services.
    
    Returns:
        dict: Health status for each service
    """
    if _service_initializer:
        return _service_initializer.get_health_status()
    return {"initialized": False, "services": {}}


# Entry point for standalone testing
if __name__ == "__main__":
    async def test_initialization():
        """Test service initialization."""
        print("Testing V5 Service Initialization...")
        
        success = await initialize_v5_services()
        
        if success:
            print("All services initialized successfully!")
            health = get_v5_health_status()
            print(f"Health Status: {health}")
        else:
            print("Service initialization failed!")
            
    asyncio.run(test_initialization())
