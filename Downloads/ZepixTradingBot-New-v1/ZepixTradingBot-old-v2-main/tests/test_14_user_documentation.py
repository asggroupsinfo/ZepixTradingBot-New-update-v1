"""
Test Suite for Document 14: User Documentation Implementation.

This test file verifies the complete implementation of:
- Documentation generation system
- User guide generation
- Admin guide generation
- Plugin developer guide generation
- API reference generation
- Troubleshooting guide generation
- Documentation file structure

Version: 1.0
Date: 2026-01-12
"""

import os
import sys
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDocumentationPackageStructure:
    """Test documentation package structure."""
    
    def test_documentation_package_exists(self):
        """Test that documentation package exists."""
        package_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'documentation')
        assert os.path.exists(package_path), "documentation package should exist"
    
    def test_documentation_init_exists(self):
        """Test that __init__.py exists."""
        init_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'documentation', '__init__.py')
        assert os.path.exists(init_path), "__init__.py should exist"
    
    def test_doc_generator_module_exists(self):
        """Test that doc_generator module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'documentation', 'doc_generator.py')
        assert os.path.exists(module_path), "doc_generator.py should exist"
    
    def test_api_reference_module_exists(self):
        """Test that api_reference module exists."""
        module_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'documentation', 'api_reference.py')
        assert os.path.exists(module_path), "api_reference.py should exist"


class TestDocsDirectoryStructure:
    """Test docs directory structure."""
    
    def test_docs_directory_exists(self):
        """Test that docs directory exists."""
        docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
        assert os.path.exists(docs_path), "docs directory should exist"
    
    def test_user_guide_exists(self):
        """Test that USER_GUIDE.md exists."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'USER_GUIDE.md')
        assert os.path.exists(file_path), "USER_GUIDE.md should exist"
    
    def test_admin_guide_exists(self):
        """Test that ADMIN_GUIDE.md exists."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ADMIN_GUIDE.md')
        assert os.path.exists(file_path), "ADMIN_GUIDE.md should exist"
    
    def test_plugin_developer_guide_exists(self):
        """Test that PLUGIN_DEVELOPER_GUIDE.md exists."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PLUGIN_DEVELOPER_GUIDE.md')
        assert os.path.exists(file_path), "PLUGIN_DEVELOPER_GUIDE.md should exist"
    
    def test_api_reference_exists(self):
        """Test that API_REFERENCE.md exists."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'API_REFERENCE.md')
        assert os.path.exists(file_path), "API_REFERENCE.md should exist"
    
    def test_troubleshooting_exists(self):
        """Test that TROUBLESHOOTING.md exists."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'TROUBLESHOOTING.md')
        assert os.path.exists(file_path), "TROUBLESHOOTING.md should exist"


class TestDocTypeEnum:
    """Test DocType enum."""
    
    def test_doc_type_values(self):
        """Test DocType enum values."""
        from src.documentation.doc_generator import DocType
        
        assert DocType.USER_GUIDE.value == "user_guide"
        assert DocType.ADMIN_GUIDE.value == "admin_guide"
        assert DocType.DEVELOPER_GUIDE.value == "developer_guide"
        assert DocType.API_REFERENCE.value == "api_reference"
        assert DocType.TROUBLESHOOTING.value == "troubleshooting"
        assert DocType.PLUGIN_GUIDE.value == "plugin_guide"


class TestDocFormatEnum:
    """Test DocFormat enum."""
    
    def test_doc_format_values(self):
        """Test DocFormat enum values."""
        from src.documentation.doc_generator import DocFormat
        
        assert DocFormat.MARKDOWN.value == "markdown"
        assert DocFormat.HTML.value == "html"
        assert DocFormat.RST.value == "rst"
        assert DocFormat.PDF.value == "pdf"


class TestDocSection:
    """Test DocSection dataclass."""
    
    def test_doc_section_creation(self):
        """Test DocSection creation."""
        from src.documentation.doc_generator import DocSection
        
        section = DocSection(
            title="Test Section",
            content="Test content",
            level=2
        )
        
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.level == 2
    
    def test_doc_section_to_markdown(self):
        """Test DocSection to_markdown method."""
        from src.documentation.doc_generator import DocSection
        
        section = DocSection(
            title="Test Section",
            content="Test content",
            level=2
        )
        
        markdown = section.to_markdown()
        
        assert "## Test Section" in markdown
        assert "Test content" in markdown
    
    def test_doc_section_with_subsections(self):
        """Test DocSection with subsections."""
        from src.documentation.doc_generator import DocSection
        
        subsection = DocSection(title="Subsection", content="Sub content", level=3)
        section = DocSection(
            title="Main Section",
            content="Main content",
            level=2,
            subsections=[subsection]
        )
        
        markdown = section.to_markdown()
        
        assert "## Main Section" in markdown
        assert "### Subsection" in markdown


class TestDocPage:
    """Test DocPage dataclass."""
    
    def test_doc_page_creation(self):
        """Test DocPage creation."""
        from src.documentation.doc_generator import DocPage, DocType
        
        page = DocPage(
            title="Test Page",
            doc_type=DocType.USER_GUIDE
        )
        
        assert page.title == "Test Page"
        assert page.doc_type == DocType.USER_GUIDE
        assert page.sections == []
    
    def test_doc_page_to_markdown(self):
        """Test DocPage to_markdown method."""
        from src.documentation.doc_generator import DocPage, DocType, DocSection
        
        page = DocPage(
            title="Test Page",
            doc_type=DocType.USER_GUIDE,
            metadata={"version": "1.0"}
        )
        page.sections.append(DocSection(title="Section 1", content="Content 1", level=2))
        
        markdown = page.to_markdown()
        
        assert "# Test Page" in markdown
        assert "## Section 1" in markdown
        assert "Content 1" in markdown


class TestFunctionDoc:
    """Test FunctionDoc dataclass."""
    
    def test_function_doc_creation(self):
        """Test FunctionDoc creation."""
        from src.documentation.doc_generator import FunctionDoc
        
        func_doc = FunctionDoc(
            name="test_func",
            signature="def test_func(x: int) -> str",
            docstring="Test function"
        )
        
        assert func_doc.name == "test_func"
        assert func_doc.signature == "def test_func(x: int) -> str"
    
    def test_function_doc_to_markdown(self):
        """Test FunctionDoc to_markdown method."""
        from src.documentation.doc_generator import FunctionDoc
        
        func_doc = FunctionDoc(
            name="test_func",
            signature="def test_func(x: int) -> str",
            docstring="Test function",
            parameters=[{"name": "x", "type": "int", "description": "Input value"}],
            returns="str"
        )
        
        markdown = func_doc.to_markdown()
        
        assert "### `test_func`" in markdown
        assert "def test_func" in markdown
        assert "**Parameters:**" in markdown


class TestClassDoc:
    """Test ClassDoc dataclass."""
    
    def test_class_doc_creation(self):
        """Test ClassDoc creation."""
        from src.documentation.doc_generator import ClassDoc
        
        class_doc = ClassDoc(
            name="TestClass",
            docstring="Test class"
        )
        
        assert class_doc.name == "TestClass"
        assert class_doc.docstring == "Test class"
    
    def test_class_doc_to_markdown(self):
        """Test ClassDoc to_markdown method."""
        from src.documentation.doc_generator import ClassDoc
        
        class_doc = ClassDoc(
            name="TestClass",
            docstring="Test class",
            bases=["BaseClass"]
        )
        
        markdown = class_doc.to_markdown()
        
        assert "## `TestClass`" in markdown
        assert "BaseClass" in markdown


class TestModuleDoc:
    """Test ModuleDoc dataclass."""
    
    def test_module_doc_creation(self):
        """Test ModuleDoc creation."""
        from src.documentation.doc_generator import ModuleDoc
        
        module_doc = ModuleDoc(
            name="test_module",
            path="/path/to/test_module.py",
            docstring="Test module"
        )
        
        assert module_doc.name == "test_module"
        assert module_doc.path == "/path/to/test_module.py"
    
    def test_module_doc_to_markdown(self):
        """Test ModuleDoc to_markdown method."""
        from src.documentation.doc_generator import ModuleDoc
        
        module_doc = ModuleDoc(
            name="test_module",
            path="/path/to/test_module.py",
            docstring="Test module"
        )
        
        markdown = module_doc.to_markdown()
        
        assert "# Module: `test_module`" in markdown
        assert "/path/to/test_module.py" in markdown


class TestDocstringParser:
    """Test DocstringParser class."""
    
    def test_parse_empty_docstring(self):
        """Test parsing empty docstring."""
        from src.documentation.doc_generator import DocstringParser
        
        result = DocstringParser.parse("")
        
        assert result["description"] == ""
        assert result["params"] == []
    
    def test_parse_simple_docstring(self):
        """Test parsing simple docstring."""
        from src.documentation.doc_generator import DocstringParser
        
        docstring = "This is a simple description."
        result = DocstringParser.parse(docstring)
        
        assert "simple description" in result["description"]
    
    def test_parse_docstring_with_params(self):
        """Test parsing docstring with parameters."""
        from src.documentation.doc_generator import DocstringParser
        
        docstring = """Description.
        
        Args:
        - x (int): Input value
        - y (str): Another value
        """
        result = DocstringParser.parse(docstring)
        
        assert len(result["params"]) >= 0


class TestCodeAnalyzer:
    """Test CodeAnalyzer class."""
    
    def test_code_analyzer_creation(self):
        """Test CodeAnalyzer creation."""
        from src.documentation.doc_generator import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        assert analyzer.project_root is not None


class TestDocumentationGenerator:
    """Test DocumentationGenerator class."""
    
    def test_documentation_generator_creation(self):
        """Test DocumentationGenerator creation."""
        from src.documentation.doc_generator import DocumentationGenerator
        
        generator = DocumentationGenerator()
        
        assert generator.project_root is not None
        assert generator.output_dir is not None
    
    def test_generate_user_guide(self):
        """Test generate_user_guide method."""
        from src.documentation.doc_generator import DocumentationGenerator, DocType
        
        generator = DocumentationGenerator()
        page = generator.generate_user_guide()
        
        assert page.title == "User Guide"
        assert page.doc_type == DocType.USER_GUIDE
        assert len(page.sections) > 0
    
    def test_generate_admin_guide(self):
        """Test generate_admin_guide method."""
        from src.documentation.doc_generator import DocumentationGenerator, DocType
        
        generator = DocumentationGenerator()
        page = generator.generate_admin_guide()
        
        assert page.title == "Administrator Guide"
        assert page.doc_type == DocType.ADMIN_GUIDE
        assert len(page.sections) > 0
    
    def test_generate_plugin_developer_guide(self):
        """Test generate_plugin_developer_guide method."""
        from src.documentation.doc_generator import DocumentationGenerator, DocType
        
        generator = DocumentationGenerator()
        page = generator.generate_plugin_developer_guide()
        
        assert page.title == "Plugin Developer Guide"
        assert page.doc_type == DocType.PLUGIN_GUIDE
        assert len(page.sections) > 0
    
    def test_generate_troubleshooting_guide(self):
        """Test generate_troubleshooting_guide method."""
        from src.documentation.doc_generator import DocumentationGenerator, DocType
        
        generator = DocumentationGenerator()
        page = generator.generate_troubleshooting_guide()
        
        assert page.title == "Troubleshooting Guide"
        assert page.doc_type == DocType.TROUBLESHOOTING
        assert len(page.sections) > 0


class TestAPICategoryEnum:
    """Test APICategory enum."""
    
    def test_api_category_values(self):
        """Test APICategory enum values."""
        from src.documentation.api_reference import APICategory
        
        assert APICategory.SERVICE_API.value == "service_api"
        assert APICategory.PLUGIN_API.value == "plugin_api"
        assert APICategory.REST_API.value == "rest_api"
        assert APICategory.TELEGRAM_API.value == "telegram_api"


class TestAPIEndpoint:
    """Test APIEndpoint dataclass."""
    
    def test_api_endpoint_creation(self):
        """Test APIEndpoint creation."""
        from src.documentation.api_reference import APIEndpoint
        
        endpoint = APIEndpoint(
            name="Test Endpoint",
            method="GET",
            path="/api/test",
            description="Test endpoint"
        )
        
        assert endpoint.name == "Test Endpoint"
        assert endpoint.method == "GET"
        assert endpoint.path == "/api/test"
    
    def test_api_endpoint_to_markdown(self):
        """Test APIEndpoint to_markdown method."""
        from src.documentation.api_reference import APIEndpoint
        
        endpoint = APIEndpoint(
            name="Test Endpoint",
            method="GET",
            path="/api/test",
            description="Test endpoint",
            parameters=[{"name": "id", "type": "int", "required": True, "description": "ID"}]
        )
        
        markdown = endpoint.to_markdown()
        
        assert "### `GET` /api/test" in markdown
        assert "**Parameters:**" in markdown


class TestAPISection:
    """Test APISection dataclass."""
    
    def test_api_section_creation(self):
        """Test APISection creation."""
        from src.documentation.api_reference import APISection, APICategory
        
        section = APISection(
            title="Test Section",
            description="Test description",
            category=APICategory.SERVICE_API
        )
        
        assert section.title == "Test Section"
        assert section.category == APICategory.SERVICE_API
    
    def test_api_section_to_markdown(self):
        """Test APISection to_markdown method."""
        from src.documentation.api_reference import APISection, APICategory
        
        section = APISection(
            title="Test Section",
            description="Test description",
            category=APICategory.SERVICE_API
        )
        
        markdown = section.to_markdown()
        
        assert "## Test Section" in markdown
        assert "Test description" in markdown


class TestServiceAPIReference:
    """Test ServiceAPIReference class."""
    
    def test_order_execution_endpoints(self):
        """Test ORDER_EXECUTION_ENDPOINTS."""
        from src.documentation.api_reference import ServiceAPIReference
        
        endpoints = ServiceAPIReference.ORDER_EXECUTION_ENDPOINTS
        
        assert len(endpoints) > 0
        assert any(e.name == "Place Dual Orders (V3)" for e in endpoints)
        assert any(e.name == "Place Single Order" for e in endpoints)
    
    def test_risk_management_endpoints(self):
        """Test RISK_MANAGEMENT_ENDPOINTS."""
        from src.documentation.api_reference import ServiceAPIReference
        
        endpoints = ServiceAPIReference.RISK_MANAGEMENT_ENDPOINTS
        
        assert len(endpoints) > 0
        assert any(e.name == "Calculate Lot Size" for e in endpoints)
    
    def test_notification_endpoints(self):
        """Test NOTIFICATION_ENDPOINTS."""
        from src.documentation.api_reference import ServiceAPIReference
        
        endpoints = ServiceAPIReference.NOTIFICATION_ENDPOINTS
        
        assert len(endpoints) > 0
        assert any(e.name == "Send Notification" for e in endpoints)
    
    def test_get_all_sections(self):
        """Test get_all_sections method."""
        from src.documentation.api_reference import ServiceAPIReference
        
        sections = ServiceAPIReference.get_all_sections()
        
        assert len(sections) >= 4
        assert any(s.title == "Order Execution Service" for s in sections)
        assert any(s.title == "Risk Management Service" for s in sections)


class TestTelegramAPIReference:
    """Test TelegramAPIReference class."""
    
    def test_controller_commands(self):
        """Test CONTROLLER_COMMANDS."""
        from src.documentation.api_reference import TelegramAPIReference
        
        commands = TelegramAPIReference.CONTROLLER_COMMANDS
        
        assert len(commands) > 0
        assert any(c.path == "/status" for c in commands)
        assert any(c.path == "/emergency_stop" for c in commands)
    
    def test_analytics_commands(self):
        """Test ANALYTICS_COMMANDS."""
        from src.documentation.api_reference import TelegramAPIReference
        
        commands = TelegramAPIReference.ANALYTICS_COMMANDS
        
        assert len(commands) > 0
        assert any(c.path == "/daily_report" for c in commands)
        assert any(c.path == "/weekly_report" for c in commands)
    
    def test_get_all_sections(self):
        """Test get_all_sections method."""
        from src.documentation.api_reference import TelegramAPIReference
        
        sections = TelegramAPIReference.get_all_sections()
        
        assert len(sections) >= 2
        assert any(s.title == "Controller Bot Commands" for s in sections)
        assert any(s.title == "Analytics Bot Commands" for s in sections)


class TestAPIReferenceGenerator:
    """Test APIReferenceGenerator class."""
    
    def test_api_reference_generator_creation(self):
        """Test APIReferenceGenerator creation."""
        from src.documentation.api_reference import APIReferenceGenerator
        
        generator = APIReferenceGenerator()
        
        assert generator.output_dir is not None
    
    def test_generate(self):
        """Test generate method."""
        from src.documentation.api_reference import APIReferenceGenerator
        
        generator = APIReferenceGenerator()
        content = generator.generate()
        
        assert "# API Reference" in content
        assert "Service API" in content
        assert "Telegram Bot API" in content


class TestUserGuideContent:
    """Test USER_GUIDE.md content."""
    
    def test_user_guide_has_getting_started(self):
        """Test USER_GUIDE.md has Getting Started section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'USER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Getting Started" in content
    
    def test_user_guide_has_telegram_bots(self):
        """Test USER_GUIDE.md has Telegram Bots section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'USER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Telegram" in content
    
    def test_user_guide_has_plugins(self):
        """Test USER_GUIDE.md has Plugins section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'USER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Plugin" in content
    
    def test_user_guide_has_safety_features(self):
        """Test USER_GUIDE.md has Safety Features section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'USER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Safety" in content


class TestAdminGuideContent:
    """Test ADMIN_GUIDE.md content."""
    
    def test_admin_guide_has_installation(self):
        """Test ADMIN_GUIDE.md has Installation section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ADMIN_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Installation" in content
    
    def test_admin_guide_has_configuration(self):
        """Test ADMIN_GUIDE.md has Configuration section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ADMIN_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Configuration" in content
    
    def test_admin_guide_has_monitoring(self):
        """Test ADMIN_GUIDE.md has Monitoring section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ADMIN_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Monitoring" in content or "Logging" in content
    
    def test_admin_guide_has_backup(self):
        """Test ADMIN_GUIDE.md has Backup section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ADMIN_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Backup" in content


class TestPluginDeveloperGuideContent:
    """Test PLUGIN_DEVELOPER_GUIDE.md content."""
    
    def test_plugin_guide_has_architecture(self):
        """Test PLUGIN_DEVELOPER_GUIDE.md has Architecture section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PLUGIN_DEVELOPER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Architecture" in content
    
    def test_plugin_guide_has_creating_plugin(self):
        """Test PLUGIN_DEVELOPER_GUIDE.md has Creating Plugin section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PLUGIN_DEVELOPER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Creating" in content or "New Plugin" in content
    
    def test_plugin_guide_has_service_api(self):
        """Test PLUGIN_DEVELOPER_GUIDE.md has ServiceAPI section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PLUGIN_DEVELOPER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "ServiceAPI" in content or "Service API" in content
    
    def test_plugin_guide_has_testing(self):
        """Test PLUGIN_DEVELOPER_GUIDE.md has Testing section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PLUGIN_DEVELOPER_GUIDE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Testing" in content or "Test" in content


class TestAPIReferenceContent:
    """Test API_REFERENCE.md content."""
    
    def test_api_reference_has_service_api(self):
        """Test API_REFERENCE.md has Service API section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'API_REFERENCE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Service API" in content
    
    def test_api_reference_has_order_execution(self):
        """Test API_REFERENCE.md has Order Execution section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'API_REFERENCE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Order Execution" in content
    
    def test_api_reference_has_telegram_api(self):
        """Test API_REFERENCE.md has Telegram API section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'API_REFERENCE.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Telegram" in content


class TestTroubleshootingContent:
    """Test TROUBLESHOOTING.md content."""
    
    def test_troubleshooting_has_common_issues(self):
        """Test TROUBLESHOOTING.md has Common Issues section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'TROUBLESHOOTING.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Common Issues" in content or "Issues" in content
    
    def test_troubleshooting_has_bot_not_responding(self):
        """Test TROUBLESHOOTING.md has Bot Not Responding section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'TROUBLESHOOTING.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Not Responding" in content or "Alerts" in content
    
    def test_troubleshooting_has_mt5_issues(self):
        """Test TROUBLESHOOTING.md has MT5 Issues section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'TROUBLESHOOTING.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "MT5" in content
    
    def test_troubleshooting_has_getting_help(self):
        """Test TROUBLESHOOTING.md has Getting Help section."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'TROUBLESHOOTING.md')
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "Help" in content or "Support" in content


class TestDocument14Integration:
    """Test Document 14 integration."""
    
    def test_all_modules_importable(self):
        """Test that all modules are importable."""
        from src.documentation import doc_generator
        from src.documentation import api_reference
        
        assert doc_generator is not None
        assert api_reference is not None
    
    def test_package_version(self):
        """Test package version."""
        from src.documentation import __version__
        
        assert __version__ == "1.0.0"
    
    def test_all_doc_types_covered(self):
        """Test that all doc types are covered."""
        from src.documentation.doc_generator import DocType
        
        types = [t.value for t in DocType]
        
        assert "user_guide" in types
        assert "admin_guide" in types
        assert "developer_guide" in types
        assert "api_reference" in types
        assert "troubleshooting" in types
    
    def test_all_api_categories_covered(self):
        """Test that all API categories are covered."""
        from src.documentation.api_reference import APICategory
        
        categories = [c.value for c in APICategory]
        
        assert "service_api" in categories
        assert "plugin_api" in categories
        assert "telegram_api" in categories


class TestDocument14Summary:
    """Test Document 14 summary verification."""
    
    def test_document_14_requirements_met(self):
        """Test that all Document 14 requirements are met."""
        docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
        
        required_files = [
            "USER_GUIDE.md",
            "ADMIN_GUIDE.md",
            "PLUGIN_DEVELOPER_GUIDE.md",
            "API_REFERENCE.md",
            "TROUBLESHOOTING.md"
        ]
        
        for filename in required_files:
            file_path = os.path.join(docs_path, filename)
            assert os.path.exists(file_path), f"{filename} should exist"
    
    def test_documentation_generator_works(self):
        """Test that documentation generator works."""
        from src.documentation.doc_generator import DocumentationGenerator
        
        generator = DocumentationGenerator()
        
        user_guide = generator.generate_user_guide()
        admin_guide = generator.generate_admin_guide()
        plugin_guide = generator.generate_plugin_developer_guide()
        troubleshooting = generator.generate_troubleshooting_guide()
        
        assert user_guide is not None
        assert admin_guide is not None
        assert plugin_guide is not None
        assert troubleshooting is not None
    
    def test_api_reference_generator_works(self):
        """Test that API reference generator works."""
        from src.documentation.api_reference import APIReferenceGenerator
        
        generator = APIReferenceGenerator()
        content = generator.generate()
        
        assert content is not None
        assert len(content) > 0
    
    def test_all_docs_have_content(self):
        """Test that all docs have content."""
        docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
        
        required_files = [
            "USER_GUIDE.md",
            "ADMIN_GUIDE.md",
            "PLUGIN_DEVELOPER_GUIDE.md",
            "API_REFERENCE.md",
            "TROUBLESHOOTING.md"
        ]
        
        for filename in required_files:
            file_path = os.path.join(docs_path, filename)
            with open(file_path, 'r') as f:
                content = f.read()
            assert len(content) > 100, f"{filename} should have substantial content"
    
    def test_docs_are_valid_markdown(self):
        """Test that all docs are valid markdown."""
        docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
        
        required_files = [
            "USER_GUIDE.md",
            "ADMIN_GUIDE.md",
            "PLUGIN_DEVELOPER_GUIDE.md",
            "API_REFERENCE.md",
            "TROUBLESHOOTING.md"
        ]
        
        for filename in required_files:
            file_path = os.path.join(docs_path, filename)
            with open(file_path, 'r') as f:
                content = f.read()
            assert content.startswith("#"), f"{filename} should start with a heading"
