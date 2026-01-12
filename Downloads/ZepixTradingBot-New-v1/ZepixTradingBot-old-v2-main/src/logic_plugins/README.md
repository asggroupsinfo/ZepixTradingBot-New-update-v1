# Logic Plugins Directory

Place your custom trading logic plugins here.
Each plugin should be in its own directory with a `plugin.py` file.

## Structure

```
src/logic_plugins/
  ├── my_strategy/
  │   ├── plugin.py
  │   └── config.json (optional)
  └── another_strategy/
      └── plugin.py
```

## Creating a Plugin

Create a class that inherits from `BaseLogicPlugin` in `plugin.py`:

```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin

class MyStrategyPlugin(BaseLogicPlugin):
    async def initialize(self):
        self.log("My Strategy Initialized")

    async def on_signal_received(self, data):
        self.log(f"Received signal: {data}")
        # Return data to continue, False to stop, or modified data
        return data

    async def process_entry_signal(self, evaluation_result):
        # Custom entry logic
        pass
```
