"""
Documentation Generator for V5 Hybrid Plugin Architecture.

This module provides automated documentation generation:
- API documentation from code
- User guide generation
- Admin guide generation
- Plugin developer guide generation
- Troubleshooting guide generation

Based on Document 14: USER_DOCUMENTATION.md

Version: 1.0
Date: 2026-01-12
"""

import os
import ast
import inspect
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import json


class DocType(Enum):
    """Documentation types."""
    USER_GUIDE = "user_guide"
    ADMIN_GUIDE = "admin_guide"
    DEVELOPER_GUIDE = "developer_guide"
    API_REFERENCE = "api_reference"
    TROUBLESHOOTING = "troubleshooting"
    PLUGIN_GUIDE = "plugin_guide"
    ARCHITECTURE = "architecture"


class DocFormat(Enum):
    """Documentation output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    RST = "rst"
    PDF = "pdf"


@dataclass
class DocSection:
    """A section in documentation."""
    title: str
    content: str
    level: int = 1
    subsections: List['DocSection'] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert section to markdown."""
        lines = []
        heading = "#" * self.level
        lines.append(f"{heading} {self.title}")
        lines.append("")
        if self.content:
            lines.append(self.content)
            lines.append("")
        
        for subsection in self.subsections:
            lines.append(subsection.to_markdown())
        
        return "\n".join(lines)


@dataclass
class DocPage:
    """A documentation page."""
    title: str
    doc_type: DocType
    sections: List[DocSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_markdown(self) -> str:
        """Convert page to markdown."""
        lines = [
            f"# {self.title}",
            "",
            f"**Version:** {self.metadata.get('version', '1.0')}",
            f"**Date:** {self.created_at.strftime('%Y-%m-%d')}",
            f"**Type:** {self.doc_type.value.replace('_', ' ').title()}",
            "",
            "---",
            "",
        ]
        
        for section in self.sections:
            lines.append(section.to_markdown())
        
        return "\n".join(lines)


@dataclass
class FunctionDoc:
    """Documentation for a function."""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, str]] = field(default_factory=list)
    returns: str = ""
    raises: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown."""
        lines = [
            f"### `{self.name}`",
            "",
            f"```python",
            f"{self.signature}",
            f"```",
            "",
        ]
        
        if self.docstring:
            lines.append(self.docstring)
            lines.append("")
        
        if self.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            for param in self.parameters:
                lines.append(f"- `{param['name']}` ({param.get('type', 'Any')}): {param.get('description', '')}")
            lines.append("")
        
        if self.returns:
            lines.append(f"**Returns:** {self.returns}")
            lines.append("")
        
        if self.raises:
            lines.append("**Raises:**")
            lines.append("")
            for exc in self.raises:
                lines.append(f"- {exc}")
            lines.append("")
        
        if self.examples:
            lines.append("**Examples:**")
            lines.append("")
            for example in self.examples:
                lines.append(f"```python")
                lines.append(example)
                lines.append(f"```")
                lines.append("")
        
        return "\n".join(lines)


@dataclass
class ClassDoc:
    """Documentation for a class."""
    name: str
    docstring: str
    methods: List[FunctionDoc] = field(default_factory=list)
    attributes: List[Dict[str, str]] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown."""
        lines = [
            f"## `{self.name}`",
            "",
        ]
        
        if self.bases:
            lines.append(f"**Inherits from:** {', '.join(self.bases)}")
            lines.append("")
        
        if self.docstring:
            lines.append(self.docstring)
            lines.append("")
        
        if self.attributes:
            lines.append("**Attributes:**")
            lines.append("")
            for attr in self.attributes:
                lines.append(f"- `{attr['name']}` ({attr.get('type', 'Any')}): {attr.get('description', '')}")
            lines.append("")
        
        if self.methods:
            lines.append("**Methods:**")
            lines.append("")
            for method in self.methods:
                lines.append(method.to_markdown())
        
        return "\n".join(lines)


@dataclass
class ModuleDoc:
    """Documentation for a module."""
    name: str
    path: str
    docstring: str
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown."""
        lines = [
            f"# Module: `{self.name}`",
            "",
            f"**Path:** `{self.path}`",
            "",
        ]
        
        if self.docstring:
            lines.append(self.docstring)
            lines.append("")
        
        if self.classes:
            lines.append("## Classes")
            lines.append("")
            for cls in self.classes:
                lines.append(cls.to_markdown())
        
        if self.functions:
            lines.append("## Functions")
            lines.append("")
            for func in self.functions:
                lines.append(func.to_markdown())
        
        return "\n".join(lines)


class DocstringParser:
    """Parser for Python docstrings."""
    
    @staticmethod
    def parse(docstring: str) -> Dict[str, Any]:
        """Parse a docstring into structured data."""
        if not docstring:
            return {"description": "", "params": [], "returns": "", "raises": [], "examples": []}
        
        result = {
            "description": "",
            "params": [],
            "returns": "",
            "raises": [],
            "examples": []
        }
        
        lines = docstring.strip().split("\n")
        current_section = "description"
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.lower().startswith("args:") or stripped.lower().startswith("parameters:"):
                if current_content:
                    result["description"] = "\n".join(current_content).strip()
                current_section = "params"
                current_content = []
            elif stripped.lower().startswith("returns:"):
                current_section = "returns"
                current_content = []
                if ":" in stripped:
                    result["returns"] = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("raises:"):
                current_section = "raises"
                current_content = []
            elif stripped.lower().startswith("example"):
                current_section = "examples"
                current_content = []
            elif current_section == "params" and stripped.startswith("-"):
                param_match = re.match(r'-\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.*)', stripped)
                if param_match:
                    result["params"].append({
                        "name": param_match.group(1),
                        "type": param_match.group(2) or "Any",
                        "description": param_match.group(3)
                    })
            elif current_section == "raises" and stripped.startswith("-"):
                result["raises"].append(stripped[1:].strip())
            elif current_section == "examples":
                current_content.append(line)
            else:
                current_content.append(line)
        
        if current_section == "description" and current_content:
            result["description"] = "\n".join(current_content).strip()
        elif current_section == "examples" and current_content:
            result["examples"] = ["\n".join(current_content).strip()]
        
        return result


class CodeAnalyzer:
    """Analyzer for Python source code."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize code analyzer."""
        self.project_root = project_root or os.getcwd()
    
    def analyze_file(self, file_path: str) -> ModuleDoc:
        """Analyze a Python file and extract documentation."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        module_docstring = ast.get_docstring(tree) or ""
        module_name = os.path.basename(file_path).replace('.py', '')
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(self._analyze_class(node))
            elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                if node.col_offset == 0:
                    functions.append(self._analyze_function(node))
            elif isinstance(node, ast.AsyncFunctionDef):
                if node.col_offset == 0:
                    functions.append(self._analyze_function(node))
        
        return ModuleDoc(
            name=module_name,
            path=file_path,
            docstring=module_docstring,
            classes=classes,
            functions=functions
        )
    
    def _analyze_class(self, node: ast.ClassDef) -> ClassDoc:
        """Analyze a class definition."""
        docstring = ast.get_docstring(node) or ""
        bases = [self._get_name(base) for base in node.bases]
        
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._analyze_function(item))
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_type = self._get_annotation(item.annotation) if item.annotation else "Any"
                attributes.append({
                    "name": item.target.id,
                    "type": attr_type,
                    "description": ""
                })
        
        return ClassDoc(
            name=node.name,
            docstring=docstring,
            methods=methods,
            attributes=attributes,
            bases=bases
        )
    
    def _analyze_function(self, node) -> FunctionDoc:
        """Analyze a function definition."""
        docstring = ast.get_docstring(node) or ""
        parsed = DocstringParser.parse(docstring)
        
        args = []
        for arg in node.args.args:
            arg_type = self._get_annotation(arg.annotation) if arg.annotation else "Any"
            args.append(f"{arg.arg}: {arg_type}")
        
        returns = ""
        if node.returns:
            returns = self._get_annotation(node.returns)
        
        signature = f"def {node.name}({', '.join(args)})"
        if returns:
            signature += f" -> {returns}"
        
        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=parsed["description"],
            parameters=parsed["params"],
            returns=parsed["returns"] or returns,
            raises=parsed["raises"],
            examples=parsed["examples"]
        )
    
    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def _get_annotation(self, node) -> str:
        """Get annotation string from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Tuple):
            return ", ".join(self._get_annotation(e) for e in node.elts)
        return "Any"


class DocumentationGenerator:
    """Main documentation generator."""
    
    def __init__(self, project_root: Optional[str] = None, output_dir: Optional[str] = None):
        """Initialize documentation generator."""
        self.project_root = project_root or os.getcwd()
        self.output_dir = output_dir or os.path.join(self.project_root, "docs")
        self.analyzer = CodeAnalyzer(self.project_root)
    
    def generate_api_reference(self, source_dirs: Optional[List[str]] = None) -> DocPage:
        """Generate API reference documentation."""
        source_dirs = source_dirs or [os.path.join(self.project_root, "src")]
        
        page = DocPage(
            title="API Reference",
            doc_type=DocType.API_REFERENCE,
            metadata={"version": "1.0", "generated": True}
        )
        
        for source_dir in source_dirs:
            if not os.path.exists(source_dir):
                continue
            
            for root, dirs, files in os.walk(source_dir):
                dirs[:] = [d for d in dirs if not d.startswith('__')]
                
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        try:
                            module_doc = self.analyzer.analyze_file(file_path)
                            
                            section = DocSection(
                                title=module_doc.name,
                                content=module_doc.to_markdown(),
                                level=2
                            )
                            page.sections.append(section)
                        except Exception:
                            pass
        
        return page
    
    def generate_user_guide(self) -> DocPage:
        """Generate user guide documentation."""
        page = DocPage(
            title="User Guide",
            doc_type=DocType.USER_GUIDE,
            metadata={"version": "3.0", "audience": "End Users (Traders)"}
        )
        
        page.sections = [
            DocSection(
                title="Getting Started",
                content="""Your Zepix Trading Bot now has a **Plugin Architecture**! This means:

- **More organized** - Each trading strategy is a separate plugin
- **Independent performance** - Track each strategy separately
- **Easy to enable/disable** - Turn strategies on/off without code changes
- **Better notifications** - 3 specialized Telegram bots""",
                level=2
            ),
            DocSection(
                title="Telegram Bots Guide",
                content="""You now have **3 Telegram bots** instead of 1:

**1. Controller Bot** (`@zepix_controller_bot`)
- Purpose: Manage the bot
- Commands: `/status`, `/enable_plugin`, `/disable_plugin`, `/daily_report`, `/help`

**2. Notification Bot** (`@zepix_notifications_bot`)
- Purpose: Receive trade alerts
- Receives: Entry alerts, Exit alerts, Profit bookings, Warnings

**3. Analytics Bot** (`@zepix_analytics_bot`)
- Purpose: Performance reports
- Commands: `/daily_report`, `/weekly_report`, `/plugin_stats`, `/export_trades`""",
                level=2
            ),
            DocSection(
                title="Plugins Explained",
                content="""A **plugin** is a self-contained trading strategy. Think of it like an app on your phone - you can install, enable, disable, or uninstall it without affecting others.

**Current Plugins:**

**combined_v3** - Your original V3 logic (combinedlogic-1/2/3)
- Symbols: XAUUSD, EURUSD, GBPUSD
- Risk: 1.5% per trade
- Max Daily Loss: $500

**Commands:**
- Check status: `/status`
- Disable: `/disable_plugin combined_v3`
- Enable: `/enable_plugin combined_v3`""",
                level=2
            ),
            DocSection(
                title="Understanding Notifications",
                content="""**Entry Alert Format:**
```
[combined_v3] ENTRY
Symbol: XAUUSD
Direction: BUY
Lot: 0.12
Entry: 2030.50
SL: 2028.00 (-25 pips)
TP: 2035.00 (+45 pips)
```

**Exit Alert Format:**
```
[combined_v3] EXIT
Symbol: XAUUSD
Ticket: #12345
Direction: BUY -> CLOSED
Exit: 2032.50
Profit: +20 pips (+$200.00)
Duration: 2h 15m
Reason: TP1 Hit
```""",
                level=2
            ),
            DocSection(
                title="Safety Features",
                content="""**Daily Loss Limit**
Each plugin has a daily loss limit. When reached:
- Plugin stops trading for the day
- You get a notification
- Resumes next day automatically

**Emergency Stop**
To stop ALL trading immediately:
```
/emergency_stop
```
This will close all open trades, disable all plugins, and require manual re-activation.""",
                level=2
            ),
            DocSection(
                title="Quick Reference",
                content="""**Most Used Commands:**

| Command | Bot | Purpose |
|---------|-----|---------|
| `/status` | Controller | System health |
| `/daily_report` | Analytics | Today's P&L |
| `/enable_plugin <name>` | Controller | Turn on strategy |
| `/disable_plugin <name>` | Controller | Turn off strategy |
| `/emergency_stop` | Controller | Stop everything |

**Config File Locations:**
- Main Config: `config/config.json`
- Plugin Configs: `src/logic_plugins/<plugin_id>/config.json`
- Logs: `logs/bot.log`
- Database: `data/zepix_combined_v3.db`""",
                level=2
            ),
        ]
        
        return page
    
    def generate_admin_guide(self) -> DocPage:
        """Generate admin guide documentation."""
        page = DocPage(
            title="Administrator Guide",
            doc_type=DocType.ADMIN_GUIDE,
            metadata={"version": "1.0", "audience": "Bot Administrators"}
        )
        
        page.sections = [
            DocSection(
                title="System Requirements",
                content="""**Hardware Requirements:**
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB free space
- Network: Stable internet connection

**Software Requirements:**
- Python 3.10 or higher
- MetaTrader 5 Terminal
- SQLite 3.x
- Git (for updates)""",
                level=2
            ),
            DocSection(
                title="Installation",
                content="""**Step 1: Clone Repository**
```bash
git clone https://github.com/asggroupsinfo/ZepixTradingBot-New-update-v1.git
cd ZepixTradingBot-New-update-v1
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Step 5: Initialize Database**
```bash
python scripts/init_database.py
```

**Step 6: Start Bot**
```bash
python main.py
```""",
                level=2
            ),
            DocSection(
                title="Configuration Management",
                content="""**Main Configuration File:** `config/config.json`

**Key Settings:**
```json
{
    "mt5": {
        "login": 12345678,
        "password": "your_password",
        "server": "XMGlobal-MT5"
    },
    "telegram": {
        "controller_token": "BOT_TOKEN_1",
        "notification_token": "BOT_TOKEN_2",
        "analytics_token": "BOT_TOKEN_3",
        "chat_id": -1001234567890
    },
    "plugins": {
        "combined_v3": {
            "enabled": true,
            "risk_percentage": 1.5,
            "max_lot_size": 1.0,
            "daily_loss_limit": 500.0
        }
    }
}
```

**Hot Reload Configuration:**
```
/config_reload <plugin_name>
```""",
                level=2
            ),
            DocSection(
                title="Plugin Management",
                content="""**Enable Plugin:**
```
/enable_plugin <plugin_name>
```

**Disable Plugin:**
```
/disable_plugin <plugin_name>
```

**Check Plugin Status:**
```
/status
```

**Plugin Directory Structure:**
```
src/logic_plugins/
├── combined_v3/
│   ├── __init__.py
│   ├── plugin.py
│   ├── config.json
│   └── README.md
└── price_action_1m/
    ├── __init__.py
    ├── plugin.py
    └── config.json
```""",
                level=2
            ),
            DocSection(
                title="Monitoring & Logging",
                content="""**Log Files:**
- `logs/bot.log` - Main bot log
- `logs/trades.log` - Trade execution log
- `logs/errors.log` - Error log

**View Live Logs:**
```bash
tail -f logs/bot.log
```

**Log Rotation:**
Logs are automatically rotated daily. Old logs are compressed and stored in `logs/archive/`.

**Health Check:**
```
/health
```
Returns system status including:
- MT5 connection status
- Telegram bot status
- Plugin health
- Database status""",
                level=2
            ),
            DocSection(
                title="Backup & Recovery",
                content="""**Database Backup:**
```bash
python scripts/backup_database.py
```
Backups are stored in `backups/` directory.

**Restore Database:**
```bash
python scripts/restore_database.py backups/backup_2026-01-12.db
```

**Configuration Backup:**
```bash
cp config/config.json config/config.json.backup
```

**Emergency Recovery:**
1. Stop the bot: `Ctrl+C` or `/emergency_stop`
2. Restore last known good config
3. Restart: `python main.py`""",
                level=2
            ),
        ]
        
        return page
    
    def generate_plugin_developer_guide(self) -> DocPage:
        """Generate plugin developer guide documentation."""
        page = DocPage(
            title="Plugin Developer Guide",
            doc_type=DocType.PLUGIN_GUIDE,
            metadata={"version": "1.0", "audience": "Plugin Developers"}
        )
        
        page.sections = [
            DocSection(
                title="Plugin Architecture Overview",
                content="""The V5 Hybrid Plugin Architecture allows you to create custom trading strategies as isolated plugins.

**Key Concepts:**
- **Plugin**: Self-contained trading strategy
- **ServiceAPI**: Interface to core services (orders, risk, notifications)
- **Plugin Database**: Isolated database per plugin
- **Plugin Config**: JSON configuration file

**Plugin Lifecycle:**
1. `on_load()` - Called when plugin is loaded
2. `on_enable()` - Called when plugin is enabled
3. `on_alert()` - Called when TradingView alert received
4. `on_disable()` - Called when plugin is disabled
5. `on_unload()` - Called when plugin is unloaded""",
                level=2
            ),
            DocSection(
                title="Creating a New Plugin",
                content="""**Step 1: Create Plugin Directory**
```bash
mkdir -p src/logic_plugins/my_strategy
```

**Step 2: Create Plugin Files**

`src/logic_plugins/my_strategy/__init__.py`:
```python
from .plugin import MyStrategyPlugin

__all__ = ['MyStrategyPlugin']
```

`src/logic_plugins/my_strategy/plugin.py`:
```python
from src.core.plugin_system.base_plugin import BaseLogicPlugin
from src.core.plugin_system.service_api import ServiceAPI

class MyStrategyPlugin(BaseLogicPlugin):
    PLUGIN_ID = "my_strategy"
    PLUGIN_NAME = "My Strategy"
    VERSION = "1.0.0"
    
    def __init__(self, service_api: ServiceAPI):
        super().__init__(service_api)
        self.config = self.load_config()
    
    async def on_alert(self, alert_data: dict) -> None:
        # Process TradingView alert
        symbol = alert_data.get('symbol')
        direction = alert_data.get('direction')
        
        if direction == 'BUY':
            await self.service_api.place_order(
                symbol=symbol,
                direction='BUY',
                lot_size=0.1,
                plugin_id=self.PLUGIN_ID
            )
```

`src/logic_plugins/my_strategy/config.json`:
```json
{
    "plugin_id": "my_strategy",
    "name": "My Strategy",
    "version": "1.0.0",
    "enabled": true,
    "symbols": ["XAUUSD", "EURUSD"],
    "settings": {
        "risk_percentage": 1.0,
        "max_lot_size": 0.5
    }
}
```""",
                level=2
            ),
            DocSection(
                title="ServiceAPI Reference",
                content="""The ServiceAPI provides access to core trading services.

**Order Execution:**
```python
await self.service_api.place_order(
    symbol="XAUUSD",
    direction="BUY",
    lot_size=0.1,
    stop_loss=2025.00,
    take_profit=2035.00,
    plugin_id=self.PLUGIN_ID
)

await self.service_api.close_position(
    ticket=12345,
    plugin_id=self.PLUGIN_ID
)

await self.service_api.modify_order(
    ticket=12345,
    stop_loss=2027.00,
    plugin_id=self.PLUGIN_ID
)
```

**Risk Management:**
```python
lot_size = await self.service_api.calculate_lot_size(
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=25,
    plugin_id=self.PLUGIN_ID
)

can_trade = await self.service_api.check_daily_limit(
    plugin_id=self.PLUGIN_ID
)
```

**Notifications:**
```python
await self.service_api.send_notification(
    message="Trade opened!",
    priority="high",
    plugin_id=self.PLUGIN_ID
)
```""",
                level=2
            ),
            DocSection(
                title="Plugin Database",
                content="""Each plugin has its own isolated database.

**Accessing Plugin Database:**
```python
class MyStrategyPlugin(BaseLogicPlugin):
    def __init__(self, service_api: ServiceAPI):
        super().__init__(service_api)
        self.db = self.get_database()
    
    async def save_trade(self, trade_data: dict):
        await self.db.execute(
            "INSERT INTO trades (symbol, direction, lot) VALUES (?, ?, ?)",
            (trade_data['symbol'], trade_data['direction'], trade_data['lot'])
        )
    
    async def get_trades(self):
        return await self.db.fetch_all("SELECT * FROM trades")
```

**Database Location:**
`data/zepix_<plugin_id>.db`

**Schema Migration:**
Place migration files in `migrations/<plugin_id>/` directory.""",
                level=2
            ),
            DocSection(
                title="Testing Your Plugin",
                content="""**Unit Tests:**
```python
import pytest
from src.logic_plugins.my_strategy.plugin import MyStrategyPlugin

class TestMyStrategyPlugin:
    def test_plugin_creation(self):
        plugin = MyStrategyPlugin(mock_service_api)
        assert plugin.PLUGIN_ID == "my_strategy"
    
    @pytest.mark.asyncio
    async def test_on_alert(self):
        plugin = MyStrategyPlugin(mock_service_api)
        await plugin.on_alert({'symbol': 'XAUUSD', 'direction': 'BUY'})
        # Assert order was placed
```

**Run Tests:**
```bash
pytest tests/test_my_strategy.py -v
```

**Shadow Mode Testing:**
Enable shadow mode to test without real trades:
```json
{
    "settings": {
        "shadow_mode": true
    }
}
```""",
                level=2
            ),
            DocSection(
                title="Best Practices",
                content="""**1. Always Use ServiceAPI**
Never access MT5 directly. Use ServiceAPI for all trading operations.

**2. Handle Errors Gracefully**
```python
try:
    await self.service_api.place_order(...)
except OrderExecutionError as e:
    self.logger.error(f"Order failed: {e}")
    await self.service_api.send_notification(f"Order failed: {e}")
```

**3. Log Important Events**
```python
self.logger.info(f"Processing alert: {alert_data}")
self.logger.warning(f"Daily limit approaching")
self.logger.error(f"Failed to execute: {error}")
```

**4. Respect Rate Limits**
Don't spam notifications. Use appropriate priority levels.

**5. Clean Up Resources**
```python
async def on_unload(self):
    await self.db.close()
    self.logger.info("Plugin unloaded")
```""",
                level=2
            ),
        ]
        
        return page
    
    def generate_troubleshooting_guide(self) -> DocPage:
        """Generate troubleshooting guide documentation."""
        page = DocPage(
            title="Troubleshooting Guide",
            doc_type=DocType.TROUBLESHOOTING,
            metadata={"version": "1.0", "audience": "All Users"}
        )
        
        page.sections = [
            DocSection(
                title="Common Issues",
                content="""This guide covers common issues and their solutions.""",
                level=2
            ),
            DocSection(
                title="Bot Not Responding to Alerts",
                content="""**Symptoms:**
- TradingView alerts sent but no trades executed
- No notifications received

**Solutions:**

1. **Check Plugin Status**
```
/status
```
Ensure the plugin is enabled.

2. **Check Daily Loss Limit**
```
/daily_limit combined_v3
```
If limit reached, plugin stops trading until next day.

3. **Check MT5 Connection**
```
/health
```
Verify MT5 connection is active.

4. **Check Logs**
```bash
tail -f logs/bot.log
```
Look for error messages.

5. **Verify Alert Format**
Ensure TradingView alert matches expected format.""",
                level=2
            ),
            DocSection(
                title="Wrong Lot Size Calculated",
                content="""**Symptoms:**
- Lot size too large or too small
- Risk percentage not matching config

**Solutions:**

1. **Check Configuration**
```json
{
    "plugins": {
        "combined_v3": {
            "settings": {
                "risk_percentage": 1.5,
                "max_lot_size": 1.0
            }
        }
    }
}
```

2. **Verify Account Balance**
Lot size is calculated based on account balance. Check MT5 account.

3. **Check Symbol Settings**
Different symbols have different pip values and lot sizes.

4. **Reload Configuration**
```
/config_reload combined_v3
```""",
                level=2
            ),
            DocSection(
                title="Not Receiving Telegram Notifications",
                content="""**Symptoms:**
- No messages from any bot
- Some bots working, others not

**Solutions:**

1. **Verify Bot Tokens**
Check `config/config.json` for correct tokens.

2. **Check Chat ID**
Ensure you're in the correct chat/group.

3. **Test Bot Connection**
```
/status
```
Should respond immediately.

4. **Check Rate Limits**
Telegram has rate limits. Wait a few minutes and try again.

5. **Restart Bots**
```bash
python main.py --restart-telegram
```""",
                level=2
            ),
            DocSection(
                title="MT5 Connection Issues",
                content="""**Symptoms:**
- "MT5 not connected" error
- Orders failing to execute

**Solutions:**

1. **Check MT5 Terminal**
Ensure MT5 is running and logged in.

2. **Verify Credentials**
```json
{
    "mt5": {
        "login": 12345678,
        "password": "correct_password",
        "server": "XMGlobal-MT5"
    }
}
```

3. **Check Server**
Ensure correct server name (case-sensitive).

4. **Restart MT5**
Close and reopen MT5 terminal.

5. **Check Network**
Verify internet connection is stable.""",
                level=2
            ),
            DocSection(
                title="Database Errors",
                content="""**Symptoms:**
- "Database locked" error
- "Table not found" error

**Solutions:**

1. **Database Locked**
```bash
# Stop the bot
# Wait 30 seconds
python main.py
```

2. **Table Not Found**
```bash
python scripts/init_database.py
```

3. **Corrupted Database**
```bash
python scripts/restore_database.py backups/latest.db
```

4. **Check Disk Space**
Ensure sufficient disk space available.""",
                level=2
            ),
            DocSection(
                title="Plugin Errors",
                content="""**Symptoms:**
- Plugin fails to load
- Plugin crashes during operation

**Solutions:**

1. **Check Plugin Logs**
```bash
tail -f logs/plugins/combined_v3.log
```

2. **Verify Plugin Config**
Ensure `config.json` is valid JSON.

3. **Check Dependencies**
```bash
pip install -r requirements.txt
```

4. **Disable and Re-enable**
```
/disable_plugin combined_v3
/enable_plugin combined_v3
```

5. **Check Plugin Version**
Ensure plugin is compatible with current bot version.""",
                level=2
            ),
            DocSection(
                title="Getting Help",
                content="""**How to Report Issues:**

1. **Collect Information**
   - Screenshot of error
   - Recent logs: `tail -n 100 logs/bot.log > issue_log.txt`
   - Configuration (remove sensitive data)

2. **Check Documentation**
   - User Guide
   - Admin Guide
   - This Troubleshooting Guide

3. **Contact Support**
   - Critical Issues: [Emergency Contact]
   - General Support: [Support Channel]

**When Reporting:**
- Describe what you expected to happen
- Describe what actually happened
- Include steps to reproduce
- Attach logs and screenshots""",
                level=2
            ),
        ]
        
        return page
    
    def save_page(self, page: DocPage, filename: str) -> str:
        """Save a documentation page to file."""
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page.to_markdown())
        
        return filepath
    
    def generate_all(self) -> Dict[str, str]:
        """Generate all documentation files."""
        generated = {}
        
        user_guide = self.generate_user_guide()
        generated["USER_GUIDE.md"] = self.save_page(user_guide, "USER_GUIDE.md")
        
        admin_guide = self.generate_admin_guide()
        generated["ADMIN_GUIDE.md"] = self.save_page(admin_guide, "ADMIN_GUIDE.md")
        
        plugin_guide = self.generate_plugin_developer_guide()
        generated["PLUGIN_DEVELOPER_GUIDE.md"] = self.save_page(plugin_guide, "PLUGIN_DEVELOPER_GUIDE.md")
        
        troubleshooting = self.generate_troubleshooting_guide()
        generated["TROUBLESHOOTING.md"] = self.save_page(troubleshooting, "TROUBLESHOOTING.md")
        
        return generated


def generate_documentation(project_root: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, str]:
    """Generate all documentation."""
    generator = DocumentationGenerator(project_root, output_dir)
    return generator.generate_all()
