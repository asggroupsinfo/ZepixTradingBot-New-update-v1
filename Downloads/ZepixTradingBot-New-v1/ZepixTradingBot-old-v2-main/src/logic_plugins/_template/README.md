# Template Plugin

This is a template for creating new trading logic plugins.

## Creating a New Plugin

1. **Copy this directory:**
   ```bash
   cp -r src/logic_plugins/_template src/logic_plugins/my_logic
   ```

2. **Update plugin.py:**
   - Rename class to `MyLogicPlugin`
   - Implement entry/exit/reversal logic
   
3. **Update config.json:**
   - Set `plugin_id` to `my_logic`
   - Configure trading settings
   
4. **Register in main config:**
   ```json
   {
     "plugins": {
       "my_logic": {
         "enabled": true,
         "config_path": "src/logic_plugins/my_logic/config.json"
       }
     }
   }
   ```

5. **Test:**
   ```bash
   python scripts/test_plugin.py my_logic
   ```

## Plugin API

Plugins have access to `service_api` with these services:

- `service_api.order_execution` - Place/close orders
- `service_api.risk_management` - Lot calculations
- `service_api.profit_booking` - Profit booking chains
- `service_api.reentry` - Re-entry systems
- `service_api.telegram` - Send notifications
- `service_api.analytics` - Performance tracking

See PLUGIN_DEVELOPER_GUIDE.md for complete API reference.
