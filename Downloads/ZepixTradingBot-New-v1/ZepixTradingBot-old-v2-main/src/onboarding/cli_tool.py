"""
Onboarding CLI Tool for V5 Hybrid Plugin Architecture.

This module provides an interactive command-line tool for:
- Verifying development environment setup
- Running onboarding checklist
- Generating configuration files
- Installing Git hooks

Based on Document 15: DEVELOPER_ONBOARDING.md

Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class CheckStatus(Enum):
    """Status of a check."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details
        }


@dataclass
class OnboardingReport:
    """Report of onboarding verification."""
    checks: List[CheckResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def passed(self) -> int:
        """Count of passed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.PASS)
    
    @property
    def failed(self) -> int:
        """Count of failed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)
    
    @property
    def warnings(self) -> int:
        """Count of warnings."""
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)
    
    @property
    def all_passed(self) -> bool:
        """Check if all required checks passed."""
        return self.failed == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "total": len(self.checks)
            }
        }


class EnvironmentChecker:
    """Checker for development environment."""
    
    @staticmethod
    def check_python_version() -> CheckResult:
        """Check Python version."""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major >= 3 and version.minor >= 9:
            return CheckResult(
                name="Python Version",
                status=CheckStatus.PASS,
                message=f"Python {version_str} detected"
            )
        return CheckResult(
            name="Python Version",
            status=CheckStatus.FAIL,
            message=f"Python 3.9+ required, found {version_str}"
        )
    
    @staticmethod
    def check_virtual_environment() -> CheckResult:
        """Check if running in virtual environment."""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            return CheckResult(
                name="Virtual Environment",
                status=CheckStatus.PASS,
                message="Running in virtual environment"
            )
        return CheckResult(
            name="Virtual Environment",
            status=CheckStatus.WARN,
            message="Not running in virtual environment",
            details="Consider creating a venv: python -m venv venv"
        )
    
    @staticmethod
    def check_directory_structure(project_root: str) -> CheckResult:
        """Check project directory structure."""
        required_dirs = ['src', 'config', 'tests']
        missing = []
        
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(project_root, dir_name)):
                missing.append(dir_name)
        
        if not missing:
            return CheckResult(
                name="Directory Structure",
                status=CheckStatus.PASS,
                message="All required directories present"
            )
        return CheckResult(
            name="Directory Structure",
            status=CheckStatus.FAIL,
            message=f"Missing directories: {', '.join(missing)}",
            details="Run setup script to create directories"
        )
    
    @staticmethod
    def check_config_file(project_root: str) -> CheckResult:
        """Check if config file exists."""
        config_path = os.path.join(project_root, 'config', 'config.json')
        
        if os.path.exists(config_path):
            return CheckResult(
                name="Configuration File",
                status=CheckStatus.PASS,
                message="config.json found"
            )
        
        template_path = os.path.join(project_root, 'config', 'config.template.json')
        if os.path.exists(template_path):
            return CheckResult(
                name="Configuration File",
                status=CheckStatus.WARN,
                message="config.json not found, template available",
                details="Copy template: cp config/config.template.json config/config.json"
            )
        
        return CheckResult(
            name="Configuration File",
            status=CheckStatus.WARN,
            message="No configuration file found"
        )
    
    @staticmethod
    def check_git_repository(project_root: str) -> CheckResult:
        """Check if in Git repository."""
        git_dir = os.path.join(project_root, '.git')
        
        if os.path.exists(git_dir):
            return CheckResult(
                name="Git Repository",
                status=CheckStatus.PASS,
                message="Git repository detected"
            )
        return CheckResult(
            name="Git Repository",
            status=CheckStatus.WARN,
            message="Not a Git repository",
            details="Initialize with: git init"
        )
    
    @staticmethod
    def check_vscode_config(project_root: str) -> CheckResult:
        """Check VS Code configuration."""
        vscode_dir = os.path.join(project_root, '.vscode')
        
        if os.path.exists(vscode_dir):
            settings_path = os.path.join(vscode_dir, 'settings.json')
            if os.path.exists(settings_path):
                return CheckResult(
                    name="VS Code Configuration",
                    status=CheckStatus.PASS,
                    message="VS Code settings found"
                )
        return CheckResult(
            name="VS Code Configuration",
            status=CheckStatus.WARN,
            message="VS Code configuration not found",
            details="Run setup to generate .vscode configs"
        )
    
    @staticmethod
    def check_pre_commit_config(project_root: str) -> CheckResult:
        """Check pre-commit configuration."""
        config_path = os.path.join(project_root, '.pre-commit-config.yaml')
        
        if os.path.exists(config_path):
            return CheckResult(
                name="Pre-commit Hooks",
                status=CheckStatus.PASS,
                message="Pre-commit configuration found"
            )
        return CheckResult(
            name="Pre-commit Hooks",
            status=CheckStatus.WARN,
            message="Pre-commit configuration not found",
            details="Run setup to generate pre-commit config"
        )
    
    @classmethod
    def run_all_checks(cls, project_root: str) -> OnboardingReport:
        """Run all environment checks."""
        report = OnboardingReport()
        
        report.checks.append(cls.check_python_version())
        report.checks.append(cls.check_virtual_environment())
        report.checks.append(cls.check_directory_structure(project_root))
        report.checks.append(cls.check_config_file(project_root))
        report.checks.append(cls.check_git_repository(project_root))
        report.checks.append(cls.check_vscode_config(project_root))
        report.checks.append(cls.check_pre_commit_config(project_root))
        
        return report


class OnboardingCLI:
    """Interactive CLI for developer onboarding."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize CLI."""
        self.project_root = project_root or os.getcwd()
    
    def print_header(self) -> None:
        """Print CLI header."""
        print("=" * 50)
        print("  Zepix Trading Bot - Developer Onboarding")
        print("=" * 50)
        print()
    
    def print_check_result(self, result: CheckResult) -> None:
        """Print a check result."""
        status_icons = {
            CheckStatus.PASS: "[PASS]",
            CheckStatus.FAIL: "[FAIL]",
            CheckStatus.WARN: "[WARN]",
            CheckStatus.SKIP: "[SKIP]"
        }
        
        icon = status_icons.get(result.status, "[????]")
        print(f"  {icon} {result.name}: {result.message}")
        
        if result.details:
            print(f"         -> {result.details}")
    
    def print_summary(self, report: OnboardingReport) -> None:
        """Print report summary."""
        print()
        print("-" * 50)
        print(f"  Summary: {report.passed} passed, {report.failed} failed, {report.warnings} warnings")
        print("-" * 50)
        
        if report.all_passed:
            print()
            print("  Your development environment is ready!")
            print()
        else:
            print()
            print("  Please fix the failed checks before proceeding.")
            print()
    
    def run_verification(self) -> OnboardingReport:
        """Run environment verification."""
        self.print_header()
        print("Running environment checks...")
        print()
        
        report = EnvironmentChecker.run_all_checks(self.project_root)
        
        for check in report.checks:
            self.print_check_result(check)
        
        self.print_summary(report)
        
        return report
    
    def show_checklist(self) -> None:
        """Show onboarding checklist."""
        self.print_header()
        print("Developer Onboarding Checklist:")
        print()
        
        checklist = [
            ("Development environment setup", "Run setup_dev.sh or setup_dev.bat"),
            ("Bot runs successfully", "Run: python src/main.py"),
            ("Understand plugin architecture", "Read: docs/PLUGIN_DEVELOPER_GUIDE.md"),
            ("Created first plugin", "Copy hello_world plugin and modify"),
            ("Wrote unit tests", "Create tests in tests/ directory"),
            ("Read code review guidelines", "Read: docs/API_REFERENCE.md"),
            ("Joined developer community", "Contact team lead for access"),
        ]
        
        for i, (item, hint) in enumerate(checklist, 1):
            print(f"  [ ] {i}. {item}")
            print(f"       Hint: {hint}")
            print()
    
    def generate_configs(self) -> None:
        """Generate configuration files."""
        self.print_header()
        print("Generating configuration files...")
        print()
        
        from src.onboarding.setup_manager import (
            SetupScriptGenerator,
            VSCodeConfigGenerator,
            GitHooksManager,
            DevContainerGenerator
        )
        
        scripts_dir = os.path.join(self.project_root, "scripts")
        scripts = SetupScriptGenerator.save_scripts(scripts_dir)
        for name, path in scripts.items():
            print(f"  [OK] Generated: {name}")
        
        vscode_dir = os.path.join(self.project_root, ".vscode")
        configs = VSCodeConfigGenerator.save_configs(vscode_dir)
        for name, path in configs.items():
            print(f"  [OK] Generated: .vscode/{name}")
        
        hooks = GitHooksManager.save_hooks(self.project_root)
        for name, path in hooks.items():
            print(f"  [OK] Generated: {name}")
        
        devcontainer_dir = os.path.join(self.project_root, ".devcontainer")
        devcontainer = DevContainerGenerator.save_configs(devcontainer_dir)
        for name, path in devcontainer.items():
            print(f"  [OK] Generated: .devcontainer/{name}")
        
        print()
        print("Configuration files generated successfully!")
        print()


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="onboarding",
        description="Zepix Trading Bot - Developer Onboarding Tool"
    )
    
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="Project root directory (default: current directory)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    subparsers.add_parser("verify", help="Verify development environment")
    subparsers.add_parser("checklist", help="Show onboarding checklist")
    subparsers.add_parser("generate", help="Generate configuration files")
    subparsers.add_parser("all", help="Run all onboarding steps")
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for CLI."""
    parser = create_argument_parser()
    parsed_args = parser.parse_args(args)
    
    cli = OnboardingCLI(parsed_args.project_root)
    
    if parsed_args.command == "verify":
        report = cli.run_verification()
        return 0 if report.all_passed else 1
    
    elif parsed_args.command == "checklist":
        cli.show_checklist()
        return 0
    
    elif parsed_args.command == "generate":
        cli.generate_configs()
        return 0
    
    elif parsed_args.command == "all":
        cli.generate_configs()
        print()
        report = cli.run_verification()
        print()
        cli.show_checklist()
        return 0 if report.all_passed else 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
