"""
Document 27: Plugin Versioning & Compatibility System

Complete Plugin Lifecycle Management with:
1. Semantic Versioning - Enforce SemVer (Major.Minor.Patch) for all plugins
2. Dependency Graph - Ensure plugins declare dependencies
3. Update Manager - Detect new versions, backup current plugin, apply update
4. Rollback System - Revert plugin to previous version if update fails
5. Compatibility Checker - Verify plugin version matches Core System version
6. Manifest Validator - Strict checking of plugin_manifest.json
7. VersionedPluginRegistry - Enhanced registry with version management
"""

import sqlite3
import os
import json
import re
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class VersionBump(Enum):
    """Version bump type"""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    PATCH = "PATCH"


class CompatibilityLevel(Enum):
    """Compatibility level between versions"""
    FULLY_COMPATIBLE = "FULLY_COMPATIBLE"
    BACKWARD_COMPATIBLE = "BACKWARD_COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


class UpdateStatus(Enum):
    """Update operation status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class DependencyStatus(Enum):
    """Dependency resolution status"""
    SATISFIED = "SATISFIED"
    MISSING = "MISSING"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    CIRCULAR = "CIRCULAR"


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class SemanticVersion:
    """
    Represents a semantic version (SemVer)
    Format: MAJOR.MINOR.PATCH
    """
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build_metadata: str = ""
    
    @classmethod
    def parse(cls, version_string: str) -> 'SemanticVersion':
        """Parse a version string into SemanticVersion"""
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
        match = re.match(pattern, version_string)
        
        if not match:
            raise ValueError(f"Invalid version string: {version_string}")
        
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4) or "",
            build_metadata=match.group(5) or ""
        )
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version
    
    def __lt__(self, other: 'SemanticVersion') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other: 'SemanticVersion') -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)
    
    def __gt__(self, other: 'SemanticVersion') -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __ge__(self, other: 'SemanticVersion') -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch))
    
    def bump(self, bump_type: VersionBump) -> 'SemanticVersion':
        """Create a new version with the specified bump"""
        if bump_type == VersionBump.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        elif bump_type == VersionBump.MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        else:
            return SemanticVersion(self.major, self.minor, self.patch + 1)
    
    def is_compatible_with(self, other: 'SemanticVersion') -> bool:
        """Check if this version is compatible with another (same MAJOR)"""
        return self.major == other.major
    
    def get_compatibility_level(self, other: 'SemanticVersion') -> CompatibilityLevel:
        """Get compatibility level with another version"""
        if self.major != other.major:
            return CompatibilityLevel.INCOMPATIBLE
        elif self.minor == other.minor and self.patch == other.patch:
            return CompatibilityLevel.FULLY_COMPATIBLE
        else:
            return CompatibilityLevel.BACKWARD_COMPATIBLE


@dataclass
class PluginVersion:
    """
    Represents a plugin version with metadata
    """
    plugin_id: str
    major: int
    minor: int
    patch: int
    
    build_date: datetime = field(default_factory=datetime.now)
    commit_hash: str = ""
    author: str = ""
    
    requires_api_version: str = "1.0.0"
    requires_db_schema: str = "1.0.0"
    
    features: List[str] = field(default_factory=list)
    deprecated: bool = False
    release_notes: str = ""
    
    @property
    def version_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @property
    def semantic_version(self) -> SemanticVersion:
        return SemanticVersion(self.major, self.minor, self.patch)
    
    def is_compatible_with(self, other: 'PluginVersion') -> bool:
        """Check if this version is compatible with another"""
        if self.plugin_id != other.plugin_id:
            return True
        return self.major == other.major
    
    def __str__(self) -> str:
        return f"{self.plugin_id} v{self.version_string}"
    
    def __lt__(self, other: 'PluginVersion') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PluginVersion):
            return False
        return (
            self.plugin_id == other.plugin_id and
            self.major == other.major and
            self.minor == other.minor and
            self.patch == other.patch
        )
    
    def __hash__(self) -> int:
        return hash((self.plugin_id, self.major, self.minor, self.patch))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "version_string": self.version_string,
            "build_date": self.build_date.isoformat(),
            "commit_hash": self.commit_hash,
            "author": self.author,
            "requires_api_version": self.requires_api_version,
            "requires_db_schema": self.requires_db_schema,
            "features": self.features,
            "deprecated": self.deprecated,
            "release_notes": self.release_notes
        }


@dataclass
class PluginDependency:
    """
    Represents a plugin dependency
    """
    plugin_id: str
    min_version: str
    max_version: Optional[str] = None
    optional: bool = False
    
    def is_satisfied_by(self, version: SemanticVersion) -> bool:
        """Check if a version satisfies this dependency"""
        min_ver = SemanticVersion.parse(self.min_version)
        
        if version < min_ver:
            return False
        
        if self.max_version:
            max_ver = SemanticVersion.parse(self.max_version)
            if version > max_ver:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "optional": self.optional
        }


@dataclass
class PluginManifest:
    """
    Plugin manifest (plugin_manifest.json)
    """
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    
    entry_point: str = "plugin.py"
    config_file: str = "config.json"
    
    requires_api_version: str = "1.0.0"
    requires_db_schema: str = "1.0.0"
    requires_core_version: str = "5.0.0"
    
    dependencies: List[PluginDependency] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "entry_point": self.entry_point,
            "config_file": self.config_file,
            "requires_api_version": self.requires_api_version,
            "requires_db_schema": self.requires_db_schema,
            "requires_core_version": self.requires_core_version,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "features": self.features,
            "permissions": self.permissions,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license
        }


@dataclass
class UpdateResult:
    """
    Result of an update operation
    """
    success: bool
    status: UpdateStatus
    message: str
    plugin_id: str
    from_version: str
    to_version: str
    backup_path: Optional[str] = None
    execution_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "status": self.status.value,
            "message": self.message,
            "plugin_id": self.plugin_id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "backup_path": self.backup_path,
            "execution_time_ms": self.execution_time_ms
        }


@dataclass
class DependencyNode:
    """
    Node in the dependency graph
    """
    plugin_id: str
    version: SemanticVersion
    dependencies: List[PluginDependency] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)


# ============================================================================
# MANIFEST VALIDATOR
# ============================================================================

class ManifestValidator:
    """
    Strict validation of plugin_manifest.json
    """
    
    REQUIRED_FIELDS = [
        "plugin_id", "name", "version", "description", "author"
    ]
    
    OPTIONAL_FIELDS = [
        "entry_point", "config_file", "requires_api_version",
        "requires_db_schema", "requires_core_version", "dependencies",
        "features", "permissions", "homepage", "repository", "license"
    ]
    
    def __init__(self):
        self._errors: List[str] = []
        self._warnings: List[str] = []
    
    def validate(self, manifest_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a manifest dictionary
        
        Returns:
            (is_valid, errors, warnings)
        """
        self._errors = []
        self._warnings = []
        
        self._validate_required_fields(manifest_data)
        self._validate_plugin_id(manifest_data.get("plugin_id", ""))
        self._validate_version(manifest_data.get("version", ""))
        self._validate_dependencies(manifest_data.get("dependencies", []))
        self._validate_permissions(manifest_data.get("permissions", []))
        
        return len(self._errors) == 0, self._errors, self._warnings
    
    def validate_file(self, manifest_path: str) -> Tuple[bool, List[str], List[str]]:
        """Validate a manifest file"""
        try:
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
            return self.validate(manifest_data)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"], []
        except FileNotFoundError:
            return False, [f"Manifest file not found: {manifest_path}"], []
    
    def parse_manifest(self, manifest_data: Dict[str, Any]) -> Optional[PluginManifest]:
        """Parse manifest data into PluginManifest object"""
        is_valid, errors, _ = self.validate(manifest_data)
        
        if not is_valid:
            logger.error(f"Invalid manifest: {errors}")
            return None
        
        dependencies = []
        for dep in manifest_data.get("dependencies", []):
            dependencies.append(PluginDependency(
                plugin_id=dep.get("plugin_id", ""),
                min_version=dep.get("min_version", "1.0.0"),
                max_version=dep.get("max_version"),
                optional=dep.get("optional", False)
            ))
        
        return PluginManifest(
            plugin_id=manifest_data["plugin_id"],
            name=manifest_data["name"],
            version=manifest_data["version"],
            description=manifest_data["description"],
            author=manifest_data["author"],
            entry_point=manifest_data.get("entry_point", "plugin.py"),
            config_file=manifest_data.get("config_file", "config.json"),
            requires_api_version=manifest_data.get("requires_api_version", "1.0.0"),
            requires_db_schema=manifest_data.get("requires_db_schema", "1.0.0"),
            requires_core_version=manifest_data.get("requires_core_version", "5.0.0"),
            dependencies=dependencies,
            features=manifest_data.get("features", []),
            permissions=manifest_data.get("permissions", []),
            homepage=manifest_data.get("homepage", ""),
            repository=manifest_data.get("repository", ""),
            license=manifest_data.get("license", "MIT")
        )
    
    def _validate_required_fields(self, manifest_data: Dict[str, Any]):
        """Validate required fields exist"""
        for field in self.REQUIRED_FIELDS:
            if field not in manifest_data:
                self._errors.append(f"Missing required field: {field}")
            elif not manifest_data[field]:
                self._errors.append(f"Empty required field: {field}")
    
    def _validate_plugin_id(self, plugin_id: str):
        """Validate plugin_id format"""
        if not plugin_id:
            return
        
        pattern = r'^[a-z][a-z0-9_]*$'
        if not re.match(pattern, plugin_id):
            self._errors.append(
                f"Invalid plugin_id format: {plugin_id}. "
                "Must start with lowercase letter and contain only lowercase letters, numbers, and underscores."
            )
    
    def _validate_version(self, version: str):
        """Validate version string is valid SemVer"""
        if not version:
            return
        
        try:
            SemanticVersion.parse(version)
        except ValueError:
            self._errors.append(
                f"Invalid version format: {version}. "
                "Must be valid SemVer (MAJOR.MINOR.PATCH)."
            )
    
    def _validate_dependencies(self, dependencies: List[Dict]):
        """Validate dependencies format"""
        for i, dep in enumerate(dependencies):
            if not isinstance(dep, dict):
                self._errors.append(f"Dependency {i} must be an object")
                continue
            
            if "plugin_id" not in dep:
                self._errors.append(f"Dependency {i} missing plugin_id")
            
            if "min_version" not in dep:
                self._warnings.append(f"Dependency {i} missing min_version, defaulting to 1.0.0")
    
    def _validate_permissions(self, permissions: List[str]):
        """Validate permissions"""
        valid_permissions = [
            "trading", "notifications", "database", "config",
            "admin", "analytics", "market_data", "user_management"
        ]
        
        for perm in permissions:
            if perm not in valid_permissions:
                self._warnings.append(f"Unknown permission: {perm}")


# ============================================================================
# DEPENDENCY GRAPH
# ============================================================================

class DependencyGraph:
    """
    Manages plugin dependency relationships
    """
    
    def __init__(self):
        self._nodes: Dict[str, DependencyNode] = {}
        self._resolved_order: List[str] = []
    
    def add_plugin(
        self,
        plugin_id: str,
        version: SemanticVersion,
        dependencies: List[PluginDependency]
    ):
        """Add a plugin to the dependency graph"""
        node = DependencyNode(
            plugin_id=plugin_id,
            version=version,
            dependencies=dependencies
        )
        self._nodes[plugin_id] = node
        
        for dep in dependencies:
            if dep.plugin_id in self._nodes:
                self._nodes[dep.plugin_id].dependents.append(plugin_id)
    
    def remove_plugin(self, plugin_id: str):
        """Remove a plugin from the dependency graph"""
        if plugin_id not in self._nodes:
            return
        
        node = self._nodes[plugin_id]
        
        for dep in node.dependencies:
            if dep.plugin_id in self._nodes:
                dependents = self._nodes[dep.plugin_id].dependents
                if plugin_id in dependents:
                    dependents.remove(plugin_id)
        
        del self._nodes[plugin_id]
    
    def get_dependencies(self, plugin_id: str) -> List[PluginDependency]:
        """Get dependencies for a plugin"""
        if plugin_id not in self._nodes:
            return []
        return self._nodes[plugin_id].dependencies
    
    def get_dependents(self, plugin_id: str) -> List[str]:
        """Get plugins that depend on this plugin"""
        if plugin_id not in self._nodes:
            return []
        return self._nodes[plugin_id].dependents
    
    def check_dependency_status(
        self,
        plugin_id: str,
        available_versions: Dict[str, SemanticVersion]
    ) -> Dict[str, DependencyStatus]:
        """Check status of all dependencies for a plugin"""
        if plugin_id not in self._nodes:
            return {}
        
        results = {}
        node = self._nodes[plugin_id]
        
        for dep in node.dependencies:
            if dep.plugin_id not in available_versions:
                if dep.optional:
                    results[dep.plugin_id] = DependencyStatus.SATISFIED
                else:
                    results[dep.plugin_id] = DependencyStatus.MISSING
            else:
                version = available_versions[dep.plugin_id]
                if dep.is_satisfied_by(version):
                    results[dep.plugin_id] = DependencyStatus.SATISFIED
                else:
                    results[dep.plugin_id] = DependencyStatus.VERSION_MISMATCH
        
        return results
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str, path: List[str]) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            if node_id in self._nodes:
                for dep in self._nodes[node_id].dependencies:
                    if dep.plugin_id not in visited:
                        if dfs(dep.plugin_id, path):
                            return True
                    elif dep.plugin_id in rec_stack:
                        cycle_start = path.index(dep.plugin_id)
                        cycles.append(path[cycle_start:] + [dep.plugin_id])
                        return True
            
            path.pop()
            rec_stack.remove(node_id)
            return False
        
        for node_id in self._nodes:
            if node_id not in visited:
                dfs(node_id, [])
        
        return cycles
    
    def get_installation_order(self) -> List[str]:
        """Get topological order for plugin installation"""
        if self._resolved_order:
            return self._resolved_order
        
        visited = set()
        order = []
        
        def visit(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            if node_id in self._nodes:
                for dep in self._nodes[node_id].dependencies:
                    visit(dep.plugin_id)
            
            order.append(node_id)
        
        for node_id in self._nodes:
            visit(node_id)
        
        self._resolved_order = order
        return order
    
    def can_remove(self, plugin_id: str) -> Tuple[bool, List[str]]:
        """Check if a plugin can be safely removed"""
        if plugin_id not in self._nodes:
            return True, []
        
        dependents = self.get_dependents(plugin_id)
        
        blocking = []
        for dep_id in dependents:
            if dep_id in self._nodes:
                for dep in self._nodes[dep_id].dependencies:
                    if dep.plugin_id == plugin_id and not dep.optional:
                        blocking.append(dep_id)
        
        return len(blocking) == 0, blocking
    
    def get_all_plugins(self) -> List[str]:
        """Get all plugins in the graph"""
        return list(self._nodes.keys())


# ============================================================================
# COMPATIBILITY CHECKER
# ============================================================================

class CompatibilityChecker:
    """
    Verify plugin version matches Core System version
    """
    
    def __init__(
        self,
        core_version: str = "5.0.0",
        api_version: str = "1.0.0",
        db_schema_version: str = "1.0.0"
    ):
        self.core_version = SemanticVersion.parse(core_version)
        self.api_version = SemanticVersion.parse(api_version)
        self.db_schema_version = SemanticVersion.parse(db_schema_version)
    
    def check_plugin_compatibility(
        self,
        manifest: PluginManifest
    ) -> Tuple[bool, List[str]]:
        """Check if a plugin is compatible with the current system"""
        issues = []
        
        required_core = SemanticVersion.parse(manifest.requires_core_version)
        if not self._is_version_compatible(required_core, self.core_version):
            issues.append(
                f"Plugin requires Core v{manifest.requires_core_version}, "
                f"but system is v{self.core_version}"
            )
        
        required_api = SemanticVersion.parse(manifest.requires_api_version)
        if not self._is_version_compatible(required_api, self.api_version):
            issues.append(
                f"Plugin requires API v{manifest.requires_api_version}, "
                f"but system has v{self.api_version}"
            )
        
        required_db = SemanticVersion.parse(manifest.requires_db_schema)
        if not self._is_version_compatible(required_db, self.db_schema_version):
            issues.append(
                f"Plugin requires DB Schema v{manifest.requires_db_schema}, "
                f"but system has v{self.db_schema_version}"
            )
        
        return len(issues) == 0, issues
    
    def check_plugin_pair_compatibility(
        self,
        plugin1: PluginVersion,
        plugin2: PluginVersion
    ) -> Tuple[bool, str]:
        """Check if two plugins are compatible with each other"""
        if plugin1.plugin_id == plugin2.plugin_id:
            if plugin1.major != plugin2.major:
                return False, (
                    f"Major version mismatch: {plugin1} vs {plugin2}"
                )
        
        return True, "Compatible"
    
    def get_compatibility_matrix(
        self,
        plugins: List[PluginVersion]
    ) -> Dict[str, Dict[str, bool]]:
        """Generate compatibility matrix for multiple plugins"""
        matrix = {}
        
        for p1 in plugins:
            matrix[str(p1)] = {}
            for p2 in plugins:
                compatible, _ = self.check_plugin_pair_compatibility(p1, p2)
                matrix[str(p1)][str(p2)] = compatible
        
        return matrix
    
    def _is_version_compatible(
        self,
        required: SemanticVersion,
        available: SemanticVersion
    ) -> bool:
        """Check if available version satisfies required version"""
        return available >= required


# ============================================================================
# UPDATE MANAGER
# ============================================================================

class UpdateManager:
    """
    Manages plugin updates: detect, backup, apply
    """
    
    def __init__(
        self,
        plugins_dir: str,
        backup_dir: str = "plugin_backups"
    ):
        self.plugins_dir = Path(plugins_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self._update_history: List[UpdateResult] = []
    
    async def check_for_updates(
        self,
        current_versions: Dict[str, PluginVersion],
        available_versions: Dict[str, List[PluginVersion]]
    ) -> Dict[str, PluginVersion]:
        """Check for available updates"""
        updates = {}
        
        for plugin_id, current in current_versions.items():
            if plugin_id not in available_versions:
                continue
            
            available = sorted(available_versions[plugin_id], reverse=True)
            
            for version in available:
                if version > current and version.is_compatible_with(current):
                    updates[plugin_id] = version
                    break
        
        return updates
    
    async def backup_plugin(self, plugin_id: str) -> Optional[str]:
        """Create backup of current plugin"""
        plugin_path = self.plugins_dir / plugin_id
        
        if not plugin_path.exists():
            logger.warning(f"Plugin path not found: {plugin_path}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{plugin_id}_{timestamp}"
        
        try:
            shutil.copytree(plugin_path, backup_path)
            logger.info(f"Backed up {plugin_id} to {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed for {plugin_id}: {e}")
            return None
    
    async def apply_update(
        self,
        plugin_id: str,
        new_version: PluginVersion,
        update_source: str
    ) -> UpdateResult:
        """Apply plugin update"""
        start_time = datetime.now()
        
        current_version = self._get_current_version(plugin_id)
        from_version = current_version.version_string if current_version else "0.0.0"
        
        backup_path = await self.backup_plugin(plugin_id)
        
        if not backup_path:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message="Backup failed",
                plugin_id=plugin_id,
                from_version=from_version,
                to_version=new_version.version_string
            )
        
        try:
            plugin_path = self.plugins_dir / plugin_id
            
            if plugin_path.exists():
                shutil.rmtree(plugin_path)
            
            if os.path.isdir(update_source):
                shutil.copytree(update_source, plugin_path)
            else:
                plugin_path.mkdir(parents=True, exist_ok=True)
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            result = UpdateResult(
                success=True,
                status=UpdateStatus.COMPLETED,
                message=f"Updated {plugin_id} to {new_version.version_string}",
                plugin_id=plugin_id,
                from_version=from_version,
                to_version=new_version.version_string,
                backup_path=backup_path,
                execution_time_ms=execution_time
            )
            
            self._update_history.append(result)
            
            logger.info(f"Updated {plugin_id}: {from_version} -> {new_version.version_string}")
            
            return result
            
        except Exception as e:
            logger.error(f"Update failed for {plugin_id}: {e}")
            
            await self.restore_from_backup(plugin_id, backup_path)
            
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"Update failed: {e}",
                plugin_id=plugin_id,
                from_version=from_version,
                to_version=new_version.version_string,
                backup_path=backup_path
            )
    
    async def restore_from_backup(self, plugin_id: str, backup_path: str) -> bool:
        """Restore plugin from backup"""
        try:
            plugin_path = self.plugins_dir / plugin_id
            
            if plugin_path.exists():
                shutil.rmtree(plugin_path)
            
            shutil.copytree(backup_path, plugin_path)
            
            logger.info(f"Restored {plugin_id} from backup")
            
            return True
            
        except Exception as e:
            logger.error(f"Restore failed for {plugin_id}: {e}")
            return False
    
    def get_update_history(self) -> List[UpdateResult]:
        """Get update history"""
        return self._update_history.copy()
    
    def _get_current_version(self, plugin_id: str) -> Optional[PluginVersion]:
        """Get current version of a plugin"""
        manifest_path = self.plugins_dir / plugin_id / "plugin_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)
            
            version = SemanticVersion.parse(data.get("version", "1.0.0"))
            
            return PluginVersion(
                plugin_id=plugin_id,
                major=version.major,
                minor=version.minor,
                patch=version.patch
            )
        except Exception:
            return None


# ============================================================================
# ROLLBACK SYSTEM
# ============================================================================

class RollbackSystem:
    """
    Revert plugin to previous version if update fails
    """
    
    def __init__(self, update_manager: UpdateManager):
        self.update_manager = update_manager
        self._rollback_history: List[UpdateResult] = []
    
    async def rollback_plugin(self, plugin_id: str) -> UpdateResult:
        """Rollback plugin to previous version"""
        history = self.update_manager.get_update_history()
        
        plugin_updates = [
            u for u in history
            if u.plugin_id == plugin_id and u.success and u.backup_path
        ]
        
        if not plugin_updates:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"No backup found for {plugin_id}",
                plugin_id=plugin_id,
                from_version="unknown",
                to_version="unknown"
            )
        
        last_update = plugin_updates[-1]
        
        success = await self.update_manager.restore_from_backup(
            plugin_id, last_update.backup_path
        )
        
        result = UpdateResult(
            success=success,
            status=UpdateStatus.ROLLED_BACK if success else UpdateStatus.FAILED,
            message=f"Rolled back {plugin_id} to {last_update.from_version}" if success else "Rollback failed",
            plugin_id=plugin_id,
            from_version=last_update.to_version,
            to_version=last_update.from_version,
            backup_path=last_update.backup_path
        )
        
        self._rollback_history.append(result)
        
        return result
    
    async def rollback_to_version(
        self,
        plugin_id: str,
        target_version: str
    ) -> UpdateResult:
        """Rollback plugin to a specific version"""
        history = self.update_manager.get_update_history()
        
        target_backup = None
        for update in reversed(history):
            if update.plugin_id == plugin_id and update.from_version == target_version:
                target_backup = update.backup_path
                break
        
        if not target_backup:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"No backup found for {plugin_id} v{target_version}",
                plugin_id=plugin_id,
                from_version="unknown",
                to_version=target_version
            )
        
        success = await self.update_manager.restore_from_backup(plugin_id, target_backup)
        
        result = UpdateResult(
            success=success,
            status=UpdateStatus.ROLLED_BACK if success else UpdateStatus.FAILED,
            message=f"Rolled back {plugin_id} to {target_version}" if success else "Rollback failed",
            plugin_id=plugin_id,
            from_version="current",
            to_version=target_version,
            backup_path=target_backup
        )
        
        self._rollback_history.append(result)
        
        return result
    
    def get_rollback_history(self) -> List[UpdateResult]:
        """Get rollback history"""
        return self._rollback_history.copy()
    
    def get_available_rollback_versions(self, plugin_id: str) -> List[str]:
        """Get list of versions available for rollback"""
        history = self.update_manager.get_update_history()
        
        versions = set()
        for update in history:
            if update.plugin_id == plugin_id and update.backup_path:
                versions.add(update.from_version)
        
        return sorted(versions, reverse=True)


# ============================================================================
# VERSIONED PLUGIN REGISTRY
# ============================================================================

class VersionedPluginRegistry:
    """
    Enhanced plugin registry with version management
    """
    
    def __init__(
        self,
        db_path: str,
        plugins_dir: str = "plugins",
        backup_dir: str = "plugin_backups"
    ):
        self.db_path = db_path
        self.plugins_dir = Path(plugins_dir)
        
        self.active_plugins: Dict[str, PluginVersion] = {}
        self.available_versions: Dict[str, List[PluginVersion]] = {}
        
        self.manifest_validator = ManifestValidator()
        self.dependency_graph = DependencyGraph()
        self.compatibility_checker = CompatibilityChecker()
        self.update_manager = UpdateManager(plugins_dir, backup_dir)
        self.rollback_system = RollbackSystem(self.update_manager)
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables for version tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                major INTEGER NOT NULL,
                minor INTEGER NOT NULL,
                patch INTEGER NOT NULL,
                build_date DATETIME NOT NULL,
                commit_hash TEXT NOT NULL,
                author TEXT NOT NULL,
                requires_api_version TEXT NOT NULL,
                requires_db_schema TEXT NOT NULL,
                features TEXT NOT NULL,
                deprecated BOOLEAN DEFAULT FALSE,
                release_notes TEXT,
                UNIQUE(plugin_id, major, minor, patch)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_version_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                version_string TEXT NOT NULL,
                activated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                deactivated_at DATETIME,
                reason TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plugin_history 
            ON plugin_version_history (plugin_id, activated_at)
        """)
        
        conn.commit()
        conn.close()
    
    def load_plugin_versions(self):
        """Load all available plugin versions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plugin_id, major, minor, patch, build_date, 
                   commit_hash, author, requires_api_version, 
                   requires_db_schema, features, deprecated, release_notes
            FROM plugin_versions
            ORDER BY major DESC, minor DESC, patch DESC
        """)
        
        for row in cursor.fetchall():
            plugin_id = row[0]
            version = PluginVersion(
                plugin_id=plugin_id,
                major=row[1],
                minor=row[2],
                patch=row[3],
                build_date=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                commit_hash=row[5] or "",
                author=row[6] or "",
                requires_api_version=row[7] or "1.0.0",
                requires_db_schema=row[8] or "1.0.0",
                features=json.loads(row[9]) if row[9] else [],
                deprecated=bool(row[10]),
                release_notes=row[11] or ""
            )
            
            if plugin_id not in self.available_versions:
                self.available_versions[plugin_id] = []
            
            self.available_versions[plugin_id].append(version)
        
        conn.close()
    
    def register_plugin(
        self,
        plugin_id: str,
        version: PluginVersion,
        force: bool = False
    ) -> Tuple[bool, str]:
        """Register a specific plugin version as active"""
        for active_id, active_version in self.active_plugins.items():
            if not version.is_compatible_with(active_version):
                msg = f"{version} is incompatible with active {active_version}"
                logger.error(msg)
                if not force:
                    return False, msg
        
        api_compatible, issues = self.compatibility_checker.check_plugin_compatibility(
            PluginManifest(
                plugin_id=version.plugin_id,
                name=version.plugin_id,
                version=version.version_string,
                description="",
                author=version.author,
                requires_api_version=version.requires_api_version,
                requires_db_schema=version.requires_db_schema
            )
        )
        
        if not api_compatible and not force:
            return False, f"Compatibility issues: {', '.join(issues)}"
        
        self.active_plugins[plugin_id] = version
        
        self._record_activation(plugin_id, version.version_string, "registration")
        
        logger.info(f"Registered {version}")
        
        return True, f"Registered {version}"
    
    def upgrade_plugin(
        self,
        plugin_id: str,
        target_version: str
    ) -> Tuple[bool, str]:
        """Upgrade plugin to a specific version"""
        current = self.active_plugins.get(plugin_id)
        
        if not current:
            return False, f"Plugin {plugin_id} not currently active"
        
        target = self._find_version(plugin_id, target_version)
        
        if not target:
            return False, f"Version {target_version} not found for {plugin_id}"
        
        if target < current:
            logger.warning(
                f"Downgrading {plugin_id} from {current.version_string} "
                f"to {target.version_string}"
            )
        
        if not current.is_compatible_with(target):
            return False, (
                f"Version {target_version} is incompatible with "
                f"current version {current.version_string} (MAJOR version mismatch)"
            )
        
        success, msg = self.register_plugin(plugin_id, target, force=False)
        
        if success:
            self._record_activation(plugin_id, target.version_string, "upgrade")
            return True, f"Upgraded {plugin_id} to {target.version_string}"
        else:
            return False, f"Upgrade failed: {msg}"
    
    def rollback_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Rollback plugin to previous stable version"""
        current = self.active_plugins.get(plugin_id)
        
        if not current:
            return False, f"Plugin {plugin_id} not currently active"
        
        available = sorted(
            [v for v in self.available_versions.get(plugin_id, [])
             if v.major == current.major and v < current and not v.deprecated],
            reverse=True
        )
        
        if not available:
            return False, f"No rollback version found for {plugin_id}"
        
        previous = available[0]
        
        success, msg = self.register_plugin(plugin_id, previous, force=True)
        
        if success:
            self._record_activation(plugin_id, previous.version_string, "rollback")
            return True, f"Rolled back {plugin_id} to {previous.version_string}"
        else:
            return False, f"Rollback failed: {msg}"
    
    def get_active_version(self, plugin_id: str) -> Optional[PluginVersion]:
        """Get currently active version of plugin"""
        return self.active_plugins.get(plugin_id)
    
    def list_available_versions(self, plugin_id: str) -> List[PluginVersion]:
        """List all available versions of plugin"""
        return sorted(
            self.available_versions.get(plugin_id, []),
            reverse=True
        )
    
    def add_version(self, version: PluginVersion):
        """Add a new version to the registry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO plugin_versions 
                (plugin_id, major, minor, patch, build_date, commit_hash, 
                 author, requires_api_version, requires_db_schema, features, 
                 deprecated, release_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.plugin_id,
                version.major,
                version.minor,
                version.patch,
                version.build_date.isoformat(),
                version.commit_hash,
                version.author,
                version.requires_api_version,
                version.requires_db_schema,
                json.dumps(version.features),
                version.deprecated,
                version.release_notes
            ))
            
            conn.commit()
            
            if version.plugin_id not in self.available_versions:
                self.available_versions[version.plugin_id] = []
            
            self.available_versions[version.plugin_id].append(version)
            
            logger.info(f"Added version {version}")
            
        except sqlite3.IntegrityError:
            logger.warning(f"Version {version} already exists")
        finally:
            conn.close()
    
    def deprecate_version(self, plugin_id: str, version_string: str) -> bool:
        """Mark a version as deprecated"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        major, minor, patch = map(int, version_string.split('.'))
        
        cursor.execute("""
            UPDATE plugin_versions 
            SET deprecated = TRUE 
            WHERE plugin_id = ? AND major = ? AND minor = ? AND patch = ?
        """, (plugin_id, major, minor, patch))
        
        conn.commit()
        conn.close()
        
        for version in self.available_versions.get(plugin_id, []):
            if version.version_string == version_string:
                version.deprecated = True
                return True
        
        return False
    
    def get_version_history(self, plugin_id: str) -> List[Dict[str, Any]]:
        """Get version activation history for a plugin"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_string, activated_at, deactivated_at, reason
            FROM plugin_version_history
            WHERE plugin_id = ?
            ORDER BY activated_at DESC
        """, (plugin_id,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "version": row[0],
                "activated_at": row[1],
                "deactivated_at": row[2],
                "reason": row[3]
            })
        
        conn.close()
        
        return history
    
    def _find_version(self, plugin_id: str, version_string: str) -> Optional[PluginVersion]:
        """Find specific version by version string"""
        major, minor, patch = map(int, version_string.split('.'))
        
        for version in self.available_versions.get(plugin_id, []):
            if version.major == major and version.minor == minor and version.patch == patch:
                return version
        
        return None
    
    def _record_activation(self, plugin_id: str, version_string: str, reason: str):
        """Record version activation in history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE plugin_version_history 
            SET deactivated_at = CURRENT_TIMESTAMP 
            WHERE plugin_id = ? AND deactivated_at IS NULL
        """, (plugin_id,))
        
        cursor.execute("""
            INSERT INTO plugin_version_history (plugin_id, version_string, reason)
            VALUES (?, ?, ?)
        """, (plugin_id, version_string, reason))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "active_plugins": len(self.active_plugins),
            "total_versions": sum(len(v) for v in self.available_versions.values()),
            "plugins_with_versions": len(self.available_versions),
            "active_plugin_ids": list(self.active_plugins.keys())
        }


# ============================================================================
# PLUGIN LIFECYCLE MANAGER
# ============================================================================

class PluginLifecycleManager:
    """
    Complete plugin lifecycle management
    """
    
    def __init__(
        self,
        db_path: str,
        plugins_dir: str = "plugins",
        backup_dir: str = "plugin_backups"
    ):
        self.registry = VersionedPluginRegistry(db_path, plugins_dir, backup_dir)
        self.manifest_validator = self.registry.manifest_validator
        self.dependency_graph = self.registry.dependency_graph
        self.compatibility_checker = self.registry.compatibility_checker
        self.update_manager = self.registry.update_manager
        self.rollback_system = self.registry.rollback_system
    
    async def install_plugin(
        self,
        manifest_path: str,
        plugin_source: str
    ) -> Tuple[bool, str]:
        """Install a new plugin"""
        is_valid, errors, warnings = self.manifest_validator.validate_file(manifest_path)
        
        if not is_valid:
            return False, f"Invalid manifest: {', '.join(errors)}"
        
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
        
        manifest = self.manifest_validator.parse_manifest(manifest_data)
        
        if not manifest:
            return False, "Failed to parse manifest"
        
        compatible, issues = self.compatibility_checker.check_plugin_compatibility(manifest)
        
        if not compatible:
            return False, f"Compatibility issues: {', '.join(issues)}"
        
        version = SemanticVersion.parse(manifest.version)
        
        dep_status = self.dependency_graph.check_dependency_status(
            manifest.plugin_id,
            {p: v.semantic_version for p, v in self.registry.active_plugins.items()}
        )
        
        for dep_id, status in dep_status.items():
            if status == DependencyStatus.MISSING:
                return False, f"Missing dependency: {dep_id}"
            elif status == DependencyStatus.VERSION_MISMATCH:
                return False, f"Dependency version mismatch: {dep_id}"
        
        plugin_version = PluginVersion(
            plugin_id=manifest.plugin_id,
            major=version.major,
            minor=version.minor,
            patch=version.patch,
            author=manifest.author,
            requires_api_version=manifest.requires_api_version,
            requires_db_schema=manifest.requires_db_schema,
            features=manifest.features
        )
        
        self.registry.add_version(plugin_version)
        
        success, msg = self.registry.register_plugin(
            manifest.plugin_id, plugin_version
        )
        
        if success:
            self.dependency_graph.add_plugin(
                manifest.plugin_id,
                version,
                manifest.dependencies
            )
        
        return success, msg
    
    async def uninstall_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Uninstall a plugin"""
        can_remove, blocking = self.dependency_graph.can_remove(plugin_id)
        
        if not can_remove:
            return False, f"Cannot remove: required by {', '.join(blocking)}"
        
        if plugin_id in self.registry.active_plugins:
            del self.registry.active_plugins[plugin_id]
        
        self.dependency_graph.remove_plugin(plugin_id)
        
        return True, f"Uninstalled {plugin_id}"
    
    async def update_plugin(
        self,
        plugin_id: str,
        target_version: str
    ) -> Tuple[bool, str]:
        """Update a plugin to a specific version"""
        return self.registry.upgrade_plugin(plugin_id, target_version)
    
    async def rollback_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Rollback a plugin to previous version"""
        return self.registry.rollback_plugin(plugin_id)
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin"""
        version = self.registry.get_active_version(plugin_id)
        
        if not version:
            return None
        
        return {
            "plugin_id": plugin_id,
            "version": version.version_string,
            "author": version.author,
            "features": version.features,
            "deprecated": version.deprecated,
            "dependencies": [
                d.to_dict() for d in self.dependency_graph.get_dependencies(plugin_id)
            ],
            "dependents": self.dependency_graph.get_dependents(plugin_id),
            "available_versions": [
                v.version_string for v in self.registry.list_available_versions(plugin_id)
            ]
        }
    
    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """Get information about all active plugins"""
        plugins = []
        
        for plugin_id in self.registry.active_plugins:
            info = self.get_plugin_info(plugin_id)
            if info:
                plugins.append(info)
        
        return plugins
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lifecycle manager statistics"""
        return {
            "registry": self.registry.get_stats(),
            "dependency_graph": {
                "total_plugins": len(self.dependency_graph.get_all_plugins()),
                "circular_dependencies": len(self.dependency_graph.detect_circular_dependencies())
            },
            "update_history": len(self.update_manager.get_update_history()),
            "rollback_history": len(self.rollback_system.get_rollback_history())
        }


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_plugin_lifecycle_manager(
    db_path: str,
    plugins_dir: str = "plugins",
    backup_dir: str = "plugin_backups"
) -> PluginLifecycleManager:
    """Factory function to create a PluginLifecycleManager"""
    return PluginLifecycleManager(db_path, plugins_dir, backup_dir)


def create_versioned_registry(
    db_path: str,
    plugins_dir: str = "plugins"
) -> VersionedPluginRegistry:
    """Factory function to create a VersionedPluginRegistry"""
    return VersionedPluginRegistry(db_path, plugins_dir)


def create_manifest_validator() -> ManifestValidator:
    """Factory function to create a ManifestValidator"""
    return ManifestValidator()


def create_dependency_graph() -> DependencyGraph:
    """Factory function to create a DependencyGraph"""
    return DependencyGraph()


def create_compatibility_checker(
    core_version: str = "5.0.0",
    api_version: str = "1.0.0",
    db_schema_version: str = "1.0.0"
) -> CompatibilityChecker:
    """Factory function to create a CompatibilityChecker"""
    return CompatibilityChecker(core_version, api_version, db_schema_version)


def parse_version(version_string: str) -> SemanticVersion:
    """Parse a version string into SemanticVersion"""
    return SemanticVersion.parse(version_string)
