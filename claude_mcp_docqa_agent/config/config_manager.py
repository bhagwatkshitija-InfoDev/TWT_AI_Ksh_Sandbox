"""Configuration management with hot-reload and audit trail support."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict

import yaml
from pydantic import BaseModel, ValidationError

from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConfigAuditEntry:
    """Audit trail entry for configuration changes."""

    timestamp: datetime
    user: str
    action: str  # 'update', 'create_rule', 'rollback', 'reload'
    changes: dict[str, Any]
    reason: Optional[str] = None
    version: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "action": self.action,
            "changes": self.changes,
            "reason": self.reason,
            "version": self.version,
        }


class ConfigValidator(BaseModel):
    """Validator for configuration structure."""

    class Config:
        """Pydantic config."""
        extra = "allow"


class ConfigManager:
    """Manages application configuration with audit trail and rollback."""

    def __init__(
        self,
        config_dir: Path = None,
        enable_versions: bool = True,
        max_versions: int = 20,
    ):
        """Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files
            enable_versions: Whether to keep version history
            max_versions: Maximum number of versions to keep
        """
        if config_dir is None:
            config_dir = Path(__file__).parent

        self.config_dir = Path(config_dir)
        self.versions_dir = self.config_dir / "versions"
        self.audit_file = self.config_dir / "audit.json"
        self.enable_versions = enable_versions
        self.max_versions = max_versions

        # State
        self.config: dict[str, Any] = {}
        self.rules: dict[str, Any] = {}
        self.audit_trail: list[ConfigAuditEntry] = []

        # Callbacks for hot-reload
        self.change_callbacks: list[callable] = []

        # Initialize
        self._ensure_directories()
        self._load_configuration()
        self._load_audit_trail()

        logger.info("Initialized ConfigManager")

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if self.enable_versions:
            self.versions_dir.mkdir(parents=True, exist_ok=True)

    def _load_configuration(self) -> None:
        """Load all configuration files."""
        logger.info("Loading configuration files")

        # Load main settings
        settings_file = self.config_dir / "settings.yaml"
        if settings_file.exists():
            with open(settings_file) as f:
                self.config = yaml.safe_load(f) or {}
            logger.info("Loaded settings.yaml")

        # Load rules files
        rule_files = [
            "default_rules.yaml",
            "german_conventions.yaml",
            "chinese_conventions.yaml",
        ]

        for rule_file in rule_files:
            rule_path = self.config_dir / rule_file
            if rule_path.exists():
                with open(rule_path) as f:
                    rule_data = yaml.safe_load(f) or {}
                    self.rules[rule_file] = rule_data
                logger.info(f"Loaded {rule_file}")

    def _load_audit_trail(self) -> None:
        """Load audit trail from file."""
        if self.audit_file.exists():
            try:
                with open(self.audit_file) as f:
                    entries = json.load(f)
                    self.audit_trail = [
                        ConfigAuditEntry(
                            timestamp=datetime.fromisoformat(entry["timestamp"]),
                            user=entry["user"],
                            action=entry["action"],
                            changes=entry["changes"],
                            reason=entry.get("reason"),
                            version=entry.get("version"),
                        )
                        for entry in entries
                    ]
                logger.info(f"Loaded {len(self.audit_trail)} audit entries")
            except Exception as e:
                logger.warning(f"Failed to load audit trail: {e}")
                self.audit_trail = []

    def _save_audit_trail(self) -> None:
        """Save audit trail to file."""
        try:
            with open(self.audit_file, "w") as f:
                json.dump(
                    [entry.to_dict() for entry in self.audit_trail],
                    f,
                    indent=2,
                    default=str,
                )
            logger.info("Saved audit trail")
        except Exception as e:
            logger.error(f"Failed to save audit trail: {e}")

    def _create_version(self) -> str:
        """Create a backup version of current configuration.

        Returns:
            Version identifier (timestamp)
        """
        if not self.enable_versions:
            return None

        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_dir = self.versions_dir / version_id

        try:
            version_dir.mkdir(parents=True, exist_ok=True)

            # Copy all config files
            for config_file in self.config_dir.glob("*.yaml"):
                if config_file.name != "audit.json":
                    shutil.copy(config_file, version_dir / config_file.name)

            logger.info(f"Created version: {version_id}")

            # Cleanup old versions
            self._cleanup_old_versions()

            return version_id

        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            return None

    def _cleanup_old_versions(self) -> None:
        """Remove old versions beyond max_versions."""
        if not self.enable_versions:
            return

        try:
            versions = sorted(
                [d for d in self.versions_dir.iterdir() if d.is_dir()],
                reverse=True,
            )

            if len(versions) > self.max_versions:
                for old_version in versions[self.max_versions :]:
                    shutil.rmtree(old_version)
                    logger.info(f"Removed old version: {old_version.name}")

        except Exception as e:
            logger.warning(f"Failed to cleanup old versions: {e}")

    def _add_audit_entry(
        self,
        user: str,
        action: str,
        changes: dict[str, Any],
        reason: Optional[str] = None,
        version: Optional[str] = None,
    ) -> None:
        """Add entry to audit trail.

        Args:
            user: User making the change
            action: Action type
            changes: Dictionary of changes
            reason: Reason for change
            version: Version ID if applicable
        """
        entry = ConfigAuditEntry(
            timestamp=datetime.now(),
            user=user,
            action=action,
            changes=changes,
            reason=reason,
            version=version,
        )
        self.audit_trail.append(entry)
        self._save_audit_trail()

    def _notify_change(self, config_section: str) -> None:
        """Notify callbacks of configuration change (hot-reload).

        Args:
            config_section: Section that changed
        """
        for callback in self.change_callbacks:
            try:
                callback(config_section)
            except Exception as e:
                logger.error(f"Error in change callback: {e}")

    def register_change_callback(self, callback: callable) -> None:
        """Register callback for configuration changes.

        Args:
            callback: Function to call with (config_section) when config changes
        """
        self.change_callbacks.append(callback)
        logger.info("Registered change callback")

    def get_config(self, section: str = None) -> dict[str, Any]:
        """Get configuration.

        Args:
            section: Optional section to retrieve

        Returns:
            Configuration dictionary
        """
        if section is None:
            return self.config.copy()

        return self.config.get(section, {})

    def get_rules(self, rule_file: str = None) -> dict[str, Any]:
        """Get rules.

        Args:
            rule_file: Optional specific rule file

        Returns:
            Rules dictionary
        """
        if rule_file is None:
            return self.rules.copy()

        return self.rules.get(rule_file, {})

    def validate_config(self, proposed_changes: dict[str, Any]) -> tuple[bool, str]:
        """Validate proposed configuration changes.

        Args:
            proposed_changes: Dictionary of proposed changes

        Returns:
            (is_valid, message)
        """
        try:
            # Check for required fields
            if "quality" in proposed_changes:
                quality = proposed_changes["quality"]
                if "min_language_confidence" in quality:
                    conf = quality["min_language_confidence"]
                    if not (0 <= conf <= 1):
                        return (
                            False,
                            "min_language_confidence must be between 0 and 1",
                        )

            # Check reporting settings
            if "reporting" in proposed_changes:
                reporting = proposed_changes["reporting"]
                if "severity_levels" in reporting:
                    valid_levels = ["critical", "warning", "info"]
                    for level in reporting["severity_levels"]:
                        if level not in valid_levels:
                            return (
                                False,
                                f"Invalid severity level: {level}",
                            )

            return True, "Configuration is valid"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def update_config(
        self,
        changes: dict[str, Any],
        user: str = "system",
        reason: str = None,
    ) -> tuple[bool, str]:
        """Update configuration with audit trail.

        Args:
            changes: Dictionary of changes to apply
            user: User making the change
            reason: Reason for change

        Returns:
            (success, message)
        """
        # Validate changes
        is_valid, validation_msg = self.validate_config(changes)
        if not is_valid:
            logger.error(f"Invalid configuration: {validation_msg}")
            return False, validation_msg

        try:
            # Create version backup
            version_id = self._create_version()

            # Apply changes
            for key, value in changes.items():
                if key in self.config and isinstance(self.config[key], dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value

            # Save to file
            settings_file = self.config_dir / "settings.yaml"
            with open(settings_file, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)

            # Add audit entry
            self._add_audit_entry(
                user=user,
                action="update",
                changes=changes,
                reason=reason,
                version=version_id,
            )

            # Notify callbacks
            for key in changes.keys():
                self._notify_change(key)

            logger.info(f"Updated configuration: {list(changes.keys())}")
            return True, "Configuration updated successfully"

        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False, f"Update failed: {str(e)}"

    def create_rule(
        self,
        rule_file: str,
        rule_definition: dict[str, Any],
        user: str = "system",
        reason: str = None,
    ) -> tuple[bool, str]:
        """Create a new rule.

        Args:
            rule_file: Which rule file to add to
            rule_definition: Rule definition
            user: User creating the rule
            reason: Reason for creating rule

        Returns:
            (success, message)
        """
        try:
            # Validate rule definition
            if "id" not in rule_definition:
                return False, "Rule must have an 'id' field"
            if "name" not in rule_definition:
                return False, "Rule must have a 'name' field"

            # Load or create rules file
            if rule_file not in self.rules:
                self.rules[rule_file] = {"formatting_rules": []}

            rule_file_path = self.config_dir / rule_file

            # Check for duplicate ID
            existing_rules = self.rules[rule_file].get("formatting_rules", [])
            for rule in existing_rules:
                if rule.get("id") == rule_definition["id"]:
                    return False, f"Rule with ID '{rule_definition['id']}' already exists"

            # Create version backup
            version_id = self._create_version()

            # Add rule
            existing_rules.append(rule_definition)
            self.rules[rule_file]["formatting_rules"] = existing_rules

            # Save to file
            with open(rule_file_path, "w") as f:
                yaml.dump(self.rules[rule_file], f, default_flow_style=False)

            # Add audit entry
            self._add_audit_entry(
                user=user,
                action="create_rule",
                changes={rule_definition["id"]: rule_definition},
                reason=reason,
                version=version_id,
            )

            logger.info(f"Created rule: {rule_definition['id']}")
            return True, f"Rule '{rule_definition['id']}' created successfully"

        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            return False, f"Rule creation failed: {str(e)}"

    def get_audit_trail(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get audit trail entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        return [entry.to_dict() for entry in self.audit_trail[-limit:]]

    def get_versions(self) -> list[str]:
        """Get available configuration versions.

        Returns:
            List of version IDs
        """
        if not self.enable_versions:
            return []

        try:
            versions = sorted(
                [d.name for d in self.versions_dir.iterdir() if d.is_dir()],
                reverse=True,
            )
            return versions
        except Exception as e:
            logger.error(f"Failed to list versions: {e}")
            return []

    def rollback_config(
        self,
        version_id: str,
        user: str = "system",
        reason: str = None,
    ) -> tuple[bool, str]:
        """Rollback configuration to a previous version.

        Args:
            version_id: Version ID to rollback to
            user: User performing rollback
            reason: Reason for rollback

        Returns:
            (success, message)
        """
        if not self.enable_versions:
            return False, "Version history is disabled"

        version_dir = self.versions_dir / version_id
        if not version_dir.exists():
            return False, f"Version '{version_id}' not found"

        try:
            # Create backup of current state first
            backup_version = self._create_version()

            # Copy files from version
            for config_file in version_dir.glob("*.yaml"):
                shutil.copy(config_file, self.config_dir / config_file.name)

            # Reload configuration
            self._load_configuration()

            # Add audit entry
            self._add_audit_entry(
                user=user,
                action="rollback",
                changes={"previous_version": backup_version, "restored_version": version_id},
                reason=reason,
                version=version_id,
            )

            # Notify callbacks
            self._notify_change("all")

            logger.info(f"Rolled back to version: {version_id}")
            return True, f"Rolled back to version {version_id}"

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False, f"Rollback failed: {str(e)}"

    def reload_from_disk(self, user: str = "system") -> tuple[bool, str]:
        """Reload configuration from disk (for manual YAML edits).

        Args:
            user: User performing reload

        Returns:
            (success, message)
        """
        try:
            self._load_configuration()

            # Add audit entry
            self._add_audit_entry(
                user=user,
                action="reload",
                changes={"source": "disk"},
                reason="Manual reload from disk",
            )

            logger.info("Reloaded configuration from disk")
            return True, "Configuration reloaded from disk"

        except Exception as e:
            logger.error(f"Failed to reload from disk: {e}")
            return False, f"Reload failed: {str(e)}"
