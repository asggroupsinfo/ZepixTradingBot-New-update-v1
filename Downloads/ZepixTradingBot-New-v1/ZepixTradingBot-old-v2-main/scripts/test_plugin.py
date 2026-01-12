import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.plugin_system import PluginRegistry
from typing import Optional

# Mock Alert class for testing
class MockAlert:
    def __init__(self, symbol, signal_type, direction):
        self.symbol = symbol
        self.signal_type = signal_type
        self.direction = direction

async def test_plugin(plugin_id: str):
    """Test a single plugin"""
    
    # Mock config and service API
    config = {
        "plugin_system": {
            "plugin_dir": "src/logic_plugins"
        },
        "plugins": {
            plugin_id: {
                "enabled": True
            }
        }
    }
    
    # Mock ServiceAPI
    class MockServiceAPI:
        pass
        
    mock_service_api = MockServiceAPI()
    
    # Initialize registry
    registry = PluginRegistry(config, mock_service_api)
    
    # Load plugin
    success = registry.load_plugin(plugin_id)
    
    if not success:
        print(f"❌ Failed to load plugin: {plugin_id}")
        return False
    
    print(f"✅ Plugin loaded: {plugin_id}")
    
    # Create dummy entry alert
    entry_alert = MockAlert(
        symbol="XAUUSD",
        signal_type="entry",
        direction="BUY"
    )
    
    # Process entry
    print(f"Testing process_entry_signal...")
    result_entry = await registry.route_alert_to_plugin(entry_alert, plugin_id)
    print(f"Result Entry: {result_entry}")
    
    # Create dummy exit alert
    exit_alert = MockAlert(
        symbol="XAUUSD",
        signal_type="exit",
        direction="BUY"
    )
    
    # Process exit
    print(f"Testing process_exit_signal...")
    result_exit = await registry.route_alert_to_plugin(exit_alert, plugin_id)
    print(f"Result Exit: {result_exit}")

    return True

if __name__ == "__main__":
    plugin_id = sys.argv[1] if len(sys.argv) > 1 else "_template"
    
    try:
        success = asyncio.run(test_plugin(plugin_id))
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error running test_plugin: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
