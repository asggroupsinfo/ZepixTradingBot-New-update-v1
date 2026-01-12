"""
Review Checklists for V5 Hybrid Plugin Architecture.

This module provides automated code review checklists:
- Universal code review checklist
- Plugin-specific review checklist
- Security review checklist
- Performance review checklist
- Test review checklist
- Documentation review checklist

Based on Document 13: CODE_REVIEW_GUIDELINES.md

Version: 1.0
Date: 2026-01-12
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import json


class ChecklistCategory(Enum):
    """Checklist categories."""
    FUNCTIONALITY = "functionality"
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PLUGIN_STRUCTURE = "plugin_structure"
    PLUGIN_CODE = "plugin_code"
    SERVICE_API_USAGE = "service_api_usage"
    SECRETS_MANAGEMENT = "secrets_management"
    DATA_ACCESS = "data_access"
    PLUGIN_SANDBOXING = "plugin_sandboxing"
    EFFICIENCY = "efficiency"
    RESOURCE_USAGE = "resource_usage"
    TEST_QUALITY = "test_quality"
    MIGRATION = "migration"
    APPROVAL = "approval"


class ChecklistPriority(Enum):
    """Checklist item priority."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ChecklistStatus(Enum):
    """Checklist item status."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ChecklistItem:
    """Single checklist item."""
    id: str
    description: str
    category: ChecklistCategory
    priority: ChecklistPriority = ChecklistPriority.MEDIUM
    status: ChecklistStatus = ChecklistStatus.PENDING
    notes: str = ""
    automated: bool = False
    
    def mark_passed(self, notes: str = "") -> None:
        """Mark item as passed."""
        self.status = ChecklistStatus.PASSED
        if notes:
            self.notes = notes
    
    def mark_failed(self, notes: str = "") -> None:
        """Mark item as failed."""
        self.status = ChecklistStatus.FAILED
        if notes:
            self.notes = notes
    
    def mark_skipped(self, notes: str = "") -> None:
        """Mark item as skipped."""
        self.status = ChecklistStatus.SKIPPED
        if notes:
            self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "notes": self.notes,
            "automated": self.automated
        }


@dataclass
class ReviewChecklist:
    """Complete review checklist."""
    name: str
    description: str
    items: List[ChecklistItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    reviewer: str = ""
    pr_number: Optional[int] = None
    
    @property
    def total_items(self) -> int:
        """Get total number of items."""
        return len(self.items)
    
    @property
    def passed_items(self) -> int:
        """Get number of passed items."""
        return sum(1 for i in self.items if i.status == ChecklistStatus.PASSED)
    
    @property
    def failed_items(self) -> int:
        """Get number of failed items."""
        return sum(1 for i in self.items if i.status == ChecklistStatus.FAILED)
    
    @property
    def pending_items(self) -> int:
        """Get number of pending items."""
        return sum(1 for i in self.items if i.status == ChecklistStatus.PENDING)
    
    @property
    def critical_failed(self) -> int:
        """Get number of failed critical items."""
        return sum(1 for i in self.items 
                   if i.status == ChecklistStatus.FAILED and i.priority == ChecklistPriority.CRITICAL)
    
    @property
    def all_passed(self) -> bool:
        """Check if all items passed."""
        return all(i.status in [ChecklistStatus.PASSED, ChecklistStatus.SKIPPED, ChecklistStatus.NOT_APPLICABLE] 
                   for i in self.items)
    
    @property
    def approval_ready(self) -> bool:
        """Check if ready for approval (no critical failures, < 3 minor issues)."""
        if self.critical_failed > 0:
            return False
        minor_failures = sum(1 for i in self.items 
                            if i.status == ChecklistStatus.FAILED 
                            and i.priority in [ChecklistPriority.LOW, ChecklistPriority.MEDIUM])
        return minor_failures < 3
    
    def add_item(self, item: ChecklistItem) -> None:
        """Add item to checklist."""
        self.items.append(item)
    
    def get_items_by_category(self, category: ChecklistCategory) -> List[ChecklistItem]:
        """Get items by category."""
        return [i for i in self.items if i.category == category]
    
    def get_items_by_status(self, status: ChecklistStatus) -> List[ChecklistItem]:
        """Get items by status."""
        return [i for i in self.items if i.status == status]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "total_items": self.total_items,
            "passed_items": self.passed_items,
            "failed_items": self.failed_items,
            "pending_items": self.pending_items,
            "all_passed": self.all_passed,
            "approval_ready": self.approval_ready,
            "reviewer": self.reviewer,
            "pr_number": self.pr_number,
            "created_at": self.created_at.isoformat(),
            "items": [i.to_dict() for i in self.items]
        }
    
    def to_markdown(self) -> str:
        """Generate markdown representation."""
        lines = [
            f"# {self.name}",
            "",
            f"**Description:** {self.description}",
            f"**Reviewer:** {self.reviewer or 'Not assigned'}",
            f"**PR:** #{self.pr_number}" if self.pr_number else "",
            f"**Created:** {self.created_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            f"**Progress:** {self.passed_items}/{self.total_items} passed",
            f"**Status:** {'Ready for Approval' if self.approval_ready else 'Needs Work'}",
            "",
        ]
        
        categories_seen = set()
        for item in self.items:
            if item.category not in categories_seen:
                categories_seen.add(item.category)
                lines.append(f"## {item.category.value.replace('_', ' ').title()}")
                lines.append("")
            
            status_icon = {
                ChecklistStatus.PASSED: "[x]",
                ChecklistStatus.FAILED: "[ ] FAILED:",
                ChecklistStatus.PENDING: "[ ]",
                ChecklistStatus.SKIPPED: "[-]",
                ChecklistStatus.NOT_APPLICABLE: "[N/A]",
            }.get(item.status, "[ ]")
            
            priority_badge = ""
            if item.priority == ChecklistPriority.CRITICAL:
                priority_badge = " **[CRITICAL]**"
            elif item.priority == ChecklistPriority.HIGH:
                priority_badge = " *[HIGH]*"
            
            lines.append(f"- {status_icon} {item.description}{priority_badge}")
            if item.notes:
                lines.append(f"  - Note: {item.notes}")
        
        return "\n".join(lines)


class UniversalReviewChecklist:
    """Generator for universal code review checklist."""
    
    FUNCTIONALITY_ITEMS = [
        ("func_01", "Code does what it's supposed to do", ChecklistPriority.CRITICAL),
        ("func_02", "All edge cases handled", ChecklistPriority.HIGH),
        ("func_03", "Error handling comprehensive", ChecklistPriority.CRITICAL),
        ("func_04", "No logic regressions", ChecklistPriority.CRITICAL),
    ]
    
    CODE_QUALITY_ITEMS = [
        ("quality_01", "Follows PEP 8 style guide", ChecklistPriority.MEDIUM, True),
        ("quality_02", "Functions < 50 lines", ChecklistPriority.MEDIUM, True),
        ("quality_03", "Classes have single responsibility", ChecklistPriority.HIGH),
        ("quality_04", "No code duplication", ChecklistPriority.MEDIUM),
        ("quality_05", "Magic numbers replaced with constants", ChecklistPriority.LOW),
    ]
    
    SECURITY_ITEMS = [
        ("sec_01", "No hardcoded credentials", ChecklistPriority.CRITICAL, True),
        ("sec_02", "SQL injection prevention (parameterized queries)", ChecklistPriority.CRITICAL),
        ("sec_03", "Input validation present", ChecklistPriority.HIGH),
        ("sec_04", "Sensitive data not logged", ChecklistPriority.CRITICAL),
    ]
    
    TESTING_ITEMS = [
        ("test_01", "Unit tests added/updated", ChecklistPriority.HIGH),
        ("test_02", "Test coverage > 80%", ChecklistPriority.MEDIUM, True),
        ("test_03", "Tests actually test the logic", ChecklistPriority.HIGH),
        ("test_04", "No commented-out test code", ChecklistPriority.LOW),
    ]
    
    DOCUMENTATION_ITEMS = [
        ("doc_01", "Docstrings for all public methods", ChecklistPriority.MEDIUM),
        ("doc_02", "Complex logic has inline comments", ChecklistPriority.LOW),
        ("doc_03", "README updated if needed", ChecklistPriority.LOW),
        ("doc_04", "API docs updated", ChecklistPriority.MEDIUM),
    ]
    
    @classmethod
    def create_checklist(cls, reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create universal review checklist."""
        checklist = ReviewChecklist(
            name="Universal Code Review Checklist",
            description="Standard code review checklist for all PRs",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.FUNCTIONALITY_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.FUNCTIONALITY,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.CODE_QUALITY_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.CODE_QUALITY,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.SECURITY_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.SECURITY,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.TESTING_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.TESTING,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.DOCUMENTATION_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.DOCUMENTATION,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class PluginReviewChecklist:
    """Generator for plugin-specific review checklist."""
    
    STRUCTURE_ITEMS = [
        ("plugin_struct_01", "Follows template structure", ChecklistPriority.HIGH),
        ("plugin_struct_02", "config.json properly formatted", ChecklistPriority.HIGH, True),
        ("plugin_struct_03", "README.md explains plugin purpose", ChecklistPriority.MEDIUM),
        ("plugin_struct_04", "Version number semantic (1.0.0)", ChecklistPriority.LOW),
    ]
    
    CODE_ITEMS = [
        ("plugin_code_01", "Extends BaseLogicPlugin correctly", ChecklistPriority.CRITICAL),
        ("plugin_code_02", "Clear docstrings on all methods", ChecklistPriority.MEDIUM),
        ("plugin_code_03", "No hardcoded values", ChecklistPriority.HIGH),
        ("plugin_code_04", "Proper async/await usage", ChecklistPriority.HIGH),
    ]
    
    SERVICE_API_ITEMS = [
        ("service_01", "Uses ServiceAPI, not direct MT5 access", ChecklistPriority.CRITICAL),
        ("service_02", "Passes plugin_id correctly", ChecklistPriority.CRITICAL),
        ("service_03", "Handles service errors gracefully", ChecklistPriority.HIGH),
        ("service_04", "No attempts to bypass security", ChecklistPriority.CRITICAL),
    ]
    
    @classmethod
    def create_checklist(cls, plugin_name: str = "", reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create plugin-specific review checklist."""
        checklist = ReviewChecklist(
            name=f"Plugin Review Checklist{f' - {plugin_name}' if plugin_name else ''}",
            description="Review checklist for plugin code changes",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.STRUCTURE_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.PLUGIN_STRUCTURE,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.CODE_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.PLUGIN_CODE,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.SERVICE_API_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.SERVICE_API_USAGE,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class SecurityReviewChecklist:
    """Generator for security review checklist."""
    
    SECRETS_ITEMS = [
        ("secrets_01", "No tokens in code", ChecklistPriority.CRITICAL, True),
        ("secrets_02", "No passwords in config", ChecklistPriority.CRITICAL, True),
        ("secrets_03", "Environment variables used", ChecklistPriority.HIGH),
        ("secrets_04", ".env file in .gitignore", ChecklistPriority.CRITICAL, True),
    ]
    
    DATA_ACCESS_ITEMS = [
        ("data_01", "Plugin only accesses own database", ChecklistPriority.CRITICAL),
        ("data_02", "No cross-plugin queries", ChecklistPriority.CRITICAL),
        ("data_03", "SQL queries parameterized", ChecklistPriority.CRITICAL),
        ("data_04", "No raw SQL string concatenation", ChecklistPriority.CRITICAL, True),
    ]
    
    SANDBOXING_ITEMS = [
        ("sandbox_01", "No import os, import sys", ChecklistPriority.HIGH, True),
        ("sandbox_02", "No subprocess calls", ChecklistPriority.HIGH, True),
        ("sandbox_03", "No file system access (except own DB)", ChecklistPriority.HIGH),
        ("sandbox_04", "No network requests (except via ServiceAPI)", ChecklistPriority.HIGH),
    ]
    
    @classmethod
    def create_checklist(cls, reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create security review checklist."""
        checklist = ReviewChecklist(
            name="Security Review Checklist",
            description="Security-focused review checklist",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.SECRETS_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.SECRETS_MANAGEMENT,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.DATA_ACCESS_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.DATA_ACCESS,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.SANDBOXING_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.PLUGIN_SANDBOXING,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class PerformanceReviewChecklist:
    """Generator for performance review checklist."""
    
    EFFICIENCY_ITEMS = [
        ("perf_01", "No N+1 query problems", ChecklistPriority.HIGH),
        ("perf_02", "Database queries optimized", ChecklistPriority.MEDIUM),
        ("perf_03", "Heavy operations async", ChecklistPriority.HIGH),
        ("perf_04", "No blocking I/O in event loop", ChecklistPriority.CRITICAL),
    ]
    
    RESOURCE_ITEMS = [
        ("resource_01", "No memory leaks", ChecklistPriority.HIGH),
        ("resource_02", "Connections properly closed", ChecklistPriority.HIGH),
        ("resource_03", "No infinite loops", ChecklistPriority.CRITICAL),
        ("resource_04", "Proper error cleanup", ChecklistPriority.MEDIUM),
    ]
    
    @classmethod
    def create_checklist(cls, reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create performance review checklist."""
        checklist = ReviewChecklist(
            name="Performance Review Checklist",
            description="Performance-focused review checklist",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.EFFICIENCY_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.EFFICIENCY,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.RESOURCE_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.RESOURCE_USAGE,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class TestReviewChecklist:
    """Generator for test review checklist."""
    
    TEST_QUALITY_ITEMS = [
        ("test_qual_01", "Tests are independent", ChecklistPriority.HIGH),
        ("test_qual_02", "Tests are deterministic", ChecklistPriority.HIGH),
        ("test_qual_03", "No sleep() calls", ChecklistPriority.MEDIUM, True),
        ("test_qual_04", "Mock external dependencies", ChecklistPriority.HIGH),
        ("test_qual_05", "Assert meaningful values", ChecklistPriority.HIGH),
    ]
    
    @classmethod
    def create_checklist(cls, reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create test review checklist."""
        checklist = ReviewChecklist(
            name="Test Review Checklist",
            description="Test quality review checklist",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.TEST_QUALITY_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.TEST_QUALITY,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class MigrationReviewChecklist:
    """Generator for migration code review checklist."""
    
    BACKWARD_COMPAT_ITEMS = [
        ("compat_01", "Existing functionality unchanged", ChecklistPriority.CRITICAL),
        ("compat_02", "Legacy code still works", ChecklistPriority.CRITICAL),
        ("compat_03", "Config changes documented", ChecklistPriority.HIGH),
        ("compat_04", "Migration path clear", ChecklistPriority.HIGH),
    ]
    
    DATA_MIGRATION_ITEMS = [
        ("data_mig_01", "Backup before migration", ChecklistPriority.CRITICAL),
        ("data_mig_02", "Rollback procedure tested", ChecklistPriority.CRITICAL),
        ("data_mig_03", "Data integrity verified", ChecklistPriority.CRITICAL),
        ("data_mig_04", "No data loss", ChecklistPriority.CRITICAL),
    ]
    
    @classmethod
    def create_checklist(cls, reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create migration review checklist."""
        checklist = ReviewChecklist(
            name="Migration Review Checklist",
            description="Migration code review checklist",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.BACKWARD_COMPAT_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.MIGRATION,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        for item_id, desc, priority, *automated in cls.DATA_MIGRATION_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.MIGRATION,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class ApprovalChecklist:
    """Generator for final approval checklist."""
    
    APPROVAL_ITEMS = [
        ("approval_01", "All conversations resolved", ChecklistPriority.HIGH),
        ("approval_02", "CI/CD pipeline green", ChecklistPriority.CRITICAL, True),
        ("approval_03", "Documentation updated", ChecklistPriority.MEDIUM),
        ("approval_04", "Changelog updated", ChecklistPriority.LOW),
        ("approval_05", "Deployment plan ready", ChecklistPriority.MEDIUM),
    ]
    
    @classmethod
    def create_checklist(cls, reviewer: str = "", pr_number: Optional[int] = None) -> ReviewChecklist:
        """Create approval checklist."""
        checklist = ReviewChecklist(
            name="Final Approval Checklist",
            description="Final checklist before merge approval",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        for item_id, desc, priority, *automated in cls.APPROVAL_ITEMS:
            checklist.add_item(ChecklistItem(
                id=item_id,
                description=desc,
                category=ChecklistCategory.APPROVAL,
                priority=priority,
                automated=automated[0] if automated else False
            ))
        
        return checklist


class ChecklistGenerator:
    """Generator for all review checklists."""
    
    @staticmethod
    def create_full_review_checklist(
        reviewer: str = "",
        pr_number: Optional[int] = None,
        include_plugin: bool = False,
        include_migration: bool = False
    ) -> ReviewChecklist:
        """Create comprehensive review checklist."""
        checklist = ReviewChecklist(
            name="Full Code Review Checklist",
            description="Comprehensive code review checklist",
            reviewer=reviewer,
            pr_number=pr_number
        )
        
        universal = UniversalReviewChecklist.create_checklist()
        for item in universal.items:
            checklist.add_item(item)
        
        security = SecurityReviewChecklist.create_checklist()
        for item in security.items:
            checklist.add_item(item)
        
        performance = PerformanceReviewChecklist.create_checklist()
        for item in performance.items:
            checklist.add_item(item)
        
        test = TestReviewChecklist.create_checklist()
        for item in test.items:
            checklist.add_item(item)
        
        if include_plugin:
            plugin = PluginReviewChecklist.create_checklist()
            for item in plugin.items:
                checklist.add_item(item)
        
        if include_migration:
            migration = MigrationReviewChecklist.create_checklist()
            for item in migration.items:
                checklist.add_item(item)
        
        approval = ApprovalChecklist.create_checklist()
        for item in approval.items:
            checklist.add_item(item)
        
        return checklist
    
    @staticmethod
    def get_all_checklist_types() -> List[str]:
        """Get list of all checklist types."""
        return [
            "universal",
            "plugin",
            "security",
            "performance",
            "test",
            "migration",
            "approval",
            "full"
        ]
    
    @staticmethod
    def create_checklist_by_type(
        checklist_type: str,
        reviewer: str = "",
        pr_number: Optional[int] = None
    ) -> Optional[ReviewChecklist]:
        """Create checklist by type name."""
        creators = {
            "universal": UniversalReviewChecklist.create_checklist,
            "plugin": PluginReviewChecklist.create_checklist,
            "security": SecurityReviewChecklist.create_checklist,
            "performance": PerformanceReviewChecklist.create_checklist,
            "test": TestReviewChecklist.create_checklist,
            "migration": MigrationReviewChecklist.create_checklist,
            "approval": ApprovalChecklist.create_checklist,
        }
        
        if checklist_type == "full":
            return ChecklistGenerator.create_full_review_checklist(reviewer, pr_number)
        
        creator = creators.get(checklist_type)
        if creator:
            return creator(reviewer, pr_number)
        
        return None


def generate_pr_checklist_comment(pr_number: int, reviewer: str = "") -> str:
    """Generate PR checklist comment in markdown format."""
    checklist = ChecklistGenerator.create_full_review_checklist(
        reviewer=reviewer,
        pr_number=pr_number,
        include_plugin=True
    )
    return checklist.to_markdown()
