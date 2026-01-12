"""
Code Quality Package for V5 Hybrid Plugin Architecture.

This package provides comprehensive code quality and review tools:
- Linting & Formatting (pylint, black, isort, flake8)
- Type Checking (mypy)
- Pre-commit Hooks
- Review Checklists
- Complexity Analysis
- Security Scanning
- CI/CD Integration

Based on Document 13: CODE_REVIEW_GUIDELINES.md

Version: 1.0
Date: 2026-01-12
"""

from src.code_quality.linting import (
    LintSeverity,
    LintTool,
    LintIssue,
    LintResult,
    PylintConfig,
    BlackConfig,
    IsortConfig,
    Flake8Config,
    LintRunner,
    generate_all_configs,
)

from src.code_quality.type_checking import (
    TypeCheckSeverity,
    TypeCheckIssue,
    TypeCheckResult,
    MypyConfig,
    TypeCheckRunner,
    TypeStubManager,
    generate_type_config,
)

from src.code_quality.pre_commit_hooks import (
    HookStage,
    HookStatus,
    HookResult,
    PreCommitResult,
    PreCommitHook,
    PreCommitRepo,
    PreCommitConfig,
    GitHookInstaller,
    PreCommitRunner,
    generate_pre_commit_config,
)

from src.code_quality.review_checklists import (
    ChecklistCategory,
    ChecklistPriority,
    ChecklistStatus,
    ChecklistItem,
    ReviewChecklist,
    UniversalReviewChecklist,
    PluginReviewChecklist,
    SecurityReviewChecklist,
    PerformanceReviewChecklist,
    TestReviewChecklist,
    MigrationReviewChecklist,
    ApprovalChecklist,
    ChecklistGenerator,
    generate_pr_checklist_comment,
)

from src.code_quality.complexity_analysis import (
    ComplexityGrade,
    MaintainabilityGrade,
    FunctionComplexity,
    ClassComplexity,
    FileComplexity,
    ProjectComplexity,
    ComplexityThresholds,
    ComplexityVisitor,
    ComplexityAnalyzer,
    RadonRunner,
    analyze_complexity,
    generate_complexity_report,
)

from src.code_quality.security_scanner import (
    SecuritySeverity,
    SecurityCategory,
    SecurityIssue,
    SecurityScanResult,
    SecretPatterns,
    SQLInjectionDetector,
    PluginSandboxChecker,
    SensitiveDataChecker,
    SecurityScanner,
    BanditRunner,
    scan_security,
    generate_security_report,
)

from src.code_quality.ci_cd_integration import (
    CIProvider,
    QualityCheckType,
    CheckStatus,
    QualityCheckResult,
    QualitySuiteResult,
    QualitySuiteRunner,
    GitHubActionsGenerator,
    QualityGateEnforcer,
    CIConfigGenerator,
    run_quality_suite,
    generate_ci_config,
    generate_quality_report,
)

__version__ = "1.0.0"

__all__ = [
    # Linting
    "LintSeverity",
    "LintTool",
    "LintIssue",
    "LintResult",
    "PylintConfig",
    "BlackConfig",
    "IsortConfig",
    "Flake8Config",
    "LintRunner",
    "generate_all_configs",
    
    # Type Checking
    "TypeCheckSeverity",
    "TypeCheckIssue",
    "TypeCheckResult",
    "MypyConfig",
    "TypeCheckRunner",
    "TypeStubManager",
    "generate_type_config",
    
    # Pre-commit Hooks
    "HookStage",
    "HookStatus",
    "HookResult",
    "PreCommitResult",
    "PreCommitHook",
    "PreCommitRepo",
    "PreCommitConfig",
    "GitHookInstaller",
    "PreCommitRunner",
    "generate_pre_commit_config",
    
    # Review Checklists
    "ChecklistCategory",
    "ChecklistPriority",
    "ChecklistStatus",
    "ChecklistItem",
    "ReviewChecklist",
    "UniversalReviewChecklist",
    "PluginReviewChecklist",
    "SecurityReviewChecklist",
    "PerformanceReviewChecklist",
    "TestReviewChecklist",
    "MigrationReviewChecklist",
    "ApprovalChecklist",
    "ChecklistGenerator",
    "generate_pr_checklist_comment",
    
    # Complexity Analysis
    "ComplexityGrade",
    "MaintainabilityGrade",
    "FunctionComplexity",
    "ClassComplexity",
    "FileComplexity",
    "ProjectComplexity",
    "ComplexityThresholds",
    "ComplexityVisitor",
    "ComplexityAnalyzer",
    "RadonRunner",
    "analyze_complexity",
    "generate_complexity_report",
    
    # Security Scanning
    "SecuritySeverity",
    "SecurityCategory",
    "SecurityIssue",
    "SecurityScanResult",
    "SecretPatterns",
    "SQLInjectionDetector",
    "PluginSandboxChecker",
    "SensitiveDataChecker",
    "SecurityScanner",
    "BanditRunner",
    "scan_security",
    "generate_security_report",
    
    # CI/CD Integration
    "CIProvider",
    "QualityCheckType",
    "CheckStatus",
    "QualityCheckResult",
    "QualitySuiteResult",
    "QualitySuiteRunner",
    "GitHubActionsGenerator",
    "QualityGateEnforcer",
    "CIConfigGenerator",
    "run_quality_suite",
    "generate_ci_config",
    "generate_quality_report",
]
