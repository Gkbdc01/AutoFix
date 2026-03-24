"""Configuration management — reads .autofixconfig.json from workspace."""

import json
import logging
import os
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "enabled": True,
    "severity": {
        "syntax": "error",
        "logic": "error",
        "performance": "warning",
        "security": "error",
    },
    "ignoreRules": [],
    "debounceMs": 500,
    "maxErrors": 5,  # Show up to 5 errors per file
}

_cached_config: Optional[Dict] = None
_config_file_path: Optional[str] = None


def load_config(workspace_root: Optional[str] = None) -> Dict:
    """Load configuration from .autofixconfig.json in workspace root."""
    global _cached_config, _config_file_path
    
    if _cached_config is not None:
        return _cached_config
    
    config_path = ".autofixconfig.json"
    if workspace_root:
        config_path = os.path.join(workspace_root, config_path)
    
    _config_file_path = config_path
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            _cached_config = {**DEFAULT_CONFIG, **user_config}
            logger.info("Loaded config from %s", config_path)
            return _cached_config
        except Exception as e:
            logger.warning("Failed to load config from %s: %s. Using defaults.", config_path, e)
    
    _cached_config = DEFAULT_CONFIG.copy()
    return _cached_config


def get_config() -> Dict:
    """Get the current configuration (loads if not already loaded)."""
    if _cached_config is None:
        load_config()
    return _cached_config


def get_severity(error_type: str) -> str:
    """Get the severity level for an error type."""
    config = get_config()
    return config.get("severity", {}).get(error_type, "error")


def is_rule_ignored(rule: str) -> bool:
    """Check if a rule is in the ignore list."""
    config = get_config()
    return rule in config.get("ignoreRules", [])


def get_max_errors() -> int:
    """Get maximum errors to report per file."""
    config = get_config()
    return config.get("maxErrors", 5)


def reload_config() -> None:
    """Force reload configuration from disk."""
    global _cached_config
    _cached_config = None
    load_config()
