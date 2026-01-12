"""
Test Suite for Document 15: Developer Onboarding Implementation.

This test file verifies the complete implementation of:
- Environment setup scripts
- VS Code configuration
- Git hooks management
- DevContainer support
- Hello World example plugin
- Onboarding CLI tool

Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import json
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestOnboardingPackageStructure:
    """Test onboarding package structure."""
    
    def test_onboarding_package_exists(self):
        """Test that onboarding package exists."""
        package_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'onboarding')
        assert os.path.exists(package_path), "onboarding package should exist"
    
    def test_onboarding_init_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'onboarding', '__init__.py')
        assert os.path.exists(init_path), "__init__.py should exist"
    
    def test_setup_manager_module_exists(self):
        """Test that setup_manager module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'onboarding', 'setup_manager.py')
        assert os.path.exists(module_path), "setup_manager.py should exist"
    
    def test_cli_tool_module_exists(self):
        """Test that cli_tool module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'onboarding', 'cli_tool.py')
        assert os.path.exists(module_path), "cli_tool.py should exist"


class TestHelloWorldPluginStructure:
    """Test Hello World plugin structure."""
    
    def test_hello_world_directory_exists(self):
        """Test that hello_world plugin directory exists."""
        plugin_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'hello_world')
        assert os.path.exists(plugin_path), "hello_world plugin directory should exist"
    
    def test_hello_world_init_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'hello_world', '__init__.py')
        assert os.path.exists(init_path), "__init__.py should exist"
    
    def test_hello_world_plugin_exists(self):
        """Test that plugin.py exists."""
        plugin_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'hello_world', 'plugin.py')
        assert os.path.exists(plugin_path), "plugin.py should exist"
    
    def test_hello_world_config_exists(self):
        """Test that config.json exists."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'hello_world', 'config.json')
        assert os.path.exists(config_path), "config.json should exist"


class TestSetupStepEnum:
    """Test SetupStep enum."""
    
    def test_setup_step_values(self):
        """Test SetupStep enum values."""
        from src.onboarding.setup_manager import SetupStep
        
        assert SetupStep.CLONE_REPO.value == "clone_repo"
        assert SetupStep.CREATE_VENV.value == "create_venv"
        assert SetupStep.INSTALL_DEPS.value == "install_deps"
        assert SetupStep.COPY_CONFIG.value == "copy_config"
        assert SetupStep.SETUP_MT5.value == "setup_mt5"
        assert SetupStep.INSTALL_HOOKS.value == "install_hooks"


class TestSetupStatusEnum:
    """Test SetupStatus enum."""
    
    def test_setup_status_values(self):
        """Test SetupStatus enum values."""
        from src.onboarding.setup_manager import SetupStatus
        
        assert SetupStatus.PENDING.value == "pending"
        assert SetupStatus.IN_PROGRESS.value == "in_progress"
        assert SetupStatus.COMPLETED.value == "completed"
        assert SetupStatus.FAILED.value == "failed"


class TestSetupResult:
    """Test SetupResult dataclass."""
    
    def test_setup_result_creation(self):
        """Test SetupResult creation."""
        from src.onboarding.setup_manager import SetupResult, SetupStep, SetupStatus
        
        result = SetupResult(
            step=SetupStep.CREATE_VENV,
            status=SetupStatus.COMPLETED,
            message="Virtual environment created"
        )
        
        assert result.step == SetupStep.CREATE_VENV
        assert result.status == SetupStatus.COMPLETED
        assert result.message == "Virtual environment created"
    
    def test_setup_result_to_dict(self):
        """Test SetupResult to_dict method."""
        from src.onboarding.setup_manager import SetupResult, SetupStep, SetupStatus
        
        result = SetupResult(
            step=SetupStep.CREATE_VENV,
            status=SetupStatus.COMPLETED,
            message="Virtual environment created"
        )
        
        data = result.to_dict()
        
        assert data["step"] == "create_venv"
        assert data["status"] == "completed"


class TestOnboardingChecklist:
    """Test OnboardingChecklist dataclass."""
    
    def test_checklist_creation(self):
        """Test OnboardingChecklist creation."""
        from src.onboarding.setup_manager import OnboardingChecklist
        
        checklist = OnboardingChecklist()
        
        assert checklist.items == []
    
    def test_checklist_add_item(self):
        """Test add_item method."""
        from src.onboarding.setup_manager import OnboardingChecklist
        
        checklist = OnboardingChecklist()
        checklist.add_item("test_item", "Test description", False)
        
        assert len(checklist.items) == 1
        assert checklist.items[0]["name"] == "test_item"
    
    def test_checklist_mark_completed(self):
        """Test mark_completed method."""
        from src.onboarding.setup_manager import OnboardingChecklist
        
        checklist = OnboardingChecklist()
        checklist.add_item("test_item", "Test description", False)
        checklist.mark_completed("test_item")
        
        assert checklist.items[0]["completed"] == True
    
    def test_checklist_get_progress(self):
        """Test get_progress method."""
        from src.onboarding.setup_manager import OnboardingChecklist
        
        checklist = OnboardingChecklist()
        checklist.add_item("item1", "Description 1", True)
        checklist.add_item("item2", "Description 2", False)
        
        completed, total = checklist.get_progress()
        
        assert completed == 1
        assert total == 2
    
    def test_checklist_to_markdown(self):
        """Test to_markdown method."""
        from src.onboarding.setup_manager import OnboardingChecklist
        
        checklist = OnboardingChecklist()
        checklist.add_item("item1", "Description 1", True)
        
        markdown = checklist.to_markdown()
        
        assert "Developer Onboarding Checklist" in markdown
        assert "[x]" in markdown


class TestSetupScriptGenerator:
    """Test SetupScriptGenerator class."""
    
    def test_generate_bash_script(self):
        """Test generate_bash_script method."""
        from src.onboarding.setup_manager import SetupScriptGenerator
        
        script = SetupScriptGenerator.generate_bash_script()
        
        assert "#!/bin/bash" in script
        assert "python3 -m venv venv" in script
        assert "pip install" in script
    
    def test_generate_batch_script(self):
        """Test generate_batch_script method."""
        from src.onboarding.setup_manager import SetupScriptGenerator
        
        script = SetupScriptGenerator.generate_batch_script()
        
        assert "@echo off" in script
        assert "python -m venv venv" in script


class TestVSCodeConfigGenerator:
    """Test VSCodeConfigGenerator class."""
    
    def test_get_settings(self):
        """Test get_settings method."""
        from src.onboarding.setup_manager import VSCodeConfigGenerator
        
        settings = VSCodeConfigGenerator.get_settings()
        
        assert "python.defaultInterpreterPath" in settings
        assert "python.formatting.provider" in settings
        assert "python.linting.enabled" in settings
    
    def test_get_launch_config(self):
        """Test get_launch_config method."""
        from src.onboarding.setup_manager import VSCodeConfigGenerator
        
        launch = VSCodeConfigGenerator.get_launch_config()
        
        assert "version" in launch
        assert "configurations" in launch
        assert len(launch["configurations"]) > 0
    
    def test_get_extensions(self):
        """Test get_extensions method."""
        from src.onboarding.setup_manager import VSCodeConfigGenerator
        
        extensions = VSCodeConfigGenerator.get_extensions()
        
        assert "recommendations" in extensions
        assert "ms-python.python" in extensions["recommendations"]


class TestGitHooksManager:
    """Test GitHooksManager class."""
    
    def test_get_pre_commit_hook(self):
        """Test get_pre_commit_hook method."""
        from src.onboarding.setup_manager import GitHooksManager
        
        hook = GitHooksManager.get_pre_commit_hook()
        
        assert "#!/bin/bash" in hook
        assert "pre-commit" in hook.lower()
    
    def test_get_pre_push_hook(self):
        """Test get_pre_push_hook method."""
        from src.onboarding.setup_manager import GitHooksManager
        
        hook = GitHooksManager.get_pre_push_hook()
        
        assert "#!/bin/bash" in hook
        assert "pytest" in hook
    
    def test_get_pre_commit_config(self):
        """Test get_pre_commit_config method."""
        from src.onboarding.setup_manager import GitHooksManager
        
        config = GitHooksManager.get_pre_commit_config()
        
        assert "repos:" in config
        assert "black" in config
        assert "isort" in config


class TestDevContainerGenerator:
    """Test DevContainerGenerator class."""
    
    def test_get_devcontainer_json(self):
        """Test get_devcontainer_json method."""
        from src.onboarding.setup_manager import DevContainerGenerator
        
        config = DevContainerGenerator.get_devcontainer_json()
        
        assert "name" in config
        assert "image" in config
        assert "customizations" in config
    
    def test_get_dockerfile(self):
        """Test get_dockerfile method."""
        from src.onboarding.setup_manager import DevContainerGenerator
        
        dockerfile = DevContainerGenerator.get_dockerfile()
        
        assert "FROM" in dockerfile
        assert "python" in dockerfile.lower()
        assert "pip install" in dockerfile


class TestOnboardingChecklistGenerator:
    """Test OnboardingChecklistGenerator class."""
    
    def test_create_default_checklist(self):
        """Test create_default_checklist method."""
        from src.onboarding.setup_manager import OnboardingChecklistGenerator
        
        checklist = OnboardingChecklistGenerator.create_default_checklist()
        
        assert len(checklist.items) > 0
    
    def test_get_checklist_items(self):
        """Test get_checklist_items method."""
        from src.onboarding.setup_manager import OnboardingChecklistGenerator
        
        items = OnboardingChecklistGenerator.get_checklist_items()
        
        assert len(items) > 0
        assert any("environment" in item[0].lower() for item in items)


class TestEnvironmentVerifier:
    """Test EnvironmentVerifier class."""
    
    def test_check_python_version(self):
        """Test check_python_version method."""
        from src.onboarding.setup_manager import EnvironmentVerifier
        
        passed, message = EnvironmentVerifier.check_python_version()
        
        assert isinstance(passed, bool)
        assert isinstance(message, str)
        assert "Python" in message
    
    def test_check_git(self):
        """Test check_git method."""
        from src.onboarding.setup_manager import EnvironmentVerifier
        
        passed, message = EnvironmentVerifier.check_git()
        
        assert isinstance(passed, bool)
        assert isinstance(message, str)


class TestDeveloperSetupManager:
    """Test DeveloperSetupManager class."""
    
    def test_setup_manager_creation(self):
        """Test DeveloperSetupManager creation."""
        from src.onboarding.setup_manager import DeveloperSetupManager
        
        manager = DeveloperSetupManager()
        
        assert manager.project_root is not None
    
    def test_verify_environment(self):
        """Test verify_environment method."""
        from src.onboarding.setup_manager import DeveloperSetupManager
        
        manager = DeveloperSetupManager()
        checks = manager.verify_environment()
        
        assert isinstance(checks, list)
        assert len(checks) > 0
    
    def test_create_onboarding_checklist(self):
        """Test create_onboarding_checklist method."""
        from src.onboarding.setup_manager import DeveloperSetupManager
        
        manager = DeveloperSetupManager()
        checklist = manager.create_onboarding_checklist()
        
        assert len(checklist.items) > 0


class TestCheckStatusEnum:
    """Test CheckStatus enum from CLI tool."""
    
    def test_check_status_values(self):
        """Test CheckStatus enum values."""
        from src.onboarding.cli_tool import CheckStatus
        
        assert CheckStatus.PASS.value == "pass"
        assert CheckStatus.FAIL.value == "fail"
        assert CheckStatus.WARN.value == "warn"
        assert CheckStatus.SKIP.value == "skip"


class TestCheckResult:
    """Test CheckResult dataclass from CLI tool."""
    
    def test_check_result_creation(self):
        """Test CheckResult creation."""
        from src.onboarding.cli_tool import CheckResult, CheckStatus
        
        result = CheckResult(
            name="Test Check",
            status=CheckStatus.PASS,
            message="Test passed"
        )
        
        assert result.name == "Test Check"
        assert result.status == CheckStatus.PASS
    
    def test_check_result_to_dict(self):
        """Test CheckResult to_dict method."""
        from src.onboarding.cli_tool import CheckResult, CheckStatus
        
        result = CheckResult(
            name="Test Check",
            status=CheckStatus.PASS,
            message="Test passed"
        )
        
        data = result.to_dict()
        
        assert data["name"] == "Test Check"
        assert data["status"] == "pass"


class TestOnboardingReport:
    """Test OnboardingReport dataclass."""
    
    def test_report_creation(self):
        """Test OnboardingReport creation."""
        from src.onboarding.cli_tool import OnboardingReport
        
        report = OnboardingReport()
        
        assert report.checks == []
    
    def test_report_passed_count(self):
        """Test passed property."""
        from src.onboarding.cli_tool import OnboardingReport, CheckResult, CheckStatus
        
        report = OnboardingReport()
        report.checks.append(CheckResult("Test1", CheckStatus.PASS, "OK"))
        report.checks.append(CheckResult("Test2", CheckStatus.FAIL, "Failed"))
        
        assert report.passed == 1
        assert report.failed == 1
    
    def test_report_all_passed(self):
        """Test all_passed property."""
        from src.onboarding.cli_tool import OnboardingReport, CheckResult, CheckStatus
        
        report = OnboardingReport()
        report.checks.append(CheckResult("Test1", CheckStatus.PASS, "OK"))
        
        assert report.all_passed == True
        
        report.checks.append(CheckResult("Test2", CheckStatus.FAIL, "Failed"))
        
        assert report.all_passed == False


class TestEnvironmentChecker:
    """Test EnvironmentChecker class."""
    
    def test_check_python_version(self):
        """Test check_python_version method."""
        from src.onboarding.cli_tool import EnvironmentChecker
        
        result = EnvironmentChecker.check_python_version()
        
        assert result.name == "Python Version"
        assert "Python" in result.message
    
    def test_check_virtual_environment(self):
        """Test check_virtual_environment method."""
        from src.onboarding.cli_tool import EnvironmentChecker
        
        result = EnvironmentChecker.check_virtual_environment()
        
        assert result.name == "Virtual Environment"
    
    def test_run_all_checks(self):
        """Test run_all_checks method."""
        from src.onboarding.cli_tool import EnvironmentChecker
        
        project_root = os.path.join(os.path.dirname(__file__), '..')
        report = EnvironmentChecker.run_all_checks(project_root)
        
        assert len(report.checks) > 0


class TestOnboardingCLI:
    """Test OnboardingCLI class."""
    
    def test_cli_creation(self):
        """Test OnboardingCLI creation."""
        from src.onboarding.cli_tool import OnboardingCLI
        
        cli = OnboardingCLI()
        
        assert cli.project_root is not None
    
    def test_cli_run_verification(self):
        """Test run_verification method."""
        from src.onboarding.cli_tool import OnboardingCLI
        
        project_root = os.path.join(os.path.dirname(__file__), '..')
        cli = OnboardingCLI(project_root)
        report = cli.run_verification()
        
        assert len(report.checks) > 0


class TestArgumentParser:
    """Test argument parser."""
    
    def test_create_argument_parser(self):
        """Test create_argument_parser function."""
        from src.onboarding.cli_tool import create_argument_parser
        
        parser = create_argument_parser()
        
        assert parser is not None
        assert parser.prog == "onboarding"


class TestHelloWorldPlugin:
    """Test Hello World plugin."""
    
    def test_plugin_import(self):
        """Test plugin can be imported."""
        from src.logic_plugins.hello_world.plugin import HelloWorldPlugin
        
        assert HelloWorldPlugin is not None
    
    def test_plugin_constants(self):
        """Test plugin constants."""
        from src.logic_plugins.hello_world.plugin import HelloWorldPlugin
        
        assert HelloWorldPlugin.PLUGIN_ID == "hello_world"
        assert HelloWorldPlugin.PLUGIN_NAME == "Hello World Example"
        assert HelloWorldPlugin.VERSION == "1.0.0"
    
    def test_plugin_creation(self):
        """Test plugin creation."""
        from src.logic_plugins.hello_world.plugin import HelloWorldPlugin, MockServiceAPI
        
        service_api = MockServiceAPI()
        plugin = HelloWorldPlugin("hello_world", {}, service_api)
        
        assert plugin.plugin_id == "hello_world"
        assert plugin.is_enabled == True
    
    def test_plugin_enable_disable(self):
        """Test enable/disable methods."""
        from src.logic_plugins.hello_world.plugin import HelloWorldPlugin, MockServiceAPI
        
        service_api = MockServiceAPI()
        plugin = HelloWorldPlugin("hello_world", {}, service_api)
        
        plugin.disable()
        assert plugin.is_enabled == False
        
        plugin.enable()
        assert plugin.is_enabled == True
    
    def test_plugin_get_status(self):
        """Test get_status method."""
        from src.logic_plugins.hello_world.plugin import HelloWorldPlugin, MockServiceAPI
        
        service_api = MockServiceAPI()
        plugin = HelloWorldPlugin("hello_world", {}, service_api)
        
        status = plugin.get_status()
        
        assert status["plugin_id"] == "hello_world"
        assert "enabled" in status
        assert "config" in status


class TestHelloWorldConfig:
    """Test HelloWorldConfig dataclass."""
    
    def test_config_creation(self):
        """Test HelloWorldConfig creation."""
        from src.logic_plugins.hello_world.plugin import HelloWorldConfig
        
        config = HelloWorldConfig()
        
        assert config.plugin_id == "hello_world"
        assert config.version == "1.0.0"
        assert config.enabled == True
    
    def test_config_from_dict(self):
        """Test from_dict method."""
        from src.logic_plugins.hello_world.plugin import HelloWorldConfig
        
        data = {
            "plugin_id": "test_plugin",
            "max_lot_size": 0.5
        }
        
        config = HelloWorldConfig.from_dict(data)
        
        assert config.plugin_id == "test_plugin"
        assert config.max_lot_size == 0.5
    
    def test_config_to_dict(self):
        """Test to_dict method."""
        from src.logic_plugins.hello_world.plugin import HelloWorldConfig
        
        config = HelloWorldConfig()
        data = config.to_dict()
        
        assert data["plugin_id"] == "hello_world"
        assert "max_lot_size" in data


class TestSignalType:
    """Test SignalType enum."""
    
    def test_signal_type_values(self):
        """Test SignalType enum values."""
        from src.logic_plugins.hello_world.plugin import SignalType
        
        assert SignalType.ENTRY.value == "entry"
        assert SignalType.EXIT.value == "exit"
        assert SignalType.INFO.value == "info"


class TestDirection:
    """Test Direction enum."""
    
    def test_direction_values(self):
        """Test Direction enum values."""
        from src.logic_plugins.hello_world.plugin import Direction
        
        assert Direction.BUY.value == "BUY"
        assert Direction.SELL.value == "SELL"


class TestSignal:
    """Test Signal dataclass."""
    
    def test_signal_creation(self):
        """Test Signal creation."""
        from src.logic_plugins.hello_world.plugin import Signal, SignalType
        
        signal = Signal(
            symbol="XAUUSD",
            signal_type=SignalType.ENTRY
        )
        
        assert signal.symbol == "XAUUSD"
        assert signal.signal_type == SignalType.ENTRY
    
    def test_signal_from_dict(self):
        """Test from_dict method."""
        from src.logic_plugins.hello_world.plugin import Signal
        
        data = {
            "symbol": "EURUSD",
            "signal_type": "entry",
            "direction": "BUY",
            "consensus_score": 8
        }
        
        signal = Signal.from_dict(data)
        
        assert signal.symbol == "EURUSD"
        assert signal.consensus_score == 8


class TestMockServices:
    """Test mock services."""
    
    def test_mock_service_api(self):
        """Test MockServiceAPI creation."""
        from src.logic_plugins.hello_world.plugin import MockServiceAPI
        
        api = MockServiceAPI()
        
        assert api.orders is not None
        assert api.risk is not None
        assert api.trend is not None
        assert api.notifications is not None
    
    def test_mock_order_service(self):
        """Test MockOrderService methods."""
        import asyncio
        from src.logic_plugins.hello_world.plugin import MockOrderService
        
        service = MockOrderService()
        
        ticket = asyncio.get_event_loop().run_until_complete(
            service.place_order("XAUUSD", "BUY", 0.1)
        )
        assert ticket == 12345
        
        result = asyncio.get_event_loop().run_until_complete(
            service.close_position(12345)
        )
        assert result == True
    
    def test_mock_risk_service(self):
        """Test MockRiskService methods."""
        import asyncio
        from src.logic_plugins.hello_world.plugin import MockRiskService
        
        service = MockRiskService()
        
        lot_size = asyncio.get_event_loop().run_until_complete(
            service.calculate_lot_size("XAUUSD", 1.5, 25)
        )
        assert lot_size > 0
        
        status = asyncio.get_event_loop().run_until_complete(
            service.check_daily_limit()
        )
        assert status["can_trade"] == True


class TestCreateHelloWorldPlugin:
    """Test create_hello_world_plugin factory function."""
    
    def test_factory_function(self):
        """Test factory function."""
        from src.logic_plugins.hello_world.plugin import create_hello_world_plugin
        
        plugin = create_hello_world_plugin()
        
        assert plugin.plugin_id == "hello_world"
        assert plugin.is_enabled == True


class TestHelloWorldConfigFile:
    """Test Hello World config.json file."""
    
    def test_config_file_valid_json(self):
        """Test config.json is valid JSON."""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'hello_world', 'config.json'
        )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config["plugin_id"] == "hello_world"
        assert "settings" in config
    
    def test_config_file_has_required_fields(self):
        """Test config.json has required fields."""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'logic_plugins', 'hello_world', 'config.json'
        )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert "plugin_id" in config
        assert "version" in config
        assert "enabled" in config
        assert "metadata" in config
        assert "settings" in config


class TestDocument15Integration:
    """Test Document 15 integration."""
    
    def test_all_modules_importable(self):
        """Test that all modules are importable."""
        from src.onboarding import setup_manager
        from src.onboarding import cli_tool
        from src.logic_plugins.hello_world import plugin
        
        assert setup_manager is not None
        assert cli_tool is not None
        assert plugin is not None
    
    def test_package_version(self):
        """Test package version."""
        from src.onboarding import __version__
        
        assert __version__ == "1.0.0"
    
    def test_all_setup_steps_covered(self):
        """Test that all setup steps are covered."""
        from src.onboarding.setup_manager import SetupStep
        
        steps = [s.value for s in SetupStep]
        
        assert "clone_repo" in steps
        assert "create_venv" in steps
        assert "install_deps" in steps
        assert "install_hooks" in steps


class TestDocument15Summary:
    """Test Document 15 summary verification."""
    
    def test_document_15_requirements_met(self):
        """Test that all Document 15 requirements are met."""
        from src.onboarding.setup_manager import (
            SetupScriptGenerator,
            VSCodeConfigGenerator,
            GitHooksManager,
            DevContainerGenerator
        )
        
        bash_script = SetupScriptGenerator.generate_bash_script()
        assert len(bash_script) > 0
        
        batch_script = SetupScriptGenerator.generate_batch_script()
        assert len(batch_script) > 0
        
        settings = VSCodeConfigGenerator.get_settings()
        assert len(settings) > 0
        
        hooks = GitHooksManager.get_pre_commit_config()
        assert len(hooks) > 0
        
        devcontainer = DevContainerGenerator.get_devcontainer_json()
        assert len(devcontainer) > 0
    
    def test_hello_world_plugin_complete(self):
        """Test Hello World plugin is complete."""
        from src.logic_plugins.hello_world.plugin import HelloWorldPlugin, create_hello_world_plugin
        
        plugin = create_hello_world_plugin()
        
        assert plugin.PLUGIN_ID == "hello_world"
        assert plugin.VERSION == "1.0.0"
        assert plugin.is_enabled == True
    
    def test_cli_tool_complete(self):
        """Test CLI tool is complete."""
        from src.onboarding.cli_tool import OnboardingCLI, create_argument_parser
        
        parser = create_argument_parser()
        assert parser is not None
        
        cli = OnboardingCLI()
        assert cli is not None
    
    def test_environment_verification_works(self):
        """Test environment verification works."""
        from src.onboarding.setup_manager import DeveloperSetupManager
        
        manager = DeveloperSetupManager()
        checks = manager.verify_environment()
        
        assert len(checks) > 0
        assert all("name" in check for check in checks)
