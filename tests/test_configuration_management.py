"""Unit tests for configuration management (Phase 6)."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from claude_mcp_docqa_agent.config.config_manager import (
    ConfigManager,
    ConfigAuditEntry,
)
from claude_mcp_docqa_agent.mcp_server.config_tools import (
    CONFIG_TOOLS,
    get_config,
    get_rules,
    validate_config,
    update_config,
    create_rule,
    get_audit_trail,
    get_versions,
    rollback_config,
    reload_config,
)


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create settings.yaml
        settings = {
            "document_processing": {
                "supported_formats": ["pdf", "docx"],
                "max_file_size_mb": 100,
            },
            "quality": {
                "min_language_confidence": 0.7,
                "max_critical_issues": 10,
            },
            "reporting": {"generate_json": True, "generate_html": True},
        }
        with open(config_dir / "settings.yaml", "w") as f:
            yaml.dump(settings, f)

        # Create default_rules.yaml
        rules = {
            "formatting_rules": [
                {
                    "id": "font_consistency",
                    "name": "Font Consistency",
                    "severity": "warning",
                    "enabled": True,
                }
            ]
        }
        with open(config_dir / "default_rules.yaml", "w") as f:
            yaml.dump(rules, f)

        yield config_dir


class TestConfigAuditEntry:
    """Test ConfigAuditEntry."""

    def test_audit_entry_creation(self):
        """Test creating audit entry."""
        entry = ConfigAuditEntry(
            timestamp=datetime(2026, 9, 28, 10, 0, 0),
            user="test_user",
            action="update",
            changes={"key": "value"},
        )
        assert entry.user == "test_user"
        assert entry.action == "update"

    def test_audit_entry_to_dict(self):
        """Test converting audit entry to dict."""
        entry = ConfigAuditEntry(
            timestamp=datetime(2026, 9, 28, 10, 0, 0),
            user="test_user",
            action="update",
            changes={"key": "value"},
        )
        entry_dict = entry.to_dict()

        assert entry_dict["user"] == "test_user"
        assert entry_dict["action"] == "update"
        assert "timestamp" in entry_dict


class TestConfigManager:
    """Test ConfigManager."""

    def test_config_manager_initialization(self, temp_config_dir):
        """Test ConfigManager initialization."""
        manager = ConfigManager(config_dir=temp_config_dir)
        assert manager.config_dir == temp_config_dir
        assert len(manager.config) > 0
        assert len(manager.rules) > 0

    def test_load_configuration(self, temp_config_dir):
        """Test loading configuration."""
        manager = ConfigManager(config_dir=temp_config_dir)

        # Check settings loaded
        assert "document_processing" in manager.config
        assert manager.config["document_processing"]["max_file_size_mb"] == 100

        # Check rules loaded
        assert "default_rules.yaml" in manager.rules

    def test_get_config_full(self, temp_config_dir):
        """Test getting full configuration."""
        manager = ConfigManager(config_dir=temp_config_dir)
        config = manager.get_config()

        assert isinstance(config, dict)
        assert "document_processing" in config

    def test_get_config_section(self, temp_config_dir):
        """Test getting configuration section."""
        manager = ConfigManager(config_dir=temp_config_dir)
        quality_config = manager.get_config("quality")

        assert "min_language_confidence" in quality_config

    def test_get_rules_all(self, temp_config_dir):
        """Test getting all rules."""
        manager = ConfigManager(config_dir=temp_config_dir)
        rules = manager.get_rules()

        assert isinstance(rules, dict)
        assert "default_rules.yaml" in rules

    def test_get_rules_specific(self, temp_config_dir):
        """Test getting specific rule file."""
        manager = ConfigManager(config_dir=temp_config_dir)
        rules = manager.get_rules("default_rules.yaml")

        assert "formatting_rules" in rules

    def test_validate_config_valid(self, temp_config_dir):
        """Test validating valid configuration."""
        manager = ConfigManager(config_dir=temp_config_dir)
        changes = {"quality": {"min_language_confidence": 0.8}}

        is_valid, message = manager.validate_config(changes)
        assert is_valid is True

    def test_validate_config_invalid_confidence(self, temp_config_dir):
        """Test validating invalid confidence."""
        manager = ConfigManager(config_dir=temp_config_dir)
        changes = {"quality": {"min_language_confidence": 1.5}}

        is_valid, message = manager.validate_config(changes)
        assert is_valid is False

    def test_validate_config_invalid_severity(self, temp_config_dir):
        """Test validating invalid severity level."""
        manager = ConfigManager(config_dir=temp_config_dir)
        changes = {
            "reporting": {"severity_levels": ["critical", "invalid_level"]}
        }

        is_valid, message = manager.validate_config(changes)
        assert is_valid is False

    def test_update_config(self, temp_config_dir):
        """Test updating configuration."""
        manager = ConfigManager(config_dir=temp_config_dir)
        changes = {"quality": {"min_language_confidence": 0.9}}

        success, message = manager.update_config(changes, user="test_user")
        assert success is True
        assert manager.config["quality"]["min_language_confidence"] == 0.9

    def test_update_config_invalid(self, temp_config_dir):
        """Test updating with invalid configuration."""
        manager = ConfigManager(config_dir=temp_config_dir)
        changes = {"quality": {"min_language_confidence": 1.5}}

        success, message = manager.update_config(changes)
        assert success is False

    def test_update_config_audit_trail(self, temp_config_dir):
        """Test that update creates audit entry."""
        manager = ConfigManager(config_dir=temp_config_dir)
        changes = {"quality": {"min_language_confidence": 0.9}}

        manager.update_config(
            changes, user="test_user", reason="Testing"
        )

        assert len(manager.audit_trail) > 0
        entry = manager.audit_trail[-1]
        assert entry.user == "test_user"
        assert entry.action == "update"

    def test_create_rule(self, temp_config_dir):
        """Test creating a new rule."""
        manager = ConfigManager(config_dir=temp_config_dir)
        rule_def = {
            "id": "test_rule",
            "name": "Test Rule",
            "severity": "warning",
            "enabled": True,
        }

        success, message = manager.create_rule(
            "default_rules.yaml", rule_def, user="test_user"
        )
        assert success is True
        assert len(manager.rules["default_rules.yaml"]["formatting_rules"]) > 0

    def test_create_rule_invalid(self, temp_config_dir):
        """Test creating rule without required fields."""
        manager = ConfigManager(config_dir=temp_config_dir)
        rule_def = {"name": "Test Rule"}  # Missing 'id'

        success, message = manager.create_rule(
            "default_rules.yaml", rule_def
        )
        assert success is False

    def test_create_rule_duplicate(self, temp_config_dir):
        """Test creating duplicate rule."""
        manager = ConfigManager(config_dir=temp_config_dir)
        rule_def = {
            "id": "font_consistency",
            "name": "Duplicate",
            "severity": "warning",
            "enabled": True,
        }

        success, message = manager.create_rule(
            "default_rules.yaml", rule_def
        )
        assert success is False

    def test_audit_trail_persistence(self, temp_config_dir):
        """Test that audit trail is persisted to disk."""
        manager1 = ConfigManager(config_dir=temp_config_dir)
        changes = {"quality": {"min_language_confidence": 0.9}}
        manager1.update_config(changes, user="user1")

        # Create new manager instance
        manager2 = ConfigManager(config_dir=temp_config_dir)
        assert len(manager2.audit_trail) > 0
        assert manager2.audit_trail[-1].user == "user1"

    def test_get_audit_trail_limit(self, temp_config_dir):
        """Test getting limited audit trail."""
        manager = ConfigManager(config_dir=temp_config_dir)

        # Create multiple audit entries
        for i in range(5):
            manager.update_config(
                {"quality": {"min_language_confidence": 0.7 + i * 0.01}},
                user=f"user{i}",
            )

        entries = manager.get_audit_trail(limit=2)
        assert len(entries) <= 2

    def test_version_creation(self, temp_config_dir):
        """Test creating configuration versions."""
        manager = ConfigManager(
            config_dir=temp_config_dir, enable_versions=True
        )
        changes = {"quality": {"min_language_confidence": 0.9}}

        manager.update_config(changes)

        versions = manager.get_versions()
        assert len(versions) > 0

    def test_rollback_config(self, temp_config_dir):
        """Test rolling back configuration."""
        manager = ConfigManager(
            config_dir=temp_config_dir, enable_versions=True
        )

        # Make first change
        manager.update_config(
            {"quality": {"min_language_confidence": 0.9}},
            user="user1",
        )
        versions = manager.get_versions()
        version_id = versions[0]

        # Make second change
        manager.update_config(
            {"quality": {"min_language_confidence": 0.5}},
            user="user2",
        )
        assert manager.config["quality"]["min_language_confidence"] == 0.5

        # Rollback
        success, message = manager.rollback_config(
            version_id, user="user3", reason="Testing rollback"
        )
        assert success is True

    def test_reload_from_disk(self, temp_config_dir):
        """Test reloading configuration from disk."""
        manager = ConfigManager(config_dir=temp_config_dir)

        # Modify file directly
        settings_file = temp_config_dir / "settings.yaml"
        with open(settings_file) as f:
            config = yaml.safe_load(f)
        config["quality"]["min_language_confidence"] = 0.5
        with open(settings_file, "w") as f:
            yaml.dump(config, f)

        # Reload
        success, message = manager.reload_from_disk()
        assert success is True
        assert manager.config["quality"]["min_language_confidence"] == 0.5

    def test_change_callback(self, temp_config_dir):
        """Test configuration change callback."""
        manager = ConfigManager(config_dir=temp_config_dir)

        callback_called = []

        def callback(section):
            callback_called.append(section)

        manager.register_change_callback(callback)
        manager.update_config({"quality": {"min_language_confidence": 0.9}})

        assert len(callback_called) > 0


class TestConfigTools:
    """Test MCP configuration tools."""

    def test_config_tools_defined(self):
        """Test that all config tools are defined."""
        tool_names = [t["name"] for t in CONFIG_TOOLS]

        expected = [
            "get_config",
            "get_rules",
            "validate_config",
            "update_config",
            "create_rule",
            "get_audit_trail",
            "get_versions",
            "rollback_config",
            "reload_config",
        ]

        for name in expected:
            assert name in tool_names

    def test_config_tools_have_schemas(self):
        """Test that all tools have input schemas."""
        for tool in CONFIG_TOOLS:
            assert "inputSchema" in tool
            assert "type" in tool["inputSchema"]

    def test_tool_get_config(self, temp_config_dir):
        """Test get_config tool."""
        from claude_mcp_docqa_agent.mcp_server.config_tools import (
            get_config_manager,
        )

        # Initialize manager with temp dir
        from unittest.mock import patch

        with patch(
            "claude_mcp_docqa_agent.mcp_server.config_tools._config_manager",
            ConfigManager(config_dir=temp_config_dir),
        ):
            # We need to set it directly since patching doesn't work well here
            import claude_mcp_docqa_agent.mcp_server.config_tools as ct

            ct._config_manager = ConfigManager(config_dir=temp_config_dir)
            result = get_config()

            assert result["status"] == "success"
            assert "config" in result

    def test_tool_validate_config(self, temp_config_dir):
        """Test validate_config tool."""
        import claude_mcp_docqa_agent.mcp_server.config_tools as ct

        ct._config_manager = ConfigManager(config_dir=temp_config_dir)

        result = validate_config(
            {"quality": {"min_language_confidence": 0.8}}
        )
        assert result["status"] == "success"
        assert result["is_valid"] is True

    def test_tool_validate_config_invalid(self, temp_config_dir):
        """Test validate_config with invalid data."""
        import claude_mcp_docqa_agent.mcp_server.config_tools as ct

        ct._config_manager = ConfigManager(config_dir=temp_config_dir)

        result = validate_config(
            {"quality": {"min_language_confidence": 1.5}}
        )
        assert result["status"] == "success"
        assert result["is_valid"] is False
