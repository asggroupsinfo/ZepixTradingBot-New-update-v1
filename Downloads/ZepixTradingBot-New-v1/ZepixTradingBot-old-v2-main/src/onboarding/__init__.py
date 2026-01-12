"""
Onboarding Package for V5 Hybrid Plugin Architecture.

This package provides developer onboarding tools:
- Environment setup scripts
- VS Code configuration
- Git hooks management
- DevContainer support
- Onboarding CLI tool

Based on Document 15: DEVELOPER_ONBOARDING.md

Version: 1.0
Date: 2026-01-12
"""

from src.onboarding.setup_manager import (
    SetupStep,
    SetupStatus,
    SetupResult,
    OnboardingChecklist,
    SetupScriptGenerator,
    VSCodeConfigGenerator,
    GitHooksManager,
    DevContainerGenerator,
    OnboardingChecklistGenerator,
    EnvironmentVerifier,
    DeveloperSetupManager,
    setup_developer_environment,
)

from src.onboarding.cli_tool import (
    CheckStatus,
    CheckResult,
    OnboardingReport,
    EnvironmentChecker,
    OnboardingCLI,
    create_argument_parser,
    main as cli_main,
)

__version__ = "1.0.0"

__all__ = [
    # Setup Manager
    "SetupStep",
    "SetupStatus",
    "SetupResult",
    "OnboardingChecklist",
    "SetupScriptGenerator",
    "VSCodeConfigGenerator",
    "GitHooksManager",
    "DevContainerGenerator",
    "OnboardingChecklistGenerator",
    "EnvironmentVerifier",
    "DeveloperSetupManager",
    "setup_developer_environment",
    
    # CLI Tool
    "CheckStatus",
    "CheckResult",
    "OnboardingReport",
    "EnvironmentChecker",
    "OnboardingCLI",
    "create_argument_parser",
    "cli_main",
]
