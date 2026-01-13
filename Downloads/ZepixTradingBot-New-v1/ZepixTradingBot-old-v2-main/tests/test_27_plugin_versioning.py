"""
Document 27: Plugin Versioning & Compatibility System Tests

Comprehensive test suite for:
1. Semantic Versioning - SemVer enforcement
2. Dependency Graph - Plugin dependencies
3. Update Manager - Detect, backup, apply updates
4. Rollback System - Revert to previous version
5. Compatibility Checker - Plugin vs Core version
6. Manifest Validator - plugin_manifest.json validation
7. VersionedPluginRegistry - Enhanced registry with version management
8. PluginLifecycleManager - Complete lifecycle management
"""

import unittest
import asyncio
import sys
import os
import json
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPluginVersioningModuleStructure(unittest.TestCase):
    """Test that all required classes and enums exist"""
    
    def test_module_imports(self):
        """Test that the module can be imported"""
        from core import plugin_versioning
        self.assertIsNotNone(plugin_versioning)
    
    def test_version_bump_enum_exists(self):
        """Test VersionBump enum exists"""
        from core.plugin_versioning import VersionBump
        self.assertTrue(hasattr(VersionBump, 'MAJOR'))
        self.assertTrue(hasattr(VersionBump, 'MINOR'))
        self.assertTrue(hasattr(VersionBump, 'PATCH'))
    
    def test_compatibility_level_enum_exists(self):
        """Test CompatibilityLevel enum exists"""
        from core.plugin_versioning import CompatibilityLevel
        self.assertTrue(hasattr(CompatibilityLevel, 'FULLY_COMPATIBLE'))
        self.assertTrue(hasattr(CompatibilityLevel, 'BACKWARD_COMPATIBLE'))
        self.assertTrue(hasattr(CompatibilityLevel, 'INCOMPATIBLE'))
    
    def test_update_status_enum_exists(self):
        """Test UpdateStatus enum exists"""
        from core.plugin_versioning import UpdateStatus
        self.assertTrue(hasattr(UpdateStatus, 'PENDING'))
        self.assertTrue(hasattr(UpdateStatus, 'COMPLETED'))
        self.assertTrue(hasattr(UpdateStatus, 'FAILED'))
        self.assertTrue(hasattr(UpdateStatus, 'ROLLED_BACK'))
    
    def test_dependency_status_enum_exists(self):
        """Test DependencyStatus enum exists"""
        from core.plugin_versioning import DependencyStatus
        self.assertTrue(hasattr(DependencyStatus, 'SATISFIED'))
        self.assertTrue(hasattr(DependencyStatus, 'MISSING'))
        self.assertTrue(hasattr(DependencyStatus, 'VERSION_MISMATCH'))
    
    def test_semantic_version_exists(self):
        """Test SemanticVersion class exists"""
        from core.plugin_versioning import SemanticVersion
        self.assertTrue(callable(SemanticVersion))
    
    def test_plugin_version_exists(self):
        """Test PluginVersion class exists"""
        from core.plugin_versioning import PluginVersion
        self.assertTrue(callable(PluginVersion))
    
    def test_plugin_dependency_exists(self):
        """Test PluginDependency class exists"""
        from core.plugin_versioning import PluginDependency
        self.assertTrue(callable(PluginDependency))
    
    def test_plugin_manifest_exists(self):
        """Test PluginManifest class exists"""
        from core.plugin_versioning import PluginManifest
        self.assertTrue(callable(PluginManifest))
    
    def test_update_result_exists(self):
        """Test UpdateResult class exists"""
        from core.plugin_versioning import UpdateResult
        self.assertTrue(callable(UpdateResult))
    
    def test_manifest_validator_exists(self):
        """Test ManifestValidator class exists"""
        from core.plugin_versioning import ManifestValidator
        self.assertTrue(callable(ManifestValidator))
    
    def test_dependency_graph_exists(self):
        """Test DependencyGraph class exists"""
        from core.plugin_versioning import DependencyGraph
        self.assertTrue(callable(DependencyGraph))
    
    def test_compatibility_checker_exists(self):
        """Test CompatibilityChecker class exists"""
        from core.plugin_versioning import CompatibilityChecker
        self.assertTrue(callable(CompatibilityChecker))
    
    def test_update_manager_exists(self):
        """Test UpdateManager class exists"""
        from core.plugin_versioning import UpdateManager
        self.assertTrue(callable(UpdateManager))
    
    def test_rollback_system_exists(self):
        """Test RollbackSystem class exists"""
        from core.plugin_versioning import RollbackSystem
        self.assertTrue(callable(RollbackSystem))
    
    def test_versioned_plugin_registry_exists(self):
        """Test VersionedPluginRegistry class exists"""
        from core.plugin_versioning import VersionedPluginRegistry
        self.assertTrue(callable(VersionedPluginRegistry))
    
    def test_plugin_lifecycle_manager_exists(self):
        """Test PluginLifecycleManager class exists"""
        from core.plugin_versioning import PluginLifecycleManager
        self.assertTrue(callable(PluginLifecycleManager))


class TestSemanticVersion(unittest.TestCase):
    """Test SemanticVersion class"""
    
    def test_parse_simple_version(self):
        """Test parsing simple version string"""
        from core.plugin_versioning import SemanticVersion
        
        version = SemanticVersion.parse("1.2.3")
        
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
    
    def test_parse_version_with_prerelease(self):
        """Test parsing version with prerelease"""
        from core.plugin_versioning import SemanticVersion
        
        version = SemanticVersion.parse("1.2.3-alpha")
        
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.prerelease, "alpha")
    
    def test_parse_version_with_build_metadata(self):
        """Test parsing version with build metadata"""
        from core.plugin_versioning import SemanticVersion
        
        version = SemanticVersion.parse("1.2.3+build123")
        
        self.assertEqual(version.major, 1)
        self.assertEqual(version.build_metadata, "build123")
    
    def test_version_string(self):
        """Test version string representation"""
        from core.plugin_versioning import SemanticVersion
        
        version = SemanticVersion(major=3, minor=2, patch=1)
        
        self.assertEqual(str(version), "3.2.1")
    
    def test_version_comparison_less_than(self):
        """Test version less than comparison"""
        from core.plugin_versioning import SemanticVersion
        
        v1 = SemanticVersion.parse("1.0.0")
        v2 = SemanticVersion.parse("2.0.0")
        
        self.assertTrue(v1 < v2)
        self.assertFalse(v2 < v1)
    
    def test_version_comparison_equal(self):
        """Test version equality comparison"""
        from core.plugin_versioning import SemanticVersion
        
        v1 = SemanticVersion.parse("1.2.3")
        v2 = SemanticVersion.parse("1.2.3")
        
        self.assertEqual(v1, v2)
    
    def test_version_bump_major(self):
        """Test major version bump"""
        from core.plugin_versioning import SemanticVersion, VersionBump
        
        version = SemanticVersion.parse("1.2.3")
        bumped = version.bump(VersionBump.MAJOR)
        
        self.assertEqual(bumped.major, 2)
        self.assertEqual(bumped.minor, 0)
        self.assertEqual(bumped.patch, 0)
    
    def test_version_bump_minor(self):
        """Test minor version bump"""
        from core.plugin_versioning import SemanticVersion, VersionBump
        
        version = SemanticVersion.parse("1.2.3")
        bumped = version.bump(VersionBump.MINOR)
        
        self.assertEqual(bumped.major, 1)
        self.assertEqual(bumped.minor, 3)
        self.assertEqual(bumped.patch, 0)
    
    def test_version_bump_patch(self):
        """Test patch version bump"""
        from core.plugin_versioning import SemanticVersion, VersionBump
        
        version = SemanticVersion.parse("1.2.3")
        bumped = version.bump(VersionBump.PATCH)
        
        self.assertEqual(bumped.major, 1)
        self.assertEqual(bumped.minor, 2)
        self.assertEqual(bumped.patch, 4)
    
    def test_is_compatible_with_same_major(self):
        """Test compatibility with same major version"""
        from core.plugin_versioning import SemanticVersion
        
        v1 = SemanticVersion.parse("3.0.0")
        v2 = SemanticVersion.parse("3.1.0")
        
        self.assertTrue(v1.is_compatible_with(v2))
    
    def test_is_incompatible_with_different_major(self):
        """Test incompatibility with different major version"""
        from core.plugin_versioning import SemanticVersion
        
        v1 = SemanticVersion.parse("3.0.0")
        v2 = SemanticVersion.parse("4.0.0")
        
        self.assertFalse(v1.is_compatible_with(v2))
    
    def test_get_compatibility_level(self):
        """Test getting compatibility level"""
        from core.plugin_versioning import SemanticVersion, CompatibilityLevel
        
        v1 = SemanticVersion.parse("3.0.0")
        v2 = SemanticVersion.parse("3.1.0")
        v3 = SemanticVersion.parse("4.0.0")
        
        self.assertEqual(
            v1.get_compatibility_level(v2),
            CompatibilityLevel.BACKWARD_COMPATIBLE
        )
        self.assertEqual(
            v1.get_compatibility_level(v3),
            CompatibilityLevel.INCOMPATIBLE
        )
    
    def test_invalid_version_string(self):
        """Test parsing invalid version string raises error"""
        from core.plugin_versioning import SemanticVersion
        
        with self.assertRaises(ValueError):
            SemanticVersion.parse("invalid")


class TestPluginVersion(unittest.TestCase):
    """Test PluginVersion class"""
    
    def test_creation(self):
        """Test PluginVersion creation"""
        from core.plugin_versioning import PluginVersion
        
        version = PluginVersion(
            plugin_id="combined_v3",
            major=3,
            minor=2,
            patch=1
        )
        
        self.assertEqual(version.plugin_id, "combined_v3")
        self.assertEqual(version.major, 3)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 1)
    
    def test_version_string(self):
        """Test version_string property"""
        from core.plugin_versioning import PluginVersion
        
        version = PluginVersion(
            plugin_id="combined_v3",
            major=3,
            minor=2,
            patch=1
        )
        
        self.assertEqual(version.version_string, "3.2.1")
    
    def test_semantic_version_property(self):
        """Test semantic_version property"""
        from core.plugin_versioning import PluginVersion
        
        version = PluginVersion(
            plugin_id="combined_v3",
            major=3,
            minor=2,
            patch=1
        )
        
        sem_ver = version.semantic_version
        
        self.assertEqual(sem_ver.major, 3)
        self.assertEqual(sem_ver.minor, 2)
        self.assertEqual(sem_ver.patch, 1)
    
    def test_is_compatible_with_same_plugin(self):
        """Test compatibility with same plugin"""
        from core.plugin_versioning import PluginVersion
        
        v1 = PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="combined_v3", major=3, minor=1, patch=0)
        v3 = PluginVersion(plugin_id="combined_v3", major=4, minor=0, patch=0)
        
        self.assertTrue(v1.is_compatible_with(v2))
        self.assertFalse(v1.is_compatible_with(v3))
    
    def test_is_compatible_with_different_plugin(self):
        """Test compatibility with different plugin"""
        from core.plugin_versioning import PluginVersion
        
        v1 = PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="price_action_v6", major=6, minor=0, patch=0)
        
        self.assertTrue(v1.is_compatible_with(v2))
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.plugin_versioning import PluginVersion
        
        version = PluginVersion(
            plugin_id="combined_v3",
            major=3,
            minor=2,
            patch=1,
            author="Test Author",
            features=["hybrid_sl", "trend_pulse"]
        )
        
        data = version.to_dict()
        
        self.assertEqual(data["plugin_id"], "combined_v3")
        self.assertEqual(data["version_string"], "3.2.1")
        self.assertEqual(data["author"], "Test Author")
        self.assertIn("hybrid_sl", data["features"])
    
    def test_comparison(self):
        """Test version comparison"""
        from core.plugin_versioning import PluginVersion
        
        v1 = PluginVersion(plugin_id="test", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test", major=1, minor=1, patch=0)
        v3 = PluginVersion(plugin_id="test", major=1, minor=1, patch=1)
        
        self.assertTrue(v1 < v2)
        self.assertTrue(v2 < v3)
        self.assertFalse(v3 < v1)


class TestPluginDependency(unittest.TestCase):
    """Test PluginDependency class"""
    
    def test_creation(self):
        """Test PluginDependency creation"""
        from core.plugin_versioning import PluginDependency
        
        dep = PluginDependency(
            plugin_id="market_data",
            min_version="1.0.0",
            max_version="2.0.0",
            optional=False
        )
        
        self.assertEqual(dep.plugin_id, "market_data")
        self.assertEqual(dep.min_version, "1.0.0")
        self.assertEqual(dep.max_version, "2.0.0")
        self.assertFalse(dep.optional)
    
    def test_is_satisfied_by_valid_version(self):
        """Test dependency satisfied by valid version"""
        from core.plugin_versioning import PluginDependency, SemanticVersion
        
        dep = PluginDependency(
            plugin_id="market_data",
            min_version="1.0.0",
            max_version="2.0.0"
        )
        
        version = SemanticVersion.parse("1.5.0")
        
        self.assertTrue(dep.is_satisfied_by(version))
    
    def test_is_not_satisfied_by_low_version(self):
        """Test dependency not satisfied by low version"""
        from core.plugin_versioning import PluginDependency, SemanticVersion
        
        dep = PluginDependency(
            plugin_id="market_data",
            min_version="1.0.0"
        )
        
        version = SemanticVersion.parse("0.9.0")
        
        self.assertFalse(dep.is_satisfied_by(version))
    
    def test_is_not_satisfied_by_high_version(self):
        """Test dependency not satisfied by high version"""
        from core.plugin_versioning import PluginDependency, SemanticVersion
        
        dep = PluginDependency(
            plugin_id="market_data",
            min_version="1.0.0",
            max_version="2.0.0"
        )
        
        version = SemanticVersion.parse("3.0.0")
        
        self.assertFalse(dep.is_satisfied_by(version))
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.plugin_versioning import PluginDependency
        
        dep = PluginDependency(
            plugin_id="market_data",
            min_version="1.0.0",
            optional=True
        )
        
        data = dep.to_dict()
        
        self.assertEqual(data["plugin_id"], "market_data")
        self.assertEqual(data["min_version"], "1.0.0")
        self.assertTrue(data["optional"])


class TestPluginManifest(unittest.TestCase):
    """Test PluginManifest class"""
    
    def test_creation(self):
        """Test PluginManifest creation"""
        from core.plugin_versioning import PluginManifest
        
        manifest = PluginManifest(
            plugin_id="combined_v3",
            name="Combined V3 Plugin",
            version="3.0.0",
            description="V3 Combined Logic Plugin",
            author="Zepix Team"
        )
        
        self.assertEqual(manifest.plugin_id, "combined_v3")
        self.assertEqual(manifest.name, "Combined V3 Plugin")
        self.assertEqual(manifest.version, "3.0.0")
    
    def test_default_values(self):
        """Test default values"""
        from core.plugin_versioning import PluginManifest
        
        manifest = PluginManifest(
            plugin_id="test",
            name="Test",
            version="1.0.0",
            description="Test",
            author="Test"
        )
        
        self.assertEqual(manifest.entry_point, "plugin.py")
        self.assertEqual(manifest.config_file, "config.json")
        self.assertEqual(manifest.requires_core_version, "5.0.0")
    
    def test_to_dict(self):
        """Test to_dict method"""
        from core.plugin_versioning import PluginManifest, PluginDependency
        
        manifest = PluginManifest(
            plugin_id="combined_v3",
            name="Combined V3 Plugin",
            version="3.0.0",
            description="V3 Combined Logic Plugin",
            author="Zepix Team",
            dependencies=[
                PluginDependency(plugin_id="market_data", min_version="1.0.0")
            ],
            features=["hybrid_sl", "trend_pulse"]
        )
        
        data = manifest.to_dict()
        
        self.assertEqual(data["plugin_id"], "combined_v3")
        self.assertEqual(len(data["dependencies"]), 1)
        self.assertIn("hybrid_sl", data["features"])


class TestManifestValidator(unittest.TestCase):
    """Test ManifestValidator class"""
    
    def test_creation(self):
        """Test ManifestValidator creation"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        self.assertIsNotNone(validator)
    
    def test_validate_valid_manifest(self):
        """Test validating valid manifest"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        manifest_data = {
            "plugin_id": "combined_v3",
            "name": "Combined V3 Plugin",
            "version": "3.0.0",
            "description": "V3 Combined Logic Plugin",
            "author": "Zepix Team"
        }
        
        is_valid, errors, warnings = validator.validate(manifest_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_required_field(self):
        """Test validating manifest with missing required field"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        manifest_data = {
            "plugin_id": "combined_v3",
            "name": "Combined V3 Plugin"
        }
        
        is_valid, errors, warnings = validator.validate(manifest_data)
        
        self.assertFalse(is_valid)
        self.assertTrue(any("version" in e for e in errors))
    
    def test_validate_invalid_plugin_id(self):
        """Test validating manifest with invalid plugin_id"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        manifest_data = {
            "plugin_id": "Invalid-Plugin-ID",
            "name": "Test",
            "version": "1.0.0",
            "description": "Test",
            "author": "Test"
        }
        
        is_valid, errors, warnings = validator.validate(manifest_data)
        
        self.assertFalse(is_valid)
        self.assertTrue(any("plugin_id" in e for e in errors))
    
    def test_validate_invalid_version(self):
        """Test validating manifest with invalid version"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        manifest_data = {
            "plugin_id": "test_plugin",
            "name": "Test",
            "version": "invalid",
            "description": "Test",
            "author": "Test"
        }
        
        is_valid, errors, warnings = validator.validate(manifest_data)
        
        self.assertFalse(is_valid)
        self.assertTrue(any("version" in e for e in errors))
    
    def test_parse_manifest(self):
        """Test parsing manifest data"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        manifest_data = {
            "plugin_id": "combined_v3",
            "name": "Combined V3 Plugin",
            "version": "3.0.0",
            "description": "V3 Combined Logic Plugin",
            "author": "Zepix Team",
            "features": ["hybrid_sl"]
        }
        
        manifest = validator.parse_manifest(manifest_data)
        
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.plugin_id, "combined_v3")
        self.assertIn("hybrid_sl", manifest.features)
    
    def test_validate_file(self):
        """Test validating manifest file"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "plugin_manifest.json")
            
            manifest_data = {
                "plugin_id": "test_plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test"
            }
            
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f)
            
            is_valid, errors, warnings = validator.validate_file(manifest_path)
            
            self.assertTrue(is_valid)


class TestDependencyGraph(unittest.TestCase):
    """Test DependencyGraph class"""
    
    def test_creation(self):
        """Test DependencyGraph creation"""
        from core.plugin_versioning import DependencyGraph
        
        graph = DependencyGraph()
        
        self.assertIsNotNone(graph)
    
    def test_add_plugin(self):
        """Test adding plugin to graph"""
        from core.plugin_versioning import DependencyGraph, SemanticVersion, PluginDependency
        
        graph = DependencyGraph()
        
        graph.add_plugin(
            "combined_v3",
            SemanticVersion.parse("3.0.0"),
            [PluginDependency(plugin_id="market_data", min_version="1.0.0")]
        )
        
        deps = graph.get_dependencies("combined_v3")
        
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0].plugin_id, "market_data")
    
    def test_remove_plugin(self):
        """Test removing plugin from graph"""
        from core.plugin_versioning import DependencyGraph, SemanticVersion
        
        graph = DependencyGraph()
        
        graph.add_plugin("test_plugin", SemanticVersion.parse("1.0.0"), [])
        graph.remove_plugin("test_plugin")
        
        deps = graph.get_dependencies("test_plugin")
        
        self.assertEqual(len(deps), 0)
    
    def test_get_dependents(self):
        """Test getting dependents"""
        from core.plugin_versioning import DependencyGraph, SemanticVersion, PluginDependency
        
        graph = DependencyGraph()
        
        graph.add_plugin("market_data", SemanticVersion.parse("1.0.0"), [])
        graph.add_plugin(
            "combined_v3",
            SemanticVersion.parse("3.0.0"),
            [PluginDependency(plugin_id="market_data", min_version="1.0.0")]
        )
        
        dependents = graph.get_dependents("market_data")
        
        self.assertIn("combined_v3", dependents)
    
    def test_check_dependency_status(self):
        """Test checking dependency status"""
        from core.plugin_versioning import (
            DependencyGraph, SemanticVersion, PluginDependency, DependencyStatus
        )
        
        graph = DependencyGraph()
        
        graph.add_plugin(
            "combined_v3",
            SemanticVersion.parse("3.0.0"),
            [PluginDependency(plugin_id="market_data", min_version="1.0.0")]
        )
        
        available = {"market_data": SemanticVersion.parse("1.5.0")}
        
        status = graph.check_dependency_status("combined_v3", available)
        
        self.assertEqual(status["market_data"], DependencyStatus.SATISFIED)
    
    def test_check_missing_dependency(self):
        """Test checking missing dependency"""
        from core.plugin_versioning import (
            DependencyGraph, SemanticVersion, PluginDependency, DependencyStatus
        )
        
        graph = DependencyGraph()
        
        graph.add_plugin(
            "combined_v3",
            SemanticVersion.parse("3.0.0"),
            [PluginDependency(plugin_id="market_data", min_version="1.0.0")]
        )
        
        status = graph.check_dependency_status("combined_v3", {})
        
        self.assertEqual(status["market_data"], DependencyStatus.MISSING)
    
    def test_detect_circular_dependencies(self):
        """Test detecting circular dependencies"""
        from core.plugin_versioning import DependencyGraph, SemanticVersion, PluginDependency
        
        graph = DependencyGraph()
        
        graph.add_plugin(
            "plugin_a",
            SemanticVersion.parse("1.0.0"),
            [PluginDependency(plugin_id="plugin_b", min_version="1.0.0")]
        )
        graph.add_plugin(
            "plugin_b",
            SemanticVersion.parse("1.0.0"),
            [PluginDependency(plugin_id="plugin_a", min_version="1.0.0")]
        )
        
        cycles = graph.detect_circular_dependencies()
        
        self.assertTrue(len(cycles) > 0)
    
    def test_get_installation_order(self):
        """Test getting installation order"""
        from core.plugin_versioning import DependencyGraph, SemanticVersion, PluginDependency
        
        graph = DependencyGraph()
        
        graph.add_plugin("base", SemanticVersion.parse("1.0.0"), [])
        graph.add_plugin(
            "dependent",
            SemanticVersion.parse("1.0.0"),
            [PluginDependency(plugin_id="base", min_version="1.0.0")]
        )
        
        order = graph.get_installation_order()
        
        base_idx = order.index("base")
        dep_idx = order.index("dependent")
        
        self.assertTrue(base_idx < dep_idx)
    
    def test_can_remove(self):
        """Test checking if plugin can be removed"""
        from core.plugin_versioning import DependencyGraph, SemanticVersion, PluginDependency
        
        graph = DependencyGraph()
        
        graph.add_plugin("base", SemanticVersion.parse("1.0.0"), [])
        graph.add_plugin(
            "dependent",
            SemanticVersion.parse("1.0.0"),
            [PluginDependency(plugin_id="base", min_version="1.0.0")]
        )
        
        can_remove, blocking = graph.can_remove("base")
        
        self.assertFalse(can_remove)
        self.assertIn("dependent", blocking)


class TestCompatibilityChecker(unittest.TestCase):
    """Test CompatibilityChecker class"""
    
    def test_creation(self):
        """Test CompatibilityChecker creation"""
        from core.plugin_versioning import CompatibilityChecker
        
        checker = CompatibilityChecker(
            core_version="5.0.0",
            api_version="1.0.0",
            db_schema_version="1.0.0"
        )
        
        self.assertIsNotNone(checker)
    
    def test_check_compatible_plugin(self):
        """Test checking compatible plugin"""
        from core.plugin_versioning import CompatibilityChecker, PluginManifest
        
        checker = CompatibilityChecker(
            core_version="5.0.0",
            api_version="1.0.0",
            db_schema_version="1.0.0"
        )
        
        manifest = PluginManifest(
            plugin_id="test",
            name="Test",
            version="1.0.0",
            description="Test",
            author="Test",
            requires_core_version="5.0.0",
            requires_api_version="1.0.0",
            requires_db_schema="1.0.0"
        )
        
        compatible, issues = checker.check_plugin_compatibility(manifest)
        
        self.assertTrue(compatible)
        self.assertEqual(len(issues), 0)
    
    def test_check_incompatible_plugin(self):
        """Test checking incompatible plugin"""
        from core.plugin_versioning import CompatibilityChecker, PluginManifest
        
        checker = CompatibilityChecker(
            core_version="5.0.0",
            api_version="1.0.0",
            db_schema_version="1.0.0"
        )
        
        manifest = PluginManifest(
            plugin_id="test",
            name="Test",
            version="1.0.0",
            description="Test",
            author="Test",
            requires_core_version="6.0.0"
        )
        
        compatible, issues = checker.check_plugin_compatibility(manifest)
        
        self.assertFalse(compatible)
        self.assertTrue(len(issues) > 0)
    
    def test_check_plugin_pair_compatibility(self):
        """Test checking plugin pair compatibility"""
        from core.plugin_versioning import CompatibilityChecker, PluginVersion
        
        checker = CompatibilityChecker()
        
        v1 = PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="combined_v3", major=3, minor=1, patch=0)
        v3 = PluginVersion(plugin_id="combined_v3", major=4, minor=0, patch=0)
        
        compatible1, _ = checker.check_plugin_pair_compatibility(v1, v2)
        compatible2, _ = checker.check_plugin_pair_compatibility(v1, v3)
        
        self.assertTrue(compatible1)
        self.assertFalse(compatible2)
    
    def test_get_compatibility_matrix(self):
        """Test getting compatibility matrix"""
        from core.plugin_versioning import CompatibilityChecker, PluginVersion
        
        checker = CompatibilityChecker()
        
        plugins = [
            PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0),
            PluginVersion(plugin_id="price_action_v6", major=6, minor=0, patch=0)
        ]
        
        matrix = checker.get_compatibility_matrix(plugins)
        
        self.assertEqual(len(matrix), 2)


class TestUpdateManager(unittest.TestCase):
    """Test UpdateManager class"""
    
    def test_creation(self):
        """Test UpdateManager creation"""
        from core.plugin_versioning import UpdateManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = os.path.join(tmpdir, "plugins")
            backup_dir = os.path.join(tmpdir, "backups")
            
            manager = UpdateManager(plugins_dir, backup_dir)
            
            self.assertIsNotNone(manager)
    
    def test_check_for_updates(self):
        """Test checking for updates"""
        from core.plugin_versioning import UpdateManager, PluginVersion
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                
                manager = UpdateManager(plugins_dir, backup_dir)
                
                current = {
                    "combined_v3": PluginVersion(
                        plugin_id="combined_v3", major=3, minor=0, patch=0
                    )
                }
                
                available = {
                    "combined_v3": [
                        PluginVersion(plugin_id="combined_v3", major=3, minor=1, patch=0),
                        PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
                    ]
                }
                
                updates = await manager.check_for_updates(current, available)
                
                self.assertIn("combined_v3", updates)
                self.assertEqual(updates["combined_v3"].version_string, "3.1.0")
        
        asyncio.run(run_test())
    
    def test_backup_plugin(self):
        """Test backing up plugin"""
        from core.plugin_versioning import UpdateManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                
                os.makedirs(plugins_dir)
                
                plugin_path = os.path.join(plugins_dir, "test_plugin")
                os.makedirs(plugin_path)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Test plugin")
                
                manager = UpdateManager(plugins_dir, backup_dir)
                
                backup_path = await manager.backup_plugin("test_plugin")
                
                self.assertIsNotNone(backup_path)
                self.assertTrue(os.path.exists(backup_path))
        
        asyncio.run(run_test())
    
    def test_apply_update(self):
        """Test applying update"""
        from core.plugin_versioning import UpdateManager, PluginVersion, UpdateStatus
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                update_source = os.path.join(tmpdir, "update_source")
                
                os.makedirs(plugins_dir)
                os.makedirs(update_source)
                
                plugin_path = os.path.join(plugins_dir, "test_plugin")
                os.makedirs(plugin_path)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Old version")
                
                with open(os.path.join(update_source, "plugin.py"), 'w') as f:
                    f.write("# New version")
                
                manager = UpdateManager(plugins_dir, backup_dir)
                
                new_version = PluginVersion(
                    plugin_id="test_plugin", major=1, minor=1, patch=0
                )
                
                result = await manager.apply_update(
                    "test_plugin", new_version, update_source
                )
                
                self.assertTrue(result.success)
                self.assertEqual(result.status, UpdateStatus.COMPLETED)
        
        asyncio.run(run_test())
    
    def test_restore_from_backup(self):
        """Test restoring from backup"""
        from core.plugin_versioning import UpdateManager
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                
                os.makedirs(plugins_dir)
                
                plugin_path = os.path.join(plugins_dir, "test_plugin")
                os.makedirs(plugin_path)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Original version")
                
                manager = UpdateManager(plugins_dir, backup_dir)
                
                backup_path = await manager.backup_plugin("test_plugin")
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Modified version")
                
                success = await manager.restore_from_backup("test_plugin", backup_path)
                
                self.assertTrue(success)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'r') as f:
                    content = f.read()
                
                self.assertIn("Original version", content)
        
        asyncio.run(run_test())


class TestRollbackSystem(unittest.TestCase):
    """Test RollbackSystem class"""
    
    def test_creation(self):
        """Test RollbackSystem creation"""
        from core.plugin_versioning import RollbackSystem, UpdateManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = os.path.join(tmpdir, "plugins")
            backup_dir = os.path.join(tmpdir, "backups")
            
            update_manager = UpdateManager(plugins_dir, backup_dir)
            rollback_system = RollbackSystem(update_manager)
            
            self.assertIsNotNone(rollback_system)
    
    def test_rollback_plugin(self):
        """Test rolling back plugin"""
        from core.plugin_versioning import (
            RollbackSystem, UpdateManager, PluginVersion, UpdateStatus
        )
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                update_source = os.path.join(tmpdir, "update_source")
                
                os.makedirs(plugins_dir)
                os.makedirs(update_source)
                
                plugin_path = os.path.join(plugins_dir, "test_plugin")
                os.makedirs(plugin_path)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Version 1.0.0")
                
                with open(os.path.join(update_source, "plugin.py"), 'w') as f:
                    f.write("# Version 1.1.0")
                
                update_manager = UpdateManager(plugins_dir, backup_dir)
                rollback_system = RollbackSystem(update_manager)
                
                new_version = PluginVersion(
                    plugin_id="test_plugin", major=1, minor=1, patch=0
                )
                
                await update_manager.apply_update(
                    "test_plugin", new_version, update_source
                )
                
                result = await rollback_system.rollback_plugin("test_plugin")
                
                self.assertTrue(result.success)
                self.assertEqual(result.status, UpdateStatus.ROLLED_BACK)
        
        asyncio.run(run_test())
    
    def test_get_available_rollback_versions(self):
        """Test getting available rollback versions"""
        from core.plugin_versioning import (
            RollbackSystem, UpdateManager, PluginVersion
        )
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                update_source = os.path.join(tmpdir, "update_source")
                
                os.makedirs(plugins_dir)
                os.makedirs(update_source)
                
                plugin_path = os.path.join(plugins_dir, "test_plugin")
                os.makedirs(plugin_path)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Version 1.0.0")
                
                manifest_data = {"version": "1.0.0"}
                with open(os.path.join(plugin_path, "plugin_manifest.json"), 'w') as f:
                    json.dump(manifest_data, f)
                
                with open(os.path.join(update_source, "plugin.py"), 'w') as f:
                    f.write("# Version 1.1.0")
                
                update_manager = UpdateManager(plugins_dir, backup_dir)
                rollback_system = RollbackSystem(update_manager)
                
                new_version = PluginVersion(
                    plugin_id="test_plugin", major=1, minor=1, patch=0
                )
                
                await update_manager.apply_update(
                    "test_plugin", new_version, update_source
                )
                
                versions = rollback_system.get_available_rollback_versions("test_plugin")
                
                self.assertIn("1.0.0", versions)
        
        asyncio.run(run_test())


class TestVersionedPluginRegistry(unittest.TestCase):
    """Test VersionedPluginRegistry class"""
    
    def test_creation(self):
        """Test VersionedPluginRegistry creation"""
        from core.plugin_versioning import VersionedPluginRegistry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            self.assertIsNotNone(registry)
    
    def test_register_plugin(self):
        """Test registering plugin"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0
            )
            
            success, msg = registry.register_plugin("combined_v3", version)
            
            self.assertTrue(success)
    
    def test_get_active_version(self):
        """Test getting active version"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0
            )
            
            registry.register_plugin("combined_v3", version)
            
            active = registry.get_active_version("combined_v3")
            
            self.assertIsNotNone(active)
            self.assertEqual(active.version_string, "3.0.0")
    
    def test_add_version(self):
        """Test adding version to registry"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0,
                author="Test"
            )
            
            registry.add_version(version)
            
            available = registry.list_available_versions("combined_v3")
            
            self.assertEqual(len(available), 1)
    
    def test_upgrade_plugin(self):
        """Test upgrading plugin"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            v1 = PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
            v2 = PluginVersion(plugin_id="combined_v3", major=3, minor=1, patch=0)
            
            registry.add_version(v1)
            registry.add_version(v2)
            registry.register_plugin("combined_v3", v1)
            
            success, msg = registry.upgrade_plugin("combined_v3", "3.1.0")
            
            self.assertTrue(success)
            
            active = registry.get_active_version("combined_v3")
            self.assertEqual(active.version_string, "3.1.0")
    
    def test_rollback_plugin(self):
        """Test rolling back plugin"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            v1 = PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
            v2 = PluginVersion(plugin_id="combined_v3", major=3, minor=1, patch=0)
            
            registry.add_version(v1)
            registry.add_version(v2)
            registry.register_plugin("combined_v3", v2)
            
            success, msg = registry.rollback_plugin("combined_v3")
            
            self.assertTrue(success)
            
            active = registry.get_active_version("combined_v3")
            self.assertEqual(active.version_string, "3.0.0")
    
    def test_deprecate_version(self):
        """Test deprecating version"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0
            )
            
            registry.add_version(version)
            
            success = registry.deprecate_version("combined_v3", "3.0.0")
            
            self.assertTrue(success)
    
    def test_get_stats(self):
        """Test getting registry stats"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0
            )
            
            registry.add_version(version)
            registry.register_plugin("combined_v3", version)
            
            stats = registry.get_stats()
            
            self.assertEqual(stats["active_plugins"], 1)
            self.assertEqual(stats["total_versions"], 1)


class TestPluginLifecycleManager(unittest.TestCase):
    """Test PluginLifecycleManager class"""
    
    def test_creation(self):
        """Test PluginLifecycleManager creation"""
        from core.plugin_versioning import PluginLifecycleManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            manager = PluginLifecycleManager(db_path, plugins_dir)
            
            self.assertIsNotNone(manager)
            self.assertIsNotNone(manager.registry)
            self.assertIsNotNone(manager.manifest_validator)
            self.assertIsNotNone(manager.dependency_graph)
            self.assertIsNotNone(manager.compatibility_checker)
    
    def test_get_all_plugins(self):
        """Test getting all plugins"""
        from core.plugin_versioning import PluginLifecycleManager, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            manager = PluginLifecycleManager(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0
            )
            
            manager.registry.add_version(version)
            manager.registry.register_plugin("combined_v3", version)
            
            plugins = manager.get_all_plugins()
            
            self.assertEqual(len(plugins), 1)
            self.assertEqual(plugins[0]["plugin_id"], "combined_v3")
    
    def test_get_stats(self):
        """Test getting lifecycle manager stats"""
        from core.plugin_versioning import PluginLifecycleManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            manager = PluginLifecycleManager(db_path, plugins_dir)
            
            stats = manager.get_stats()
            
            self.assertIn("registry", stats)
            self.assertIn("dependency_graph", stats)
            self.assertIn("update_history", stats)
            self.assertIn("rollback_history", stats)


class TestFactoryFunctions(unittest.TestCase):
    """Test factory functions"""
    
    def test_create_plugin_lifecycle_manager(self):
        """Test create_plugin_lifecycle_manager factory"""
        from core.plugin_versioning import create_plugin_lifecycle_manager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            
            manager = create_plugin_lifecycle_manager(db_path)
            
            self.assertIsNotNone(manager)
    
    def test_create_versioned_registry(self):
        """Test create_versioned_registry factory"""
        from core.plugin_versioning import create_versioned_registry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            
            registry = create_versioned_registry(db_path)
            
            self.assertIsNotNone(registry)
    
    def test_create_manifest_validator(self):
        """Test create_manifest_validator factory"""
        from core.plugin_versioning import create_manifest_validator
        
        validator = create_manifest_validator()
        
        self.assertIsNotNone(validator)
    
    def test_create_dependency_graph(self):
        """Test create_dependency_graph factory"""
        from core.plugin_versioning import create_dependency_graph
        
        graph = create_dependency_graph()
        
        self.assertIsNotNone(graph)
    
    def test_create_compatibility_checker(self):
        """Test create_compatibility_checker factory"""
        from core.plugin_versioning import create_compatibility_checker
        
        checker = create_compatibility_checker()
        
        self.assertIsNotNone(checker)
    
    def test_parse_version(self):
        """Test parse_version function"""
        from core.plugin_versioning import parse_version
        
        version = parse_version("3.2.1")
        
        self.assertEqual(version.major, 3)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 1)


class TestDocument27Requirements(unittest.TestCase):
    """Test all Document 27 specific requirements"""
    
    def test_semantic_versioning_enforcement(self):
        """Test SemVer enforcement (Major.Minor.Patch)"""
        from core.plugin_versioning import SemanticVersion, VersionBump
        
        version = SemanticVersion.parse("3.2.1")
        
        self.assertEqual(version.major, 3)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 1)
        
        bumped_major = version.bump(VersionBump.MAJOR)
        self.assertEqual(str(bumped_major), "4.0.0")
        
        bumped_minor = version.bump(VersionBump.MINOR)
        self.assertEqual(str(bumped_minor), "3.3.0")
        
        bumped_patch = version.bump(VersionBump.PATCH)
        self.assertEqual(str(bumped_patch), "3.2.2")
    
    def test_dependency_graph_implementation(self):
        """Test dependency graph for plugin dependencies"""
        from core.plugin_versioning import (
            DependencyGraph, SemanticVersion, PluginDependency
        )
        
        graph = DependencyGraph()
        
        graph.add_plugin("market_data", SemanticVersion.parse("1.0.0"), [])
        
        graph.add_plugin(
            "combined_v3",
            SemanticVersion.parse("3.0.0"),
            [PluginDependency(plugin_id="market_data", min_version="1.0.0")]
        )
        
        deps = graph.get_dependencies("combined_v3")
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0].plugin_id, "market_data")
        
        dependents = graph.get_dependents("market_data")
        self.assertIn("combined_v3", dependents)
    
    def test_update_manager_implementation(self):
        """Test update manager (detect, backup, apply)"""
        from core.plugin_versioning import UpdateManager, PluginVersion
        
        async def run_test():
            with tempfile.TemporaryDirectory() as tmpdir:
                plugins_dir = os.path.join(tmpdir, "plugins")
                backup_dir = os.path.join(tmpdir, "backups")
                
                os.makedirs(plugins_dir)
                
                plugin_path = os.path.join(plugins_dir, "test_plugin")
                os.makedirs(plugin_path)
                
                with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
                    f.write("# Test")
                
                manager = UpdateManager(plugins_dir, backup_dir)
                
                current = {
                    "test_plugin": PluginVersion(
                        plugin_id="test_plugin", major=1, minor=0, patch=0
                    )
                }
                available = {
                    "test_plugin": [
                        PluginVersion(plugin_id="test_plugin", major=1, minor=1, patch=0)
                    ]
                }
                
                updates = await manager.check_for_updates(current, available)
                self.assertIn("test_plugin", updates)
                
                backup_path = await manager.backup_plugin("test_plugin")
                self.assertIsNotNone(backup_path)
        
        asyncio.run(run_test())
    
    def test_rollback_system_implementation(self):
        """Test rollback system (revert to previous version)"""
        from core.plugin_versioning import RollbackSystem, UpdateManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = os.path.join(tmpdir, "plugins")
            backup_dir = os.path.join(tmpdir, "backups")
            
            update_manager = UpdateManager(plugins_dir, backup_dir)
            rollback_system = RollbackSystem(update_manager)
            
            self.assertIsNotNone(rollback_system)
            self.assertTrue(hasattr(rollback_system, 'rollback_plugin'))
            self.assertTrue(hasattr(rollback_system, 'rollback_to_version'))
    
    def test_compatibility_checker_implementation(self):
        """Test compatibility checker (plugin vs Core version)"""
        from core.plugin_versioning import CompatibilityChecker, PluginManifest
        
        checker = CompatibilityChecker(
            core_version="5.0.0",
            api_version="1.0.0",
            db_schema_version="1.0.0"
        )
        
        compatible_manifest = PluginManifest(
            plugin_id="test",
            name="Test",
            version="1.0.0",
            description="Test",
            author="Test",
            requires_core_version="5.0.0"
        )
        
        compatible, issues = checker.check_plugin_compatibility(compatible_manifest)
        self.assertTrue(compatible)
        
        incompatible_manifest = PluginManifest(
            plugin_id="test",
            name="Test",
            version="1.0.0",
            description="Test",
            author="Test",
            requires_core_version="6.0.0"
        )
        
        compatible, issues = checker.check_plugin_compatibility(incompatible_manifest)
        self.assertFalse(compatible)
    
    def test_manifest_validator_implementation(self):
        """Test manifest validator (plugin_manifest.json)"""
        from core.plugin_versioning import ManifestValidator
        
        validator = ManifestValidator()
        
        valid_manifest = {
            "plugin_id": "combined_v3",
            "name": "Combined V3 Plugin",
            "version": "3.0.0",
            "description": "V3 Combined Logic Plugin",
            "author": "Zepix Team"
        }
        
        is_valid, errors, warnings = validator.validate(valid_manifest)
        self.assertTrue(is_valid)
        
        invalid_manifest = {
            "plugin_id": "Invalid-ID",
            "name": "Test"
        }
        
        is_valid, errors, warnings = validator.validate(invalid_manifest)
        self.assertFalse(is_valid)
    
    def test_versioned_registry_implementation(self):
        """Test versioned plugin registry"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            v1 = PluginVersion(plugin_id="combined_v3", major=3, minor=0, patch=0)
            v2 = PluginVersion(plugin_id="combined_v3", major=3, minor=1, patch=0)
            
            registry.add_version(v1)
            registry.add_version(v2)
            
            registry.register_plugin("combined_v3", v1)
            
            active = registry.get_active_version("combined_v3")
            self.assertEqual(active.version_string, "3.0.0")
            
            registry.upgrade_plugin("combined_v3", "3.1.0")
            
            active = registry.get_active_version("combined_v3")
            self.assertEqual(active.version_string, "3.1.0")
            
            registry.rollback_plugin("combined_v3")
            
            active = registry.get_active_version("combined_v3")
            self.assertEqual(active.version_string, "3.0.0")
    
    def test_plugin_lifecycle_manager_implementation(self):
        """Test complete plugin lifecycle manager"""
        from core.plugin_versioning import PluginLifecycleManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            manager = PluginLifecycleManager(db_path, plugins_dir)
            
            self.assertIsNotNone(manager.registry)
            self.assertIsNotNone(manager.manifest_validator)
            self.assertIsNotNone(manager.dependency_graph)
            self.assertIsNotNone(manager.compatibility_checker)
            self.assertIsNotNone(manager.update_manager)
            self.assertIsNotNone(manager.rollback_system)


class TestDocument27Summary(unittest.TestCase):
    """Summary tests for Document 27 implementation"""
    
    def test_all_components_importable(self):
        """Test all components can be imported"""
        from core.plugin_versioning import (
            VersionBump,
            CompatibilityLevel,
            UpdateStatus,
            DependencyStatus,
            SemanticVersion,
            PluginVersion,
            PluginDependency,
            PluginManifest,
            UpdateResult,
            DependencyNode,
            ManifestValidator,
            DependencyGraph,
            CompatibilityChecker,
            UpdateManager,
            RollbackSystem,
            VersionedPluginRegistry,
            PluginLifecycleManager,
            create_plugin_lifecycle_manager,
            create_versioned_registry,
            create_manifest_validator,
            create_dependency_graph,
            create_compatibility_checker,
            parse_version
        )
        
        self.assertTrue(True)
    
    def test_version_compatibility_rules(self):
        """Test version compatibility rules from Document 27"""
        from core.plugin_versioning import SemanticVersion, CompatibilityLevel
        
        v3_0_0 = SemanticVersion.parse("3.0.0")
        v3_0_1 = SemanticVersion.parse("3.0.1")
        v3_1_0 = SemanticVersion.parse("3.1.0")
        v4_0_0 = SemanticVersion.parse("4.0.0")
        
        self.assertTrue(v3_0_0.is_compatible_with(v3_0_1))
        self.assertTrue(v3_0_0.is_compatible_with(v3_1_0))
        
        self.assertFalse(v3_0_0.is_compatible_with(v4_0_0))
        
        self.assertEqual(
            v3_0_0.get_compatibility_level(v3_0_1),
            CompatibilityLevel.BACKWARD_COMPATIBLE
        )
        self.assertEqual(
            v3_0_0.get_compatibility_level(v4_0_0),
            CompatibilityLevel.INCOMPATIBLE
        )
    
    def test_plugin_version_comparison(self):
        """Test plugin version comparison from Document 27"""
        from core.plugin_versioning import PluginVersion
        
        v1 = PluginVersion(plugin_id="test", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test", major=3, minor=1, patch=0)
        v3 = PluginVersion(plugin_id="test", major=3, minor=1, patch=1)
        
        self.assertTrue(v1 < v2)
        self.assertTrue(v2 < v3)
        self.assertFalse(v3 < v1)
    
    def test_database_schema_created(self):
        """Test database schema is created correctly"""
        from core.plugin_versioning import VersionedPluginRegistry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='plugin_versions'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='plugin_version_history'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            conn.close()
    
    def test_telegram_command_support(self):
        """Test Telegram command support structures exist"""
        from core.plugin_versioning import VersionedPluginRegistry, PluginVersion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            plugins_dir = os.path.join(tmpdir, "plugins")
            
            registry = VersionedPluginRegistry(db_path, plugins_dir)
            
            version = PluginVersion(
                plugin_id="combined_v3",
                major=3,
                minor=0,
                patch=0,
                features=["hybrid_sl", "trend_pulse"]
            )
            
            registry.add_version(version)
            registry.register_plugin("combined_v3", version)
            
            active = registry.get_active_version("combined_v3")
            self.assertIsNotNone(active)
            self.assertEqual(active.version_string, "3.0.0")
            
            available = registry.list_available_versions("combined_v3")
            self.assertEqual(len(available), 1)
            
            history = registry.get_version_history("combined_v3")
            self.assertTrue(len(history) > 0)


if __name__ == '__main__':
    unittest.main()
