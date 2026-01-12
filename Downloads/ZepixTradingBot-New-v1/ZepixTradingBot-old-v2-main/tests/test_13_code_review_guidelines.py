"""
Test Suite for Document 13: Code Review Guidelines Implementation.

This test file verifies the complete implementation of:
- Linting & Formatting configurations
- Type Checking configuration
- Pre-commit Hooks
- Review Checklists
- Complexity Analysis tools
- Security Scanning integration
- CI/CD Integration scripts

Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCodeQualityPackageStructure:
    """Test code_quality package structure."""
    
    def test_code_quality_package_exists(self):
        """Test that code_quality package exists."""
        package_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality')
        assert os.path.exists(package_path), "code_quality package should exist"
    
    def test_code_quality_init_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', '__init__.py')
        assert os.path.exists(init_path), "__init__.py should exist"
    
    def test_linting_module_exists(self):
        """Test that linting module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'linting.py')
        assert os.path.exists(module_path), "linting.py should exist"
    
    def test_type_checking_module_exists(self):
        """Test that type_checking module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'type_checking.py')
        assert os.path.exists(module_path), "type_checking.py should exist"
    
    def test_pre_commit_hooks_module_exists(self):
        """Test that pre_commit_hooks module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'pre_commit_hooks.py')
        assert os.path.exists(module_path), "pre_commit_hooks.py should exist"
    
    def test_review_checklists_module_exists(self):
        """Test that review_checklists module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'review_checklists.py')
        assert os.path.exists(module_path), "review_checklists.py should exist"
    
    def test_complexity_analysis_module_exists(self):
        """Test that complexity_analysis module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'complexity_analysis.py')
        assert os.path.exists(module_path), "complexity_analysis.py should exist"
    
    def test_security_scanner_module_exists(self):
        """Test that security_scanner module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'security_scanner.py')
        assert os.path.exists(module_path), "security_scanner.py should exist"
    
    def test_ci_cd_integration_module_exists(self):
        """Test that ci_cd_integration module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'code_quality', 'ci_cd_integration.py')
        assert os.path.exists(module_path), "ci_cd_integration.py should exist"


class TestLintingEnums:
    """Test linting enums."""
    
    def test_lint_severity_enum(self):
        """Test LintSeverity enum values."""
        from src.code_quality.linting import LintSeverity
        
        assert LintSeverity.ERROR.value == "error"
        assert LintSeverity.WARNING.value == "warning"
        assert LintSeverity.CONVENTION.value == "convention"
        assert LintSeverity.REFACTOR.value == "refactor"
        assert LintSeverity.INFO.value == "info"
    
    def test_lint_tool_enum(self):
        """Test LintTool enum values."""
        from src.code_quality.linting import LintTool
        
        assert LintTool.PYLINT.value == "pylint"
        assert LintTool.FLAKE8.value == "flake8"
        assert LintTool.BLACK.value == "black"
        assert LintTool.ISORT.value == "isort"
        assert LintTool.MYPY.value == "mypy"


class TestLintIssue:
    """Test LintIssue dataclass."""
    
    def test_lint_issue_creation(self):
        """Test LintIssue creation."""
        from src.code_quality.linting import LintIssue, LintSeverity, LintTool
        
        issue = LintIssue(
            file_path="test.py",
            line=10,
            column=5,
            code="E501",
            message="Line too long",
            severity=LintSeverity.WARNING,
            tool=LintTool.FLAKE8
        )
        
        assert issue.file_path == "test.py"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.code == "E501"
        assert issue.message == "Line too long"
        assert issue.severity == LintSeverity.WARNING
        assert issue.tool == LintTool.FLAKE8
    
    def test_lint_issue_to_dict(self):
        """Test LintIssue to_dict method."""
        from src.code_quality.linting import LintIssue, LintSeverity, LintTool
        
        issue = LintIssue(
            file_path="test.py",
            line=10,
            column=5,
            code="E501",
            message="Line too long",
            severity=LintSeverity.WARNING,
            tool=LintTool.FLAKE8
        )
        
        result = issue.to_dict()
        assert result["file_path"] == "test.py"
        assert result["severity"] == "warning"
        assert result["tool"] == "flake8"


class TestLintResult:
    """Test LintResult dataclass."""
    
    def test_lint_result_creation(self):
        """Test LintResult creation."""
        from src.code_quality.linting import LintResult, LintTool
        
        result = LintResult(tool=LintTool.PYLINT)
        
        assert result.tool == LintTool.PYLINT
        assert result.issues == []
        assert result.passed == True
        assert result.exit_code == 0
    
    def test_lint_result_error_count(self):
        """Test LintResult error_count property."""
        from src.code_quality.linting import LintResult, LintIssue, LintSeverity, LintTool
        
        result = LintResult(tool=LintTool.PYLINT)
        result.issues = [
            LintIssue("test.py", 1, 0, "E001", "Error 1", LintSeverity.ERROR, LintTool.PYLINT),
            LintIssue("test.py", 2, 0, "W001", "Warning 1", LintSeverity.WARNING, LintTool.PYLINT),
            LintIssue("test.py", 3, 0, "E002", "Error 2", LintSeverity.ERROR, LintTool.PYLINT),
        ]
        
        assert result.error_count == 2
        assert result.warning_count == 1


class TestPylintConfig:
    """Test PylintConfig class."""
    
    def test_pylint_config_default(self):
        """Test PylintConfig default configuration."""
        from src.code_quality.linting import PylintConfig
        
        config = PylintConfig.get_config_dict()
        
        assert "MASTER" in config
        assert "FORMAT" in config
        assert "DESIGN" in config
        assert config["FORMAT"]["max-line-length"] == 120
    
    def test_pylint_config_generate_pylintrc(self):
        """Test PylintConfig generate_pylintrc method."""
        from src.code_quality.linting import PylintConfig
        
        content = PylintConfig.generate_pylintrc()
        
        assert "[MASTER]" in content
        assert "[FORMAT]" in content
        assert "max-line-length=120" in content


class TestBlackConfig:
    """Test BlackConfig class."""
    
    def test_black_config_default(self):
        """Test BlackConfig default configuration."""
        from src.code_quality.linting import BlackConfig
        
        config = BlackConfig.get_config_dict()
        
        assert config["line-length"] == 120
        assert "py310" in config["target-version"]
    
    def test_black_config_generate_pyproject(self):
        """Test BlackConfig generate_pyproject_section method."""
        from src.code_quality.linting import BlackConfig
        
        content = BlackConfig.generate_pyproject_section()
        
        assert "[tool.black]" in content
        assert "line-length = 120" in content


class TestIsortConfig:
    """Test IsortConfig class."""
    
    def test_isort_config_default(self):
        """Test IsortConfig default configuration."""
        from src.code_quality.linting import IsortConfig
        
        config = IsortConfig.get_config_dict()
        
        assert config["profile"] == "black"
        assert config["line_length"] == 120
    
    def test_isort_config_generate_pyproject(self):
        """Test IsortConfig generate_pyproject_section method."""
        from src.code_quality.linting import IsortConfig
        
        content = IsortConfig.generate_pyproject_section()
        
        assert "[tool.isort]" in content
        assert 'profile = "black"' in content


class TestFlake8Config:
    """Test Flake8Config class."""
    
    def test_flake8_config_default(self):
        """Test Flake8Config default configuration."""
        from src.code_quality.linting import Flake8Config
        
        config = Flake8Config.get_config_dict()
        
        assert config["max-line-length"] == 120
        assert config["max-complexity"] == 15
    
    def test_flake8_config_generate_setup_cfg(self):
        """Test Flake8Config generate_setup_cfg_section method."""
        from src.code_quality.linting import Flake8Config
        
        content = Flake8Config.generate_setup_cfg_section()
        
        assert "[flake8]" in content
        assert "max-line-length = 120" in content


class TestLintRunner:
    """Test LintRunner class."""
    
    def test_lint_runner_creation(self):
        """Test LintRunner creation."""
        from src.code_quality.linting import LintRunner
        
        runner = LintRunner()
        
        assert runner.project_root is not None
        assert runner.results == []
    
    def test_lint_runner_get_summary(self):
        """Test LintRunner get_summary method."""
        from src.code_quality.linting import LintRunner
        
        runner = LintRunner()
        summary = runner.get_summary()
        
        assert "total_tools" in summary
        assert "all_passed" in summary
        assert "total_errors" in summary


class TestTypeCheckingEnums:
    """Test type checking enums."""
    
    def test_type_check_severity_enum(self):
        """Test TypeCheckSeverity enum values."""
        from src.code_quality.type_checking import TypeCheckSeverity
        
        assert TypeCheckSeverity.ERROR.value == "error"
        assert TypeCheckSeverity.WARNING.value == "warning"
        assert TypeCheckSeverity.NOTE.value == "note"


class TestTypeCheckIssue:
    """Test TypeCheckIssue dataclass."""
    
    def test_type_check_issue_creation(self):
        """Test TypeCheckIssue creation."""
        from src.code_quality.type_checking import TypeCheckIssue, TypeCheckSeverity
        
        issue = TypeCheckIssue(
            file_path="test.py",
            line=10,
            column=5,
            code="arg-type",
            message="Argument type mismatch",
            severity=TypeCheckSeverity.ERROR
        )
        
        assert issue.file_path == "test.py"
        assert issue.line == 10
        assert issue.severity == TypeCheckSeverity.ERROR


class TestMypyConfig:
    """Test MypyConfig class."""
    
    def test_mypy_config_default(self):
        """Test MypyConfig default configuration."""
        from src.code_quality.type_checking import MypyConfig
        
        config = MypyConfig.get_config_dict()
        
        assert "mypy" in config
        assert config["mypy"]["python_version"] == "3.10"
    
    def test_mypy_config_strict(self):
        """Test MypyConfig strict configuration."""
        from src.code_quality.type_checking import MypyConfig
        
        config = MypyConfig.get_config_dict(strict=True)
        
        assert config["mypy"]["strict"] == True
    
    def test_mypy_config_generate_ini(self):
        """Test MypyConfig generate_mypy_ini method."""
        from src.code_quality.type_checking import MypyConfig
        
        content = MypyConfig.generate_mypy_ini()
        
        assert "[mypy]" in content
        assert "python_version = 3.10" in content


class TestTypeCheckRunner:
    """Test TypeCheckRunner class."""
    
    def test_type_check_runner_creation(self):
        """Test TypeCheckRunner creation."""
        from src.code_quality.type_checking import TypeCheckRunner
        
        runner = TypeCheckRunner()
        
        assert runner.project_root is not None
        assert runner.results == []


class TestTypeStubManager:
    """Test TypeStubManager class."""
    
    def test_type_stub_manager_packages(self):
        """Test TypeStubManager get_stub_packages method."""
        from src.code_quality.type_checking import TypeStubManager
        
        packages = TypeStubManager.get_stub_packages()
        
        assert isinstance(packages, list)
        assert len(packages) > 0
    
    def test_type_stub_manager_custom_stubs(self):
        """Test TypeStubManager get_all_custom_stubs method."""
        from src.code_quality.type_checking import TypeStubManager
        
        stubs = TypeStubManager.get_all_custom_stubs()
        
        assert isinstance(stubs, dict)
        assert "MetaTrader5" in stubs


class TestPreCommitHooksEnums:
    """Test pre-commit hooks enums."""
    
    def test_hook_stage_enum(self):
        """Test HookStage enum values."""
        from src.code_quality.pre_commit_hooks import HookStage
        
        assert HookStage.PRE_COMMIT.value == "pre-commit"
        assert HookStage.PRE_PUSH.value == "pre-push"
        assert HookStage.COMMIT_MSG.value == "commit-msg"
    
    def test_hook_status_enum(self):
        """Test HookStatus enum values."""
        from src.code_quality.pre_commit_hooks import HookStatus
        
        assert HookStatus.PASSED.value == "passed"
        assert HookStatus.FAILED.value == "failed"
        assert HookStatus.SKIPPED.value == "skipped"


class TestHookResult:
    """Test HookResult dataclass."""
    
    def test_hook_result_creation(self):
        """Test HookResult creation."""
        from src.code_quality.pre_commit_hooks import HookResult, HookStage, HookStatus
        
        result = HookResult(
            hook_id="black",
            name="Black",
            stage=HookStage.PRE_COMMIT,
            status=HookStatus.PASSED
        )
        
        assert result.hook_id == "black"
        assert result.passed == True
    
    def test_hook_result_to_dict(self):
        """Test HookResult to_dict method."""
        from src.code_quality.pre_commit_hooks import HookResult, HookStage, HookStatus
        
        result = HookResult(
            hook_id="black",
            name="Black",
            stage=HookStage.PRE_COMMIT,
            status=HookStatus.PASSED
        )
        
        data = result.to_dict()
        assert data["hook_id"] == "black"
        assert data["status"] == "passed"


class TestPreCommitConfig:
    """Test PreCommitConfig class."""
    
    def test_pre_commit_config_repos(self):
        """Test PreCommitConfig get_repos method."""
        from src.code_quality.pre_commit_hooks import PreCommitConfig
        
        repos = PreCommitConfig.get_repos()
        
        assert isinstance(repos, list)
        assert len(repos) > 0
    
    def test_pre_commit_config_local_hooks(self):
        """Test PreCommitConfig get_local_hooks method."""
        from src.code_quality.pre_commit_hooks import PreCommitConfig
        
        hooks = PreCommitConfig.get_local_hooks()
        
        assert isinstance(hooks, list)
    
    def test_pre_commit_config_generate(self):
        """Test PreCommitConfig generate_pre_commit_config method."""
        from src.code_quality.pre_commit_hooks import PreCommitConfig
        
        content = PreCommitConfig.generate_pre_commit_config()
        
        assert "repos:" in content
        assert "pre-commit-hooks" in content


class TestGitHookInstaller:
    """Test GitHookInstaller class."""
    
    def test_git_hook_installer_creation(self):
        """Test GitHookInstaller creation."""
        from src.code_quality.pre_commit_hooks import GitHookInstaller
        
        installer = GitHookInstaller()
        
        assert installer.project_root is not None
        assert installer.hooks_dir is not None
    
    def test_git_hook_installer_hooks_content(self):
        """Test GitHookInstaller hook content."""
        from src.code_quality.pre_commit_hooks import GitHookInstaller
        
        assert "pre-commit" in GitHookInstaller.PRE_COMMIT_HOOK
        assert "pytest" in GitHookInstaller.PRE_PUSH_HOOK
        assert "commit_msg" in GitHookInstaller.COMMIT_MSG_HOOK


class TestReviewChecklistsEnums:
    """Test review checklists enums."""
    
    def test_checklist_category_enum(self):
        """Test ChecklistCategory enum values."""
        from src.code_quality.review_checklists import ChecklistCategory
        
        assert ChecklistCategory.FUNCTIONALITY.value == "functionality"
        assert ChecklistCategory.CODE_QUALITY.value == "code_quality"
        assert ChecklistCategory.SECURITY.value == "security"
        assert ChecklistCategory.TESTING.value == "testing"
    
    def test_checklist_priority_enum(self):
        """Test ChecklistPriority enum values."""
        from src.code_quality.review_checklists import ChecklistPriority
        
        assert ChecklistPriority.CRITICAL.value == "critical"
        assert ChecklistPriority.HIGH.value == "high"
        assert ChecklistPriority.MEDIUM.value == "medium"
        assert ChecklistPriority.LOW.value == "low"
    
    def test_checklist_status_enum(self):
        """Test ChecklistStatus enum values."""
        from src.code_quality.review_checklists import ChecklistStatus
        
        assert ChecklistStatus.PENDING.value == "pending"
        assert ChecklistStatus.PASSED.value == "passed"
        assert ChecklistStatus.FAILED.value == "failed"


class TestChecklistItem:
    """Test ChecklistItem dataclass."""
    
    def test_checklist_item_creation(self):
        """Test ChecklistItem creation."""
        from src.code_quality.review_checklists import ChecklistItem, ChecklistCategory, ChecklistPriority
        
        item = ChecklistItem(
            id="func_01",
            description="Code does what it's supposed to do",
            category=ChecklistCategory.FUNCTIONALITY,
            priority=ChecklistPriority.CRITICAL
        )
        
        assert item.id == "func_01"
        assert item.priority == ChecklistPriority.CRITICAL
    
    def test_checklist_item_mark_passed(self):
        """Test ChecklistItem mark_passed method."""
        from src.code_quality.review_checklists import ChecklistItem, ChecklistCategory, ChecklistStatus
        
        item = ChecklistItem(
            id="test",
            description="Test item",
            category=ChecklistCategory.FUNCTIONALITY
        )
        
        item.mark_passed("Verified")
        
        assert item.status == ChecklistStatus.PASSED
        assert item.notes == "Verified"
    
    def test_checklist_item_mark_failed(self):
        """Test ChecklistItem mark_failed method."""
        from src.code_quality.review_checklists import ChecklistItem, ChecklistCategory, ChecklistStatus
        
        item = ChecklistItem(
            id="test",
            description="Test item",
            category=ChecklistCategory.FUNCTIONALITY
        )
        
        item.mark_failed("Issue found")
        
        assert item.status == ChecklistStatus.FAILED
        assert item.notes == "Issue found"


class TestReviewChecklist:
    """Test ReviewChecklist dataclass."""
    
    def test_review_checklist_creation(self):
        """Test ReviewChecklist creation."""
        from src.code_quality.review_checklists import ReviewChecklist
        
        checklist = ReviewChecklist(
            name="Test Checklist",
            description="Test description"
        )
        
        assert checklist.name == "Test Checklist"
        assert checklist.total_items == 0
    
    def test_review_checklist_add_item(self):
        """Test ReviewChecklist add_item method."""
        from src.code_quality.review_checklists import ReviewChecklist, ChecklistItem, ChecklistCategory
        
        checklist = ReviewChecklist(name="Test", description="Test")
        item = ChecklistItem(id="test", description="Test", category=ChecklistCategory.FUNCTIONALITY)
        
        checklist.add_item(item)
        
        assert checklist.total_items == 1
    
    def test_review_checklist_properties(self):
        """Test ReviewChecklist properties."""
        from src.code_quality.review_checklists import ReviewChecklist, ChecklistItem, ChecklistCategory, ChecklistStatus
        
        checklist = ReviewChecklist(name="Test", description="Test")
        item1 = ChecklistItem(id="test1", description="Test 1", category=ChecklistCategory.FUNCTIONALITY)
        item2 = ChecklistItem(id="test2", description="Test 2", category=ChecklistCategory.FUNCTIONALITY)
        
        item1.status = ChecklistStatus.PASSED
        item2.status = ChecklistStatus.FAILED
        
        checklist.add_item(item1)
        checklist.add_item(item2)
        
        assert checklist.passed_items == 1
        assert checklist.failed_items == 1
        assert checklist.all_passed == False
    
    def test_review_checklist_to_markdown(self):
        """Test ReviewChecklist to_markdown method."""
        from src.code_quality.review_checklists import ReviewChecklist, ChecklistItem, ChecklistCategory
        
        checklist = ReviewChecklist(name="Test", description="Test")
        item = ChecklistItem(id="test", description="Test item", category=ChecklistCategory.FUNCTIONALITY)
        checklist.add_item(item)
        
        markdown = checklist.to_markdown()
        
        assert "# Test" in markdown
        assert "Test item" in markdown


class TestUniversalReviewChecklist:
    """Test UniversalReviewChecklist class."""
    
    def test_universal_checklist_creation(self):
        """Test UniversalReviewChecklist create_checklist method."""
        from src.code_quality.review_checklists import UniversalReviewChecklist
        
        checklist = UniversalReviewChecklist.create_checklist()
        
        assert checklist.name == "Universal Code Review Checklist"
        assert checklist.total_items > 0
    
    def test_universal_checklist_categories(self):
        """Test UniversalReviewChecklist has all categories."""
        from src.code_quality.review_checklists import UniversalReviewChecklist, ChecklistCategory
        
        checklist = UniversalReviewChecklist.create_checklist()
        categories = set(item.category for item in checklist.items)
        
        assert ChecklistCategory.FUNCTIONALITY in categories
        assert ChecklistCategory.CODE_QUALITY in categories
        assert ChecklistCategory.SECURITY in categories
        assert ChecklistCategory.TESTING in categories
        assert ChecklistCategory.DOCUMENTATION in categories


class TestPluginReviewChecklist:
    """Test PluginReviewChecklist class."""
    
    def test_plugin_checklist_creation(self):
        """Test PluginReviewChecklist create_checklist method."""
        from src.code_quality.review_checklists import PluginReviewChecklist
        
        checklist = PluginReviewChecklist.create_checklist(plugin_name="TestPlugin")
        
        assert "Plugin Review Checklist" in checklist.name
        assert checklist.total_items > 0


class TestSecurityReviewChecklist:
    """Test SecurityReviewChecklist class."""
    
    def test_security_checklist_creation(self):
        """Test SecurityReviewChecklist create_checklist method."""
        from src.code_quality.review_checklists import SecurityReviewChecklist
        
        checklist = SecurityReviewChecklist.create_checklist()
        
        assert checklist.name == "Security Review Checklist"
        assert checklist.total_items > 0


class TestChecklistGenerator:
    """Test ChecklistGenerator class."""
    
    def test_checklist_generator_types(self):
        """Test ChecklistGenerator get_all_checklist_types method."""
        from src.code_quality.review_checklists import ChecklistGenerator
        
        types = ChecklistGenerator.get_all_checklist_types()
        
        assert "universal" in types
        assert "plugin" in types
        assert "security" in types
        assert "full" in types
    
    def test_checklist_generator_create_by_type(self):
        """Test ChecklistGenerator create_checklist_by_type method."""
        from src.code_quality.review_checklists import ChecklistGenerator
        
        checklist = ChecklistGenerator.create_checklist_by_type("universal")
        
        assert checklist is not None
        assert checklist.total_items > 0
    
    def test_checklist_generator_full_checklist(self):
        """Test ChecklistGenerator create_full_review_checklist method."""
        from src.code_quality.review_checklists import ChecklistGenerator
        
        checklist = ChecklistGenerator.create_full_review_checklist(
            include_plugin=True,
            include_migration=True
        )
        
        assert checklist.name == "Full Code Review Checklist"
        assert checklist.total_items > 20


class TestComplexityAnalysisEnums:
    """Test complexity analysis enums."""
    
    def test_complexity_grade_enum(self):
        """Test ComplexityGrade enum values."""
        from src.code_quality.complexity_analysis import ComplexityGrade
        
        assert ComplexityGrade.A.value == "A"
        assert ComplexityGrade.B.value == "B"
        assert ComplexityGrade.C.value == "C"
        assert ComplexityGrade.F.value == "F"
    
    def test_maintainability_grade_enum(self):
        """Test MaintainabilityGrade enum values."""
        from src.code_quality.complexity_analysis import MaintainabilityGrade
        
        assert MaintainabilityGrade.A.value == "A"
        assert MaintainabilityGrade.B.value == "B"
        assert MaintainabilityGrade.C.value == "C"


class TestFunctionComplexity:
    """Test FunctionComplexity dataclass."""
    
    def test_function_complexity_creation(self):
        """Test FunctionComplexity creation."""
        from src.code_quality.complexity_analysis import FunctionComplexity
        
        func = FunctionComplexity(
            name="test_func",
            file_path="test.py",
            line_start=1,
            line_end=10,
            cyclomatic_complexity=5
        )
        
        assert func.name == "test_func"
        assert func.cyclomatic_complexity == 5
    
    def test_function_complexity_grade(self):
        """Test FunctionComplexity grade property."""
        from src.code_quality.complexity_analysis import FunctionComplexity, ComplexityGrade
        
        func_a = FunctionComplexity("f", "t.py", 1, 10, cyclomatic_complexity=3)
        func_c = FunctionComplexity("f", "t.py", 1, 10, cyclomatic_complexity=15)
        func_f = FunctionComplexity("f", "t.py", 1, 10, cyclomatic_complexity=50)
        
        assert func_a.grade == ComplexityGrade.A
        assert func_c.grade == ComplexityGrade.C
        assert func_f.grade == ComplexityGrade.F
    
    def test_function_complexity_is_complex(self):
        """Test FunctionComplexity is_complex property."""
        from src.code_quality.complexity_analysis import FunctionComplexity
        
        simple = FunctionComplexity("f", "t.py", 1, 10, cyclomatic_complexity=5)
        complex_func = FunctionComplexity("f", "t.py", 1, 10, cyclomatic_complexity=15)
        
        assert simple.is_complex == False
        assert complex_func.is_complex == True


class TestComplexityThresholds:
    """Test ComplexityThresholds class."""
    
    def test_complexity_thresholds_values(self):
        """Test ComplexityThresholds default values."""
        from src.code_quality.complexity_analysis import ComplexityThresholds
        
        assert ComplexityThresholds.MAX_CYCLOMATIC_COMPLEXITY == 15
        assert ComplexityThresholds.MAX_FUNCTION_LINES == 50
        assert ComplexityThresholds.MIN_MAINTAINABILITY_INDEX == 20.0
    
    def test_complexity_thresholds_get_thresholds(self):
        """Test ComplexityThresholds get_thresholds method."""
        from src.code_quality.complexity_analysis import ComplexityThresholds
        
        thresholds = ComplexityThresholds.get_thresholds()
        
        assert "max_cyclomatic_complexity" in thresholds
        assert "max_function_lines" in thresholds
    
    def test_complexity_thresholds_check_function(self):
        """Test ComplexityThresholds check_function method."""
        from src.code_quality.complexity_analysis import ComplexityThresholds, FunctionComplexity
        
        complex_func = FunctionComplexity("f", "t.py", 1, 100, cyclomatic_complexity=20, lines_of_code=60)
        
        violations = ComplexityThresholds.check_function(complex_func)
        
        assert len(violations) > 0


class TestComplexityAnalyzer:
    """Test ComplexityAnalyzer class."""
    
    def test_complexity_analyzer_creation(self):
        """Test ComplexityAnalyzer creation."""
        from src.code_quality.complexity_analysis import ComplexityAnalyzer
        
        analyzer = ComplexityAnalyzer()
        
        assert analyzer.project_root is not None


class TestSecurityScannerEnums:
    """Test security scanner enums."""
    
    def test_security_severity_enum(self):
        """Test SecuritySeverity enum values."""
        from src.code_quality.security_scanner import SecuritySeverity
        
        assert SecuritySeverity.CRITICAL.value == "critical"
        assert SecuritySeverity.HIGH.value == "high"
        assert SecuritySeverity.MEDIUM.value == "medium"
        assert SecuritySeverity.LOW.value == "low"
    
    def test_security_category_enum(self):
        """Test SecurityCategory enum values."""
        from src.code_quality.security_scanner import SecurityCategory
        
        assert SecurityCategory.HARDCODED_SECRET.value == "hardcoded_secret"
        assert SecurityCategory.SQL_INJECTION.value == "sql_injection"
        assert SecurityCategory.COMMAND_INJECTION.value == "command_injection"


class TestSecurityIssue:
    """Test SecurityIssue dataclass."""
    
    def test_security_issue_creation(self):
        """Test SecurityIssue creation."""
        from src.code_quality.security_scanner import SecurityIssue, SecuritySeverity, SecurityCategory
        
        issue = SecurityIssue(
            file_path="test.py",
            line=10,
            column=5,
            code="SECRET_KEY",
            message="Hardcoded secret detected",
            severity=SecuritySeverity.CRITICAL,
            category=SecurityCategory.HARDCODED_SECRET
        )
        
        assert issue.file_path == "test.py"
        assert issue.severity == SecuritySeverity.CRITICAL
    
    def test_security_issue_to_dict(self):
        """Test SecurityIssue to_dict method."""
        from src.code_quality.security_scanner import SecurityIssue, SecuritySeverity, SecurityCategory
        
        issue = SecurityIssue(
            file_path="test.py",
            line=10,
            column=5,
            code="SECRET_KEY",
            message="Hardcoded secret detected",
            severity=SecuritySeverity.CRITICAL,
            category=SecurityCategory.HARDCODED_SECRET
        )
        
        data = issue.to_dict()
        assert data["severity"] == "critical"
        assert data["category"] == "hardcoded_secret"


class TestSecurityScanResult:
    """Test SecurityScanResult dataclass."""
    
    def test_security_scan_result_creation(self):
        """Test SecurityScanResult creation."""
        from src.code_quality.security_scanner import SecurityScanResult
        
        result = SecurityScanResult()
        
        assert result.issues == []
        assert result.passed == True
    
    def test_security_scan_result_counts(self):
        """Test SecurityScanResult count properties."""
        from src.code_quality.security_scanner import SecurityScanResult, SecurityIssue, SecuritySeverity, SecurityCategory
        
        result = SecurityScanResult()
        result.issues = [
            SecurityIssue("t.py", 1, 0, "C1", "Critical", SecuritySeverity.CRITICAL, SecurityCategory.HARDCODED_SECRET),
            SecurityIssue("t.py", 2, 0, "H1", "High", SecuritySeverity.HIGH, SecurityCategory.SQL_INJECTION),
            SecurityIssue("t.py", 3, 0, "M1", "Medium", SecuritySeverity.MEDIUM, SecurityCategory.INSECURE_IMPORT),
        ]
        
        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.medium_count == 1
        assert result.has_critical_issues == True


class TestSecretPatterns:
    """Test SecretPatterns class."""
    
    def test_secret_patterns_get_patterns(self):
        """Test SecretPatterns get_patterns method."""
        from src.code_quality.security_scanner import SecretPatterns
        
        patterns = SecretPatterns.get_patterns()
        
        assert "api_key" in patterns
        assert "password" in patterns
        assert "token" in patterns
    
    def test_secret_patterns_scan_content(self):
        """Test SecretPatterns scan_content method."""
        from src.code_quality.security_scanner import SecretPatterns
        
        content = 'api_key = "sk_test_1234567890abcdefghij"'
        issues = SecretPatterns.scan_content(content, "test.py")
        
        assert len(issues) > 0


class TestSQLInjectionDetector:
    """Test SQLInjectionDetector class."""
    
    def test_sql_injection_detector_scan(self):
        """Test SQLInjectionDetector scan_content method."""
        from src.code_quality.security_scanner import SQLInjectionDetector
        
        content = 'cursor.execute("SELECT * FROM users WHERE id = " + user_id)'
        issues = SQLInjectionDetector.scan_content(content, "test.py")
        
        assert len(issues) > 0


class TestSecurityScanner:
    """Test SecurityScanner class."""
    
    def test_security_scanner_creation(self):
        """Test SecurityScanner creation."""
        from src.code_quality.security_scanner import SecurityScanner
        
        scanner = SecurityScanner()
        
        assert scanner.project_root is not None


class TestCICDIntegrationEnums:
    """Test CI/CD integration enums."""
    
    def test_ci_provider_enum(self):
        """Test CIProvider enum values."""
        from src.code_quality.ci_cd_integration import CIProvider
        
        assert CIProvider.GITHUB_ACTIONS.value == "github_actions"
        assert CIProvider.GITLAB_CI.value == "gitlab_ci"
        assert CIProvider.JENKINS.value == "jenkins"
    
    def test_quality_check_type_enum(self):
        """Test QualityCheckType enum values."""
        from src.code_quality.ci_cd_integration import QualityCheckType
        
        assert QualityCheckType.LINT.value == "lint"
        assert QualityCheckType.TYPE_CHECK.value == "type_check"
        assert QualityCheckType.SECURITY.value == "security"
        assert QualityCheckType.TESTS.value == "tests"
    
    def test_check_status_enum(self):
        """Test CheckStatus enum values."""
        from src.code_quality.ci_cd_integration import CheckStatus
        
        assert CheckStatus.PENDING.value == "pending"
        assert CheckStatus.PASSED.value == "passed"
        assert CheckStatus.FAILED.value == "failed"


class TestQualityCheckResult:
    """Test QualityCheckResult dataclass."""
    
    def test_quality_check_result_creation(self):
        """Test QualityCheckResult creation."""
        from src.code_quality.ci_cd_integration import QualityCheckResult, QualityCheckType, CheckStatus
        
        result = QualityCheckResult(
            check_type=QualityCheckType.LINT,
            status=CheckStatus.PASSED
        )
        
        assert result.check_type == QualityCheckType.LINT
        assert result.passed == True
    
    def test_quality_check_result_to_dict(self):
        """Test QualityCheckResult to_dict method."""
        from src.code_quality.ci_cd_integration import QualityCheckResult, QualityCheckType, CheckStatus
        
        result = QualityCheckResult(
            check_type=QualityCheckType.LINT,
            status=CheckStatus.PASSED
        )
        
        data = result.to_dict()
        assert data["check_type"] == "lint"
        assert data["passed"] == True


class TestQualitySuiteResult:
    """Test QualitySuiteResult dataclass."""
    
    def test_quality_suite_result_creation(self):
        """Test QualitySuiteResult creation."""
        from src.code_quality.ci_cd_integration import QualitySuiteResult
        
        result = QualitySuiteResult()
        
        assert result.checks == []
        assert result.total_checks == 0
    
    def test_quality_suite_result_properties(self):
        """Test QualitySuiteResult properties."""
        from src.code_quality.ci_cd_integration import QualitySuiteResult, QualityCheckResult, QualityCheckType, CheckStatus
        
        result = QualitySuiteResult()
        result.checks = [
            QualityCheckResult(QualityCheckType.LINT, CheckStatus.PASSED),
            QualityCheckResult(QualityCheckType.TESTS, CheckStatus.FAILED),
        ]
        
        assert result.total_checks == 2
        assert result.passed_checks == 1
        assert result.failed_checks == 1
        assert result.all_passed == False


class TestQualitySuiteRunner:
    """Test QualitySuiteRunner class."""
    
    def test_quality_suite_runner_creation(self):
        """Test QualitySuiteRunner creation."""
        from src.code_quality.ci_cd_integration import QualitySuiteRunner
        
        runner = QualitySuiteRunner()
        
        assert runner.project_root is not None


class TestGitHubActionsGenerator:
    """Test GitHubActionsGenerator class."""
    
    def test_github_actions_quality_workflow(self):
        """Test GitHubActionsGenerator generate_quality_workflow method."""
        from src.code_quality.ci_cd_integration import GitHubActionsGenerator
        
        workflow = GitHubActionsGenerator.generate_quality_workflow()
        
        assert "name: Code Quality" in workflow
        assert "flake8" in workflow
        assert "black" in workflow
    
    def test_github_actions_test_workflow(self):
        """Test GitHubActionsGenerator generate_test_workflow method."""
        from src.code_quality.ci_cd_integration import GitHubActionsGenerator
        
        workflow = GitHubActionsGenerator.generate_test_workflow()
        
        assert "name: Tests" in workflow
        assert "pytest" in workflow
    
    def test_github_actions_all_workflows(self):
        """Test GitHubActionsGenerator generate_all_workflows method."""
        from src.code_quality.ci_cd_integration import GitHubActionsGenerator
        
        workflows = GitHubActionsGenerator.generate_all_workflows()
        
        assert "quality.yml" in workflows
        assert "tests.yml" in workflows
        assert "pre-commit.yml" in workflows


class TestQualityGateEnforcer:
    """Test QualityGateEnforcer class."""
    
    def test_quality_gate_enforcer_creation(self):
        """Test QualityGateEnforcer creation."""
        from src.code_quality.ci_cd_integration import QualityGateEnforcer
        
        enforcer = QualityGateEnforcer()
        
        assert enforcer.gates is not None
    
    def test_quality_gate_enforcer_default_gates(self):
        """Test QualityGateEnforcer get_default_gates method."""
        from src.code_quality.ci_cd_integration import QualityGateEnforcer
        
        gates = QualityGateEnforcer.get_default_gates()
        
        assert "lint_passed" in gates
        assert "tests_passed" in gates
        assert "coverage_min" in gates


class TestCIConfigGenerator:
    """Test CIConfigGenerator class."""
    
    def test_ci_config_generator_gitlab(self):
        """Test CIConfigGenerator generate_gitlab_ci method."""
        from src.code_quality.ci_cd_integration import CIConfigGenerator
        
        config = CIConfigGenerator.generate_gitlab_ci()
        
        assert "stages:" in config
        assert "quality:" in config
        assert "test:" in config
    
    def test_ci_config_generator_azure(self):
        """Test CIConfigGenerator generate_azure_pipelines method."""
        from src.code_quality.ci_cd_integration import CIConfigGenerator
        
        config = CIConfigGenerator.generate_azure_pipelines()
        
        assert "trigger:" in config
        assert "pytest" in config


class TestDocument13Integration:
    """Test Document 13 integration."""
    
    def test_all_modules_importable(self):
        """Test that all modules are importable."""
        from src.code_quality import linting
        from src.code_quality import type_checking
        from src.code_quality import pre_commit_hooks
        from src.code_quality import review_checklists
        from src.code_quality import complexity_analysis
        from src.code_quality import security_scanner
        from src.code_quality import ci_cd_integration
        
        assert linting is not None
        assert type_checking is not None
        assert pre_commit_hooks is not None
        assert review_checklists is not None
        assert complexity_analysis is not None
        assert security_scanner is not None
        assert ci_cd_integration is not None
    
    def test_package_version(self):
        """Test package version."""
        from src.code_quality import __version__
        
        assert __version__ == "1.0.0"
    
    def test_linting_tools_coverage(self):
        """Test that all linting tools are covered."""
        from src.code_quality.linting import LintTool
        
        tools = [t.value for t in LintTool]
        
        assert "pylint" in tools
        assert "flake8" in tools
        assert "black" in tools
        assert "isort" in tools
        assert "mypy" in tools
    
    def test_checklist_categories_coverage(self):
        """Test that all checklist categories from Document 13 are covered."""
        from src.code_quality.review_checklists import ChecklistCategory
        
        categories = [c.value for c in ChecklistCategory]
        
        assert "functionality" in categories
        assert "code_quality" in categories
        assert "security" in categories
        assert "testing" in categories
        assert "documentation" in categories


class TestDocument13Summary:
    """Test Document 13 summary verification."""
    
    def test_document_13_requirements_met(self):
        """Test that all Document 13 requirements are met."""
        from src.code_quality import (
            PylintConfig,
            BlackConfig,
            IsortConfig,
            Flake8Config,
            MypyConfig,
            PreCommitConfig,
            UniversalReviewChecklist,
            SecurityReviewChecklist,
            ComplexityAnalyzer,
            SecurityScanner,
            GitHubActionsGenerator,
        )
        
        assert PylintConfig.get_config_dict() is not None
        assert BlackConfig.get_config_dict() is not None
        assert IsortConfig.get_config_dict() is not None
        assert Flake8Config.get_config_dict() is not None
        assert MypyConfig.get_config_dict() is not None
        assert PreCommitConfig.get_repos() is not None
        assert UniversalReviewChecklist.create_checklist() is not None
        assert SecurityReviewChecklist.create_checklist() is not None
        assert ComplexityAnalyzer() is not None
        assert SecurityScanner() is not None
        assert GitHubActionsGenerator.generate_all_workflows() is not None
    
    def test_linting_configurations_complete(self):
        """Test that linting configurations are complete."""
        from src.code_quality.linting import generate_all_configs
        
        configs = generate_all_configs(".")
        
        assert ".pylintrc" in configs
        assert "pyproject_lint_section.toml" in configs
        assert "setup_flake8_section.cfg" in configs
    
    def test_type_checking_configuration_complete(self):
        """Test that type checking configuration is complete."""
        from src.code_quality.type_checking import generate_type_config
        
        configs = generate_type_config(".")
        
        assert "mypy.ini" in configs
        assert "pyproject_mypy_section.toml" in configs
    
    def test_pre_commit_hooks_complete(self):
        """Test that pre-commit hooks are complete."""
        from src.code_quality.pre_commit_hooks import PreCommitConfig
        
        repos = PreCommitConfig.get_repos()
        
        repo_urls = [r.repo for r in repos]
        assert any("pre-commit-hooks" in url for url in repo_urls)
        assert any("black" in url for url in repo_urls)
        assert any("isort" in url for url in repo_urls)
        assert any("flake8" in url for url in repo_urls)
        assert any("mypy" in url for url in repo_urls)
        assert any("bandit" in url for url in repo_urls)
    
    def test_review_checklists_complete(self):
        """Test that review checklists are complete."""
        from src.code_quality.review_checklists import ChecklistGenerator
        
        types = ChecklistGenerator.get_all_checklist_types()
        
        assert "universal" in types
        assert "plugin" in types
        assert "security" in types
        assert "performance" in types
        assert "test" in types
        assert "migration" in types
        assert "approval" in types
        assert "full" in types
    
    def test_complexity_analysis_complete(self):
        """Test that complexity analysis is complete."""
        from src.code_quality.complexity_analysis import ComplexityThresholds
        
        thresholds = ComplexityThresholds.get_thresholds()
        
        assert "max_cyclomatic_complexity" in thresholds
        assert "max_cognitive_complexity" in thresholds
        assert "max_function_lines" in thresholds
        assert "max_function_parameters" in thresholds
        assert "min_maintainability_index" in thresholds
    
    def test_security_scanning_complete(self):
        """Test that security scanning is complete."""
        from src.code_quality.security_scanner import SecretPatterns, SecurityCategory
        
        patterns = SecretPatterns.get_patterns()
        categories = [c.value for c in SecurityCategory]
        
        assert "api_key" in patterns
        assert "password" in patterns
        assert "token" in patterns
        assert "hardcoded_secret" in categories
        assert "sql_injection" in categories
        assert "command_injection" in categories
    
    def test_ci_cd_integration_complete(self):
        """Test that CI/CD integration is complete."""
        from src.code_quality.ci_cd_integration import CIProvider, GitHubActionsGenerator
        
        providers = [p.value for p in CIProvider]
        workflows = GitHubActionsGenerator.generate_all_workflows()
        
        assert "github_actions" in providers
        assert "gitlab_ci" in providers
        assert len(workflows) >= 3
