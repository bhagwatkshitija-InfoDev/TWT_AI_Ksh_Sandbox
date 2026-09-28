"""MCP Configuration Management Tools."""

import json
from typing import Any

from claude_mcp_docqa_agent.config.config_manager import ConfigManager
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)

# Global config manager instance
_config_manager: ConfigManager = None


def get_config_manager() -> ConfigManager:
    """Get or initialize the global config manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# Tool Definitions
CONFIG_TOOLS = [
    {
        "name": "get_config",
        "description": "Retrieve current configuration settings or a specific section",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Optional config section (e.g., 'quality', 'analysis', 'reporting'). If empty, returns full config.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_rules",
        "description": "Retrieve rule definitions from a specific rule file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_file": {
                    "type": "string",
                    "description": "Which rule file to retrieve (e.g., 'default_rules.yaml', 'german_conventions.yaml', 'chinese_conventions.yaml')",
                }
            },
            "required": [],
        },
    },
    {
        "name": "validate_config",
        "description": "Validate proposed configuration changes before applying them",
        "inputSchema": {
            "type": "object",
            "properties": {
                "proposed_changes": {
                    "type": "object",
                    "description": "Dictionary of proposed configuration changes",
                }
            },
            "required": ["proposed_changes"],
        },
    },
    {
        "name": "update_config",
        "description": "Update configuration settings with audit trail",
        "inputSchema": {
            "type": "object",
            "properties": {
                "changes": {
                    "type": "object",
                    "description": "Dictionary of configuration changes to apply",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the configuration change",
                },
            },
            "required": ["changes"],
        },
    },
    {
        "name": "create_rule",
        "description": "Create a new analysis rule",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_file": {
                    "type": "string",
                    "description": "Which rule file to add to (e.g., 'default_rules.yaml')",
                },
                "rule_definition": {
                    "type": "object",
                    "description": "Rule definition with id, name, severity, etc.",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for creating this rule",
                },
            },
            "required": ["rule_file", "rule_definition"],
        },
    },
    {
        "name": "get_audit_trail",
        "description": "Retrieve configuration change audit trail",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of entries to return (default: 50)",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_versions",
        "description": "List available configuration versions for rollback",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "rollback_config",
        "description": "Rollback configuration to a previous version",
        "inputSchema": {
            "type": "object",
            "properties": {
                "version_id": {
                    "type": "string",
                    "description": "Version ID to rollback to (format: YYYYMMDD_HHMMSS)",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for rollback",
                },
            },
            "required": ["version_id"],
        },
    },
    {
        "name": "reload_config",
        "description": "Reload configuration from disk (for manual YAML edits)",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# Tool Handlers
def get_config(section: str = None) -> dict[str, Any]:
    """Get configuration."""
    logger.info(f"Getting configuration: {section or 'full'}")

    try:
        config_mgr = get_config_manager()
        config = config_mgr.get_config(section)

        return {
            "status": "success",
            "section": section,
            "config": config,
        }

    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        return {"status": "error", "error": str(e)}


def get_rules(rule_file: str = None) -> dict[str, Any]:
    """Get rules."""
    logger.info(f"Getting rules: {rule_file or 'all'}")

    try:
        config_mgr = get_config_manager()
        rules = config_mgr.get_rules(rule_file)

        return {
            "status": "success",
            "rule_file": rule_file,
            "rules": rules,
        }

    except Exception as e:
        logger.error(f"Failed to get rules: {e}")
        return {"status": "error", "error": str(e)}


def validate_config(proposed_changes: dict[str, Any]) -> dict[str, Any]:
    """Validate configuration changes."""
    logger.info("Validating configuration changes")

    try:
        config_mgr = get_config_manager()
        is_valid, message = config_mgr.validate_config(proposed_changes)

        return {
            "status": "success",
            "is_valid": is_valid,
            "message": message,
            "changes": proposed_changes,
        }

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {"status": "error", "error": str(e)}


def update_config(
    changes: dict[str, Any], reason: str = None
) -> dict[str, Any]:
    """Update configuration."""
    logger.info(f"Updating configuration: {list(changes.keys())}")

    try:
        config_mgr = get_config_manager()
        success, message = config_mgr.update_config(
            changes=changes,
            user="claude",
            reason=reason,
        )

        return {
            "status": "success" if success else "error",
            "success": success,
            "message": message,
            "changes": changes if success else {},
        }

    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return {"status": "error", "error": str(e)}


def create_rule(
    rule_file: str,
    rule_definition: dict[str, Any],
    reason: str = None,
) -> dict[str, Any]:
    """Create a new rule."""
    logger.info(f"Creating rule: {rule_definition.get('id')}")

    try:
        config_mgr = get_config_manager()
        success, message = config_mgr.create_rule(
            rule_file=rule_file,
            rule_definition=rule_definition,
            user="claude",
            reason=reason,
        )

        return {
            "status": "success" if success else "error",
            "success": success,
            "message": message,
            "rule_id": rule_definition.get("id") if success else None,
        }

    except Exception as e:
        logger.error(f"Failed to create rule: {e}")
        return {"status": "error", "error": str(e)}


def get_audit_trail(limit: int = 50) -> dict[str, Any]:
    """Get audit trail."""
    logger.info(f"Getting audit trail (limit: {limit})")

    try:
        config_mgr = get_config_manager()
        entries = config_mgr.get_audit_trail(limit=limit)

        return {
            "status": "success",
            "entries": entries,
            "total": len(entries),
        }

    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        return {"status": "error", "error": str(e)}


def get_versions() -> dict[str, Any]:
    """Get available versions."""
    logger.info("Getting available versions")

    try:
        config_mgr = get_config_manager()
        versions = config_mgr.get_versions()

        return {
            "status": "success",
            "versions": versions,
            "total": len(versions),
        }

    except Exception as e:
        logger.error(f"Failed to get versions: {e}")
        return {"status": "error", "error": str(e)}


def rollback_config(version_id: str, reason: str = None) -> dict[str, Any]:
    """Rollback configuration."""
    logger.info(f"Rolling back to version: {version_id}")

    try:
        config_mgr = get_config_manager()
        success, message = config_mgr.rollback_config(
            version_id=version_id,
            user="claude",
            reason=reason,
        )

        return {
            "status": "success" if success else "error",
            "success": success,
            "message": message,
            "version_id": version_id if success else None,
        }

    except Exception as e:
        logger.error(f"Failed to rollback config: {e}")
        return {"status": "error", "error": str(e)}


def reload_config() -> dict[str, Any]:
    """Reload configuration from disk."""
    logger.info("Reloading configuration from disk")

    try:
        config_mgr = get_config_manager()
        success, message = config_mgr.reload_from_disk(user="claude")

        return {
            "status": "success" if success else "error",
            "success": success,
            "message": message,
        }

    except Exception as e:
        logger.error(f"Failed to reload config: {e}")
        return {"status": "error", "error": str(e)}


# Tool dispatcher
CONFIG_TOOL_HANDLERS = {
    "get_config": get_config,
    "get_rules": get_rules,
    "validate_config": validate_config,
    "update_config": update_config,
    "create_rule": create_rule,
    "get_audit_trail": get_audit_trail,
    "get_versions": get_versions,
    "rollback_config": rollback_config,
    "reload_config": reload_config,
}


def handle_config_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Handle a config tool call and return JSON result."""
    logger.info(f"Handling config tool: {tool_name}")

    if tool_name not in CONFIG_TOOL_HANDLERS:
        return json.dumps(
            {"status": "error", "error": f"Unknown tool: {tool_name}"}
        )

    try:
        handler = CONFIG_TOOL_HANDLERS[tool_name]
        result = handler(**tool_input)
        return json.dumps(result)

    except Exception as e:
        logger.error(f"Config tool handler error: {e}")
        return json.dumps({"status": "error", "error": str(e)})
