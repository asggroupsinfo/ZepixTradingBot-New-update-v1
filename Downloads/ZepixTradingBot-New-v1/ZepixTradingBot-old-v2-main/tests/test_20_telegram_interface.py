"""
Test Suite for Document 20: Telegram Unified Interface Addendum

Tests all components of the Telegram Unified Interface:
- Visual Menu Layouts (MenuBuilder)
- Live Header Manager
- Callback Handler
- User Input Wizard
- Unified Interface Manager
- Message Editing
- Navigation Logic

Version: 1.0
Date: 2026-01-12
"""

import pytest
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# =============================================================================
# Test: Module Structure Verification
# =============================================================================

class TestTelegramInterfaceStructure:
    """Test that all Document 20 modules exist."""
    
    def test_menu_builder_module_exists(self):
        """Test menu_builder.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'telegram', 'menu_builder.py'
        )
        assert os.path.exists(module_path), "menu_builder.py should exist"
    
    def test_live_header_module_exists(self):
        """Test live_header.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'telegram', 'live_header.py'
        )
        assert os.path.exists(module_path), "live_header.py should exist"
    
    def test_callback_handler_module_exists(self):
        """Test callback_handler.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'telegram', 'callback_handler.py'
        )
        assert os.path.exists(module_path), "callback_handler.py should exist"
    
    def test_input_wizard_module_exists(self):
        """Test input_wizard.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'telegram', 'input_wizard.py'
        )
        assert os.path.exists(module_path), "input_wizard.py should exist"
    
    def test_unified_interface_module_exists(self):
        """Test unified_interface.py exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'telegram', 'unified_interface.py'
        )
        assert os.path.exists(module_path), "unified_interface.py should exist"


# =============================================================================
# Test: Menu Builder Imports
# =============================================================================

class TestMenuBuilderImports:
    """Test MenuBuilder imports."""
    
    def test_import_menu_builder(self):
        """Test MenuBuilder can be imported."""
        from telegram.menu_builder import MenuBuilder
        assert MenuBuilder is not None
    
    def test_import_menu_type(self):
        """Test MenuType can be imported."""
        from telegram.menu_builder import MenuType
        assert MenuType is not None
    
    def test_import_menu_button(self):
        """Test MenuButton can be imported."""
        from telegram.menu_builder import MenuButton
        assert MenuButton is not None
    
    def test_import_menu_layout(self):
        """Test MenuLayout can be imported."""
        from telegram.menu_builder import MenuLayout
        assert MenuLayout is not None
    
    def test_import_button_type(self):
        """Test ButtonType can be imported."""
        from telegram.menu_builder import ButtonType
        assert ButtonType is not None


# =============================================================================
# Test: Menu Builder Functionality
# =============================================================================

class TestMenuBuilder:
    """Test MenuBuilder functionality."""
    
    def test_menu_builder_instantiation(self):
        """Test MenuBuilder can be instantiated."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        assert builder is not None
    
    def test_menu_builder_has_menus(self):
        """Test MenuBuilder has default menus."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        assert len(builder.menus) > 0
    
    def test_get_main_menu(self):
        """Test getting main menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_main_menu()
        assert menu is not None
        assert menu.menu_type == MenuType.MAIN
    
    def test_get_trading_menu(self):
        """Test getting trading menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.TRADING)
        assert menu is not None
        assert menu.menu_type == MenuType.TRADING
    
    def test_get_settings_menu(self):
        """Test getting settings menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.SETTINGS)
        assert menu is not None
        assert menu.menu_type == MenuType.SETTINGS
    
    def test_get_plugins_menu(self):
        """Test getting plugins menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.PLUGINS)
        assert menu is not None
        assert menu.menu_type == MenuType.PLUGINS
    
    def test_get_risk_menu(self):
        """Test getting risk menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.RISK)
        assert menu is not None
        assert menu.menu_type == MenuType.RISK
    
    def test_get_analytics_menu(self):
        """Test getting analytics menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.ANALYTICS)
        assert menu is not None
        assert menu.menu_type == MenuType.ANALYTICS
    
    def test_get_help_menu(self):
        """Test getting help menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.HELP)
        assert menu is not None
        assert menu.menu_type == MenuType.HELP
    
    def test_get_admin_menu(self):
        """Test getting admin menu."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        menu = builder.get_menu(MenuType.ADMIN)
        assert menu is not None
        assert menu.menu_type == MenuType.ADMIN
    
    def test_menu_has_buttons(self):
        """Test menu has buttons."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        menu = builder.get_main_menu()
        assert len(menu.buttons) > 0
    
    def test_menu_to_inline_keyboard(self):
        """Test menu converts to inline keyboard."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        keyboard = builder.get_inline_keyboard(builder.get_main_menu().menu_type)
        assert isinstance(keyboard, list)
        assert len(keyboard) > 0
    
    def test_menu_to_reply_keyboard(self):
        """Test menu converts to reply keyboard."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        keyboard = builder.get_reply_keyboard(builder.get_main_menu().menu_type)
        assert isinstance(keyboard, list)
        assert len(keyboard) > 0
    
    def test_create_confirmation_keyboard(self):
        """Test creating confirmation keyboard."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        keyboard = builder.create_confirmation_keyboard("test_action")
        assert isinstance(keyboard, list)
        assert len(keyboard) == 1
        assert len(keyboard[0]) == 2  # Confirm and Cancel buttons
    
    def test_create_position_keyboard(self):
        """Test creating position keyboard."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        keyboard = builder.create_position_keyboard(12345, "EURUSD")
        assert isinstance(keyboard, list)
        assert len(keyboard) >= 3  # Multiple rows
    
    def test_create_plugin_keyboard(self):
        """Test creating plugin keyboard."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        keyboard = builder.create_plugin_keyboard("V3_Combined", True)
        assert isinstance(keyboard, list)
        assert len(keyboard) >= 2
    
    def test_list_menus(self):
        """Test listing all menus."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        menus = builder.list_menus()
        assert len(menus) >= 8  # At least 8 menu types


# =============================================================================
# Test: Menu Button
# =============================================================================

class TestMenuButton:
    """Test MenuButton functionality."""
    
    def test_menu_button_creation(self):
        """Test MenuButton can be created."""
        from telegram.menu_builder import MenuButton, ButtonType
        button = MenuButton(
            text="Test",
            callback_data="test:action",
            button_type=ButtonType.PRIMARY,
            emoji="🔥"
        )
        assert button.text == "Test"
        assert button.callback_data == "test:action"
    
    def test_menu_button_display_text(self):
        """Test MenuButton display text with emoji."""
        from telegram.menu_builder import MenuButton
        button = MenuButton(text="Test", callback_data="test", emoji="🔥")
        assert button.display_text == "🔥 Test"
    
    def test_menu_button_to_dict(self):
        """Test MenuButton to_dict conversion."""
        from telegram.menu_builder import MenuButton
        button = MenuButton(text="Test", callback_data="test", emoji="🔥")
        d = button.to_dict()
        assert "text" in d
        assert "callback_data" in d


# =============================================================================
# Test: Menu Layout
# =============================================================================

class TestMenuLayout:
    """Test MenuLayout functionality."""
    
    def test_menu_layout_creation(self):
        """Test MenuLayout can be created."""
        from telegram.menu_builder import MenuLayout, MenuType
        layout = MenuLayout(
            menu_type=MenuType.MAIN,
            title="Test Menu",
            description="Test Description"
        )
        assert layout.title == "Test Menu"
        assert layout.menu_type == MenuType.MAIN
    
    def test_menu_layout_add_button(self):
        """Test adding button to layout."""
        from telegram.menu_builder import MenuLayout, MenuType, MenuButton
        layout = MenuLayout(menu_type=MenuType.MAIN, title="Test")
        button = MenuButton(text="Test", callback_data="test")
        layout.add_button(button)
        assert len(layout.buttons) == 1
    
    def test_menu_layout_get_rows(self):
        """Test getting rows from layout."""
        from telegram.menu_builder import MenuLayout, MenuType, MenuButton
        layout = MenuLayout(menu_type=MenuType.MAIN, title="Test", show_back=False, show_home=False)
        layout.add_button(MenuButton(text="A", callback_data="a", row=0))
        layout.add_button(MenuButton(text="B", callback_data="b", row=0))
        layout.add_button(MenuButton(text="C", callback_data="c", row=1))
        rows = layout.get_rows()
        assert len(rows) == 2
        assert len(rows[0]) == 2
        assert len(rows[1]) == 1


# =============================================================================
# Test: Live Header Manager Imports
# =============================================================================

class TestLiveHeaderManagerImports:
    """Test LiveHeaderManager imports."""
    
    def test_import_live_header_manager(self):
        """Test LiveHeaderManager can be imported."""
        from telegram.live_header import LiveHeaderManager
        assert LiveHeaderManager is not None
    
    def test_import_header_config(self):
        """Test HeaderConfig can be imported."""
        from telegram.live_header import HeaderConfig
        assert HeaderConfig is not None
    
    def test_import_header_metrics(self):
        """Test HeaderMetrics can be imported."""
        from telegram.live_header import HeaderMetrics
        assert HeaderMetrics is not None
    
    def test_import_bot_type(self):
        """Test BotType can be imported."""
        from telegram.live_header import BotType
        assert BotType is not None
    
    def test_import_header_status(self):
        """Test HeaderStatus can be imported."""
        from telegram.live_header import HeaderStatus
        assert HeaderStatus is not None
    
    def test_import_header_formatter(self):
        """Test HeaderFormatter can be imported."""
        from telegram.live_header import HeaderFormatter
        assert HeaderFormatter is not None
    
    def test_import_header_synchronizer(self):
        """Test HeaderSynchronizer can be imported."""
        from telegram.live_header import HeaderSynchronizer
        assert HeaderSynchronizer is not None


# =============================================================================
# Test: Live Header Manager Functionality
# =============================================================================

class TestLiveHeaderManager:
    """Test LiveHeaderManager functionality."""
    
    def test_live_header_manager_instantiation(self):
        """Test LiveHeaderManager can be instantiated."""
        from telegram.live_header import LiveHeaderManager, BotType
        manager = LiveHeaderManager(bot_type=BotType.CONTROLLER)
        assert manager is not None
    
    def test_header_config_defaults(self):
        """Test HeaderConfig has correct defaults."""
        from telegram.live_header import HeaderConfig
        config = HeaderConfig()
        assert config.update_interval == 60
        assert config.show_clock == True
        assert config.show_date == True
    
    def test_header_metrics_creation(self):
        """Test HeaderMetrics can be created."""
        from telegram.live_header import HeaderMetrics
        metrics = HeaderMetrics(
            open_trades=5,
            daily_pnl=150.50,
            win_rate=65.5
        )
        assert metrics.open_trades == 5
        assert metrics.daily_pnl == 150.50
    
    def test_header_metrics_to_dict(self):
        """Test HeaderMetrics to_dict conversion."""
        from telegram.live_header import HeaderMetrics
        metrics = HeaderMetrics(open_trades=3)
        d = metrics.to_dict()
        assert "open_trades" in d
        assert d["open_trades"] == 3
    
    def test_header_formatter_controller(self):
        """Test HeaderFormatter for controller bot."""
        from telegram.live_header import HeaderFormatter, BotType, HeaderMetrics
        formatter = HeaderFormatter(BotType.CONTROLLER)
        metrics = HeaderMetrics(open_trades=2, daily_pnl=100.0)
        header = formatter.format_header(metrics)
        assert "ZEPIX CONTROLLER" in header
        assert "Trades" in header
    
    def test_header_formatter_notification(self):
        """Test HeaderFormatter for notification bot."""
        from telegram.live_header import HeaderFormatter, BotType, HeaderMetrics
        formatter = HeaderFormatter(BotType.NOTIFICATION)
        metrics = HeaderMetrics(alerts_today=10)
        header = formatter.format_header(metrics)
        assert "ZEPIX NOTIFICATIONS" in header
        assert "Alerts" in header
    
    def test_header_formatter_analytics(self):
        """Test HeaderFormatter for analytics bot."""
        from telegram.live_header import HeaderFormatter, BotType, HeaderMetrics
        formatter = HeaderFormatter(BotType.ANALYTICS)
        metrics = HeaderMetrics(win_rate=70.0)
        header = formatter.format_header(metrics)
        assert "ZEPIX ANALYTICS" in header
        assert "Win Rate" in header
    
    def test_header_manager_update_metrics(self):
        """Test updating metrics in header manager."""
        from telegram.live_header import LiveHeaderManager, BotType, HeaderMetrics
        manager = LiveHeaderManager(bot_type=BotType.CONTROLLER)
        metrics = HeaderMetrics(open_trades=5)
        manager.update_metrics(metrics)
        assert manager.metrics.open_trades == 5
    
    def test_header_manager_update_single_metric(self):
        """Test updating single metric."""
        from telegram.live_header import LiveHeaderManager, BotType
        manager = LiveHeaderManager(bot_type=BotType.CONTROLLER)
        manager.update_metric("open_trades", 10)
        assert manager.metrics.open_trades == 10
    
    def test_header_manager_get_status(self):
        """Test getting header manager status."""
        from telegram.live_header import LiveHeaderManager, BotType
        manager = LiveHeaderManager(bot_type=BotType.CONTROLLER)
        status = manager.get_status()
        assert "bot_type" in status
        assert "status" in status
        assert status["bot_type"] == "controller"
    
    def test_header_synchronizer_creation(self):
        """Test HeaderSynchronizer can be created."""
        from telegram.live_header import HeaderSynchronizer
        sync = HeaderSynchronizer()
        assert sync is not None
    
    def test_header_synchronizer_register(self):
        """Test registering headers with synchronizer."""
        from telegram.live_header import HeaderSynchronizer, LiveHeaderManager, BotType
        sync = HeaderSynchronizer()
        header = LiveHeaderManager(bot_type=BotType.CONTROLLER)
        sync.register_header(header)
        assert BotType.CONTROLLER in sync.headers


# =============================================================================
# Test: Callback Handler Imports
# =============================================================================

class TestCallbackHandlerImports:
    """Test CallbackHandler imports."""
    
    def test_import_callback_processor(self):
        """Test CallbackProcessor can be imported."""
        from telegram.callback_handler import CallbackProcessor
        assert CallbackProcessor is not None
    
    def test_import_callback_data(self):
        """Test CallbackData can be imported."""
        from telegram.callback_handler import CallbackData
        assert CallbackData is not None
    
    def test_import_callback_context(self):
        """Test CallbackContext can be imported."""
        from telegram.callback_handler import CallbackContext
        assert CallbackContext is not None
    
    def test_import_callback_result(self):
        """Test CallbackResult can be imported."""
        from telegram.callback_handler import CallbackResult
        assert CallbackResult is not None
    
    def test_import_callback_type(self):
        """Test CallbackType can be imported."""
        from telegram.callback_handler import CallbackType
        assert CallbackType is not None
    
    def test_import_callback_registry(self):
        """Test CallbackRegistry can be imported."""
        from telegram.callback_handler import CallbackRegistry
        assert CallbackRegistry is not None


# =============================================================================
# Test: Callback Handler Functionality
# =============================================================================

class TestCallbackHandler:
    """Test CallbackHandler functionality."""
    
    def test_callback_processor_instantiation(self):
        """Test CallbackProcessor can be instantiated."""
        from telegram.callback_handler import CallbackProcessor
        processor = CallbackProcessor()
        assert processor is not None
    
    def test_callback_data_parse_menu(self):
        """Test parsing menu callback data."""
        from telegram.callback_handler import CallbackData, CallbackType
        data = CallbackData.parse("menu:trading")
        assert data.callback_type == CallbackType.MENU
        assert data.action == "trading"
    
    def test_callback_data_parse_action(self):
        """Test parsing action callback data."""
        from telegram.callback_handler import CallbackData, CallbackType
        data = CallbackData.parse("action:status")
        assert data.callback_type == CallbackType.ACTION
        assert data.action == "status"
    
    def test_callback_data_parse_wizard(self):
        """Test parsing wizard callback data."""
        from telegram.callback_handler import CallbackData, CallbackType
        data = CallbackData.parse("wizard:lot_size")
        assert data.callback_type == CallbackType.WIZARD
        assert data.action == "lot_size"
    
    def test_callback_data_parse_position(self):
        """Test parsing position callback data."""
        from telegram.callback_handler import CallbackData, CallbackType
        data = CallbackData.parse("position:close:12345")
        assert data.callback_type == CallbackType.POSITION
        assert data.action == "close"
        assert data.params == ["12345"]
    
    def test_callback_data_parse_plugin(self):
        """Test parsing plugin callback data."""
        from telegram.callback_handler import CallbackData, CallbackType
        data = CallbackData.parse("plugin:enable:V3_Combined")
        assert data.callback_type == CallbackType.PLUGIN
        assert data.action == "enable"
        assert data.params == ["V3_Combined"]
    
    def test_callback_data_to_string(self):
        """Test callback data to string conversion."""
        from telegram.callback_handler import CallbackData, CallbackType
        data = CallbackData(
            callback_type=CallbackType.MENU,
            action="trading",
            params=[],
            raw_data="menu:trading"
        )
        assert data.to_string() == "menu:trading"
    
    def test_callback_context_creation(self):
        """Test CallbackContext can be created."""
        from telegram.callback_handler import CallbackContext, CallbackData
        data = CallbackData.parse("menu:main")
        context = CallbackContext(
            user_id=123,
            chat_id=456,
            message_id=789,
            callback_data=data
        )
        assert context.user_id == 123
        assert context.chat_id == 456
    
    def test_callback_context_to_dict(self):
        """Test CallbackContext to_dict conversion."""
        from telegram.callback_handler import CallbackContext, CallbackData
        data = CallbackData.parse("menu:main")
        context = CallbackContext(
            user_id=123,
            chat_id=456,
            message_id=789,
            callback_data=data
        )
        d = context.to_dict()
        assert "user_id" in d
        assert "callback_type" in d
    
    def test_callback_result_creation(self):
        """Test CallbackResult can be created."""
        from telegram.callback_handler import CallbackResult
        result = CallbackResult(
            success=True,
            message="Test message"
        )
        assert result.success == True
        assert result.message == "Test message"
    
    def test_callback_registry_register(self):
        """Test registering callback handler."""
        from telegram.callback_handler import CallbackRegistry
        
        async def test_handler(ctx):
            pass
        
        registry = CallbackRegistry()
        registry.register("test:action", test_handler)
        assert "test:action" in registry.handlers
    
    def test_callback_registry_get_handler(self):
        """Test getting callback handler."""
        from telegram.callback_handler import CallbackRegistry
        
        async def test_handler(ctx):
            pass
        
        registry = CallbackRegistry()
        registry.register("test:action", test_handler)
        handler = registry.get_handler("test:action")
        assert handler == test_handler
    
    def test_callback_processor_process_menu(self):
        """Test processing menu callback."""
        from telegram.callback_handler import CallbackProcessor, CallbackContext, CallbackData
        
        processor = CallbackProcessor()
        data = CallbackData.parse("menu:trading")
        context = CallbackContext(
            user_id=123,
            chat_id=456,
            message_id=789,
            callback_data=data
        )
        
        # Run async test
        async def run_test():
            result = await processor.process(context)
            assert result.success == True
            assert result.redirect_menu == "trading"
        
        asyncio.run(run_test())
    
    def test_callback_processor_pending_confirmations(self):
        """Test pending confirmations tracking."""
        from telegram.callback_handler import CallbackProcessor
        processor = CallbackProcessor()
        assert processor.get_pending_confirmation(123) is None
    
    def test_callback_processor_clear_confirmation(self):
        """Test clearing pending confirmation."""
        from telegram.callback_handler import CallbackProcessor
        processor = CallbackProcessor()
        result = processor.clear_pending_confirmation(123)
        assert result == False  # No pending confirmation to clear


# =============================================================================
# Test: Input Wizard Imports
# =============================================================================

class TestUserInputWizardImports:
    """Test InputWizard imports."""
    
    def test_import_input_wizard_manager(self):
        """Test InputWizardManager can be imported."""
        from telegram.input_wizard import InputWizardManager
        assert InputWizardManager is not None
    
    def test_import_wizard_step(self):
        """Test WizardStep can be imported."""
        from telegram.input_wizard import WizardStep
        assert WizardStep is not None
    
    def test_import_wizard_config(self):
        """Test WizardConfig can be imported."""
        from telegram.input_wizard import WizardConfig
        assert WizardConfig is not None
    
    def test_import_wizard_session(self):
        """Test WizardSession can be imported."""
        from telegram.input_wizard import WizardSession
        assert WizardSession is not None
    
    def test_import_wizard_state(self):
        """Test WizardState can be imported."""
        from telegram.input_wizard import WizardState
        assert WizardState is not None
    
    def test_import_input_type(self):
        """Test InputType can be imported."""
        from telegram.input_wizard import InputType
        assert InputType is not None


# =============================================================================
# Test: Input Wizard Functionality
# =============================================================================

class TestUserInputWizard:
    """Test InputWizard functionality."""
    
    def test_wizard_manager_instantiation(self):
        """Test InputWizardManager can be instantiated."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        assert manager is not None
    
    def test_wizard_manager_has_default_wizards(self):
        """Test manager has default wizards."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        assert len(manager.wizards) > 0
    
    def test_wizard_step_creation(self):
        """Test WizardStep can be created."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Enter value:",
            input_type=InputType.NUMBER
        )
        assert step.step_id == "test"
        assert step.input_type == InputType.NUMBER
    
    def test_wizard_step_validate_number(self):
        """Test number validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Enter number:",
            input_type=InputType.NUMBER,
            min_value=1,
            max_value=100
        )
        is_valid, error, value = step.validate("50")
        assert is_valid == True
        assert value == 50
    
    def test_wizard_step_validate_number_invalid(self):
        """Test invalid number validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Enter number:",
            input_type=InputType.NUMBER
        )
        is_valid, error, value = step.validate("abc")
        assert is_valid == False
        assert error is not None
    
    def test_wizard_step_validate_decimal(self):
        """Test decimal validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Enter decimal:",
            input_type=InputType.DECIMAL
        )
        is_valid, error, value = step.validate("0.5")
        assert is_valid == True
        assert value == 0.5
    
    def test_wizard_step_validate_percentage(self):
        """Test percentage validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Enter percentage:",
            input_type=InputType.PERCENTAGE
        )
        is_valid, error, value = step.validate("50%")
        assert is_valid == True
        assert value == 50.0
    
    def test_wizard_step_validate_price(self):
        """Test price validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Enter price:",
            input_type=InputType.PRICE
        )
        is_valid, error, value = step.validate("$100.50")
        assert is_valid == True
        assert value == 100.50
    
    def test_wizard_step_validate_confirmation(self):
        """Test confirmation validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Confirm?",
            input_type=InputType.CONFIRMATION
        )
        is_valid, error, value = step.validate("yes")
        assert is_valid == True
        assert value == True
    
    def test_wizard_step_validate_selection(self):
        """Test selection validation."""
        from telegram.input_wizard import WizardStep, InputType
        step = WizardStep(
            step_id="test",
            prompt="Select:",
            input_type=InputType.SELECTION,
            options=["Option A", "Option B", "Option C"]
        )
        is_valid, error, value = step.validate("Option A")
        assert is_valid == True
        assert value == "Option A"
    
    def test_wizard_config_creation(self):
        """Test WizardConfig can be created."""
        from telegram.input_wizard import WizardConfig, WizardStep, InputType
        config = WizardConfig(
            wizard_id="test",
            name="Test Wizard",
            description="Test description",
            steps=[
                WizardStep(step_id="step1", prompt="Enter:", input_type=InputType.TEXT)
            ]
        )
        assert config.wizard_id == "test"
        assert len(config.steps) == 1
    
    def test_wizard_manager_get_wizard(self):
        """Test getting wizard by ID."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        wizard = manager.get_wizard("lot_size")
        assert wizard is not None
        assert wizard.wizard_id == "lot_size"
    
    def test_wizard_manager_start_wizard(self):
        """Test starting a wizard session."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        session = manager.start_wizard("lot_size", user_id=123, chat_id=456)
        assert session is not None
        assert session.user_id == 123
    
    def test_wizard_manager_has_active_session(self):
        """Test checking for active session."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        manager.start_wizard("lot_size", user_id=123, chat_id=456)
        assert manager.has_active_session(123) == True
        assert manager.has_active_session(999) == False
    
    def test_wizard_manager_process_input(self):
        """Test processing wizard input."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        manager.start_wizard("lot_size", user_id=123, chat_id=456)
        success, message, data = manager.process_input(123, "0.5")
        assert success == True
        assert data is not None  # Wizard completed
    
    def test_wizard_manager_cancel_session(self):
        """Test cancelling wizard session."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        manager.start_wizard("lot_size", user_id=123, chat_id=456)
        result = manager.cancel_session(123)
        assert result == True
        assert manager.has_active_session(123) == False
    
    def test_wizard_manager_list_wizards(self):
        """Test listing all wizards."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        wizards = manager.list_wizards()
        assert len(wizards) >= 10  # At least 10 default wizards
    
    def test_wizard_session_progress(self):
        """Test wizard session progress tracking."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        session = manager.start_wizard("lot_size", user_id=123, chat_id=456)
        current, total = session.progress
        assert current == 1
        assert total >= 1


# =============================================================================
# Test: Unified Interface Manager Imports
# =============================================================================

class TestUnifiedInterfaceManagerImports:
    """Test UnifiedInterfaceManager imports."""
    
    def test_import_unified_interface_manager(self):
        """Test UnifiedInterfaceManager can be imported."""
        from telegram.unified_interface import UnifiedInterfaceManager
        assert UnifiedInterfaceManager is not None
    
    def test_import_interface_state(self):
        """Test InterfaceState can be imported."""
        from telegram.unified_interface import InterfaceState
        assert InterfaceState is not None
    
    def test_import_bot_interface(self):
        """Test BotInterface can be imported."""
        from telegram.unified_interface import BotInterface
        assert BotInterface is not None
    
    def test_import_message_editor(self):
        """Test MessageEditor can be imported."""
        from telegram.unified_interface import MessageEditor
        assert MessageEditor is not None
    
    def test_import_navigation_manager(self):
        """Test NavigationManager can be imported."""
        from telegram.unified_interface import NavigationManager
        assert NavigationManager is not None
    
    def test_import_factory_function(self):
        """Test factory function can be imported."""
        from telegram.unified_interface import create_unified_interface_manager
        assert create_unified_interface_manager is not None


# =============================================================================
# Test: Unified Interface Manager Functionality
# =============================================================================

class TestUnifiedInterfaceManager:
    """Test UnifiedInterfaceManager functionality."""
    
    def test_unified_interface_manager_instantiation(self):
        """Test UnifiedInterfaceManager can be instantiated."""
        from telegram.unified_interface import UnifiedInterfaceManager
        manager = UnifiedInterfaceManager()
        assert manager is not None
    
    def test_unified_interface_manager_with_chat_ids(self):
        """Test manager with chat IDs."""
        from telegram.unified_interface import UnifiedInterfaceManager, BotType
        manager = UnifiedInterfaceManager(
            controller_chat_id=123,
            notification_chat_id=456,
            analytics_chat_id=789
        )
        assert len(manager.interfaces) == 3
        assert BotType.CONTROLLER in manager.interfaces
    
    def test_unified_interface_manager_add_bot(self):
        """Test adding bot to manager."""
        from telegram.unified_interface import UnifiedInterfaceManager, BotType
        manager = UnifiedInterfaceManager()
        interface = manager.add_bot(BotType.CONTROLLER, 123)
        assert interface is not None
        assert interface.chat_id == 123
    
    def test_unified_interface_manager_get_interface(self):
        """Test getting interface."""
        from telegram.unified_interface import UnifiedInterfaceManager, BotType
        manager = UnifiedInterfaceManager(controller_chat_id=123)
        interface = manager.get_interface(BotType.CONTROLLER)
        assert interface is not None
        assert interface.chat_id == 123
    
    def test_unified_interface_manager_update_metrics(self):
        """Test updating metrics."""
        from telegram.unified_interface import UnifiedInterfaceManager, HeaderMetrics
        manager = UnifiedInterfaceManager()
        metrics = HeaderMetrics(open_trades=5)
        manager.update_metrics(metrics)
        assert manager.shared_metrics.open_trades == 5
    
    def test_unified_interface_manager_update_single_metric(self):
        """Test updating single metric."""
        from telegram.unified_interface import UnifiedInterfaceManager
        manager = UnifiedInterfaceManager()
        manager.update_metric("open_trades", 10)
        assert manager.shared_metrics.open_trades == 10
    
    def test_unified_interface_manager_get_all_status(self):
        """Test getting all status."""
        from telegram.unified_interface import UnifiedInterfaceManager
        manager = UnifiedInterfaceManager(controller_chat_id=123)
        status = manager.get_all_status()
        assert "state" in status
        assert "interfaces" in status
        assert "metrics" in status
    
    def test_unified_interface_manager_list_bots(self):
        """Test listing bots."""
        from telegram.unified_interface import UnifiedInterfaceManager
        manager = UnifiedInterfaceManager(
            controller_chat_id=123,
            notification_chat_id=456
        )
        bots = manager.list_bots()
        assert len(bots) == 2
    
    def test_factory_function(self):
        """Test factory function."""
        from telegram.unified_interface import create_unified_interface_manager
        manager = create_unified_interface_manager(controller_chat_id=123)
        assert manager is not None


# =============================================================================
# Test: Message Editor
# =============================================================================

class TestMessageEditor:
    """Test MessageEditor functionality."""
    
    def test_message_editor_instantiation(self):
        """Test MessageEditor can be instantiated."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        assert editor is not None
    
    def test_message_editor_track_message(self):
        """Test tracking a message."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        editor.track_message("menu:main", 123)
        assert editor.get_message_id("menu:main") == 123
    
    def test_message_editor_untrack_message(self):
        """Test untracking a message."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        editor.track_message("menu:main", 123)
        result = editor.untrack_message("menu:main")
        assert result == True
        assert editor.get_message_id("menu:main") is None
    
    def test_message_editor_should_edit(self):
        """Test should_edit check."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        editor.track_message("menu:main", 123)
        assert editor.should_edit("menu:main") == True
        assert editor.should_edit("menu:other") == False
    
    def test_message_editor_get_tracked_count(self):
        """Test getting tracked count."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        editor.track_message("a", 1)
        editor.track_message("b", 2)
        assert editor.get_tracked_count() == 2
    
    def test_message_editor_clear_all(self):
        """Test clearing all tracked messages."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        editor.track_message("a", 1)
        editor.track_message("b", 2)
        editor.clear_all()
        assert editor.get_tracked_count() == 0


# =============================================================================
# Test: Navigation Manager
# =============================================================================

class TestNavigationManager:
    """Test NavigationManager functionality."""
    
    def test_navigation_manager_instantiation(self):
        """Test NavigationManager can be instantiated."""
        from telegram.unified_interface import NavigationManager
        nav = NavigationManager()
        assert nav is not None
    
    def test_navigation_manager_push(self):
        """Test pushing menu to history."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        assert len(nav.history[123]) == 2
    
    def test_navigation_manager_pop(self):
        """Test popping menu from history."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        menu = nav.pop(123)
        assert menu == MenuType.TRADES
    
    def test_navigation_manager_peek(self):
        """Test peeking at last menu."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        menu = nav.peek(123)
        assert menu == MenuType.TRADES
        assert len(nav.history[123]) == 2  # Not removed
    
    def test_navigation_manager_get_previous(self):
        """Test getting previous menu."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        prev = nav.get_previous(123)
        assert prev == MenuType.MAIN
    
    def test_navigation_manager_clear(self):
        """Test clearing history."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        nav.push(123, MenuType.MAIN)
        nav.clear(123)
        assert 123 not in nav.history
    
    def test_navigation_manager_get_breadcrumb(self):
        """Test getting breadcrumb."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        breadcrumb = nav.get_breadcrumb(123)
        assert len(breadcrumb) == 2
    
    def test_navigation_manager_max_history(self):
        """Test max history limit."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager(max_history=3)
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        nav.push(123, MenuType.SETTINGS)
        nav.push(123, MenuType.PLUGINS)
        assert len(nav.history[123]) == 3


# =============================================================================
# Test: Document 20 Integration
# =============================================================================

class TestDocument20Integration:
    """Test Document 20 integration."""
    
    def test_all_modules_import(self):
        """Test all Document 20 modules can be imported."""
        from telegram.menu_builder import MenuBuilder
        from telegram.live_header import LiveHeaderManager
        from telegram.callback_handler import CallbackProcessor
        from telegram.input_wizard import InputWizardManager
        from telegram.unified_interface import UnifiedInterfaceManager
        
        assert MenuBuilder is not None
        assert LiveHeaderManager is not None
        assert CallbackProcessor is not None
        assert InputWizardManager is not None
        assert UnifiedInterfaceManager is not None
    
    def test_menu_builder_version(self):
        """Test MenuBuilder has correct structure."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        # Should have at least 8 menu types
        assert len(builder.list_menus()) >= 8
    
    def test_live_header_version(self):
        """Test LiveHeaderManager has correct structure."""
        from telegram.live_header import LiveHeaderManager, BotType
        # Should support all 3 bot types
        for bot_type in [BotType.CONTROLLER, BotType.NOTIFICATION, BotType.ANALYTICS]:
            manager = LiveHeaderManager(bot_type=bot_type)
            assert manager is not None
    
    def test_callback_handler_version(self):
        """Test CallbackProcessor has correct structure."""
        from telegram.callback_handler import CallbackProcessor, CallbackType
        processor = CallbackProcessor()
        # Should have handlers for all callback types
        assert len(list(CallbackType)) >= 8
    
    def test_input_wizard_version(self):
        """Test InputWizardManager has correct structure."""
        from telegram.input_wizard import InputWizardManager, InputType
        manager = InputWizardManager()
        # Should have at least 10 default wizards
        assert len(manager.list_wizards()) >= 10
        # Should support all input types
        assert len(list(InputType)) >= 10


# =============================================================================
# Test: Document 20 Summary
# =============================================================================

class TestDocument20Summary:
    """Test Document 20 requirements summary."""
    
    def test_visual_menu_layouts_implemented(self):
        """Test visual menu layouts are implemented."""
        from telegram.menu_builder import MenuBuilder, MenuType
        builder = MenuBuilder()
        
        # All required menus exist
        required_menus = [
            MenuType.MAIN, MenuType.TRADING, MenuType.SETTINGS,
            MenuType.PLUGINS, MenuType.RISK, MenuType.ANALYTICS,
            MenuType.HELP, MenuType.ADMIN
        ]
        for menu_type in required_menus:
            menu = builder.get_menu(menu_type)
            assert menu is not None, f"Menu {menu_type} should exist"
    
    def test_navigation_logic_implemented(self):
        """Test navigation logic is implemented."""
        from telegram.unified_interface import NavigationManager, MenuType
        nav = NavigationManager()
        
        # Back button support
        nav.push(123, MenuType.MAIN)
        nav.push(123, MenuType.TRADES)
        prev = nav.get_previous(123)
        assert prev == MenuType.MAIN
        
        # Home button support (clear and go to main)
        nav.clear(123)
        assert nav.get_previous(123) == MenuType.MAIN
    
    def test_inline_keyboards_implemented(self):
        """Test inline keyboards are implemented."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        
        # Confirmation keyboard
        confirm_kb = builder.create_confirmation_keyboard("test")
        assert len(confirm_kb) > 0
        
        # Position keyboard
        pos_kb = builder.create_position_keyboard(12345, "EURUSD")
        assert len(pos_kb) > 0
        
        # Plugin keyboard
        plugin_kb = builder.create_plugin_keyboard("V3", True)
        assert len(plugin_kb) > 0
    
    def test_message_editing_implemented(self):
        """Test message editing is implemented."""
        from telegram.unified_interface import MessageEditor
        editor = MessageEditor()
        
        # Track message
        editor.track_message("menu:main", 123)
        assert editor.should_edit("menu:main") == True
        
        # Get message ID for editing
        msg_id = editor.get_message_id("menu:main")
        assert msg_id == 123
    
    def test_callback_query_handling_implemented(self):
        """Test callback query handling is implemented."""
        from telegram.callback_handler import CallbackProcessor, CallbackData, CallbackContext
        import asyncio
        
        processor = CallbackProcessor()
        
        # Menu callback
        data = CallbackData.parse("menu:trading")
        context = CallbackContext(
            user_id=123, chat_id=456, message_id=789,
            callback_data=data
        )
        
        async def run_test():
            result = await processor.process(context)
            assert result.success == True
        
        asyncio.run(run_test())
    
    def test_user_input_handling_implemented(self):
        """Test user input handling is implemented."""
        from telegram.input_wizard import InputWizardManager
        manager = InputWizardManager()
        
        # Start wizard
        session = manager.start_wizard("lot_size", 123, 456)
        assert session is not None
        
        # Process input
        success, msg, data = manager.process_input(123, "0.5")
        assert success == True
    
    def test_zero_typing_interface_principle(self):
        """Test zero-typing interface principle is followed."""
        from telegram.menu_builder import MenuBuilder
        builder = MenuBuilder()
        
        # All menus have buttons (no typing required)
        for menu_type in builder.list_menus():
            menu = builder.get_menu(menu_type)
            assert len(menu.buttons) > 0, f"Menu {menu_type} should have buttons"
    
    def test_three_bot_support(self):
        """Test all 3 bots are supported."""
        from telegram.live_header import BotType
        from telegram.unified_interface import UnifiedInterfaceManager
        
        # All 3 bot types exist
        assert BotType.CONTROLLER is not None
        assert BotType.NOTIFICATION is not None
        assert BotType.ANALYTICS is not None
        
        # Manager supports all 3
        manager = UnifiedInterfaceManager(
            controller_chat_id=1,
            notification_chat_id=2,
            analytics_chat_id=3
        )
        assert len(manager.interfaces) == 3


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
