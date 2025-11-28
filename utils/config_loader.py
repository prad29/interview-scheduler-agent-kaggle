"""
Configuration Loader

Utilities for loading and managing application configuration.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def load_config(
    config_path: Optional[str] = None,
    config_type: str = 'auto'
) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Supports JSON, YAML, and Python files.
    
    Args:
        config_path: Path to configuration file
        config_type: Type of config file ('json', 'yaml', 'py', or 'auto')
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config type is unsupported
    """
    if config_path is None:
        # Try to find config in common locations
        common_paths = [
            'config.json',
            'config.yaml',
            'config.yml',
            'config.py',
            'config/config.json',
            'config/config.yaml'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        if config_path is None:
            raise FileNotFoundError(
                "No configuration file found. Please provide config_path or "
                "create config.json, config.yaml, or config.py"
            )
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Auto-detect config type from extension
    if config_type == 'auto':
        extension = config_file.suffix.lower()
        
        if extension == '.json':
            config_type = 'json'
        elif extension in ['.yaml', '.yml']:
            config_type = 'yaml'
        elif extension == '.py':
            config_type = 'py'
        else:
            raise ValueError(f"Cannot auto-detect config type from extension: {extension}")
    
    logger.info(f"Loading configuration from {config_path} (type: {config_type})")
    
    # Load based on type
    if config_type == 'json':
        return load_json_config(config_path)
    elif config_type == 'yaml':
        return load_yaml_config(config_path)
    elif config_type == 'py':
        return load_python_config(config_path)
    else:
        raise ValueError(f"Unsupported config type: {config_type}")


def load_json_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Loaded JSON configuration: {len(config)} keys")
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading JSON config: {str(e)}")
        raise


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Configuration dictionary
    """
    try:
        import yaml
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded YAML configuration: {len(config)} keys")
        return config
        
    except ImportError:
        raise ImportError(
            "PyYAML is required to load YAML configs. "
            "Install it with: pip install pyyaml"
        )
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading YAML config: {str(e)}")
        raise


def load_python_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from Python file
    
    Args:
        config_path: Path to Python config file
        
    Returns:
        Configuration dictionary
    """
    try:
        import importlib.util
        
        # Load module from file
        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Extract configuration variables (uppercase only)
        config = {}
        for key in dir(config_module):
            if key.isupper():
                config[key] = getattr(config_module, key)
        
        logger.info(f"Loaded Python configuration: {len(config)} keys")
        return config
        
    except Exception as e:
        logger.error(f"Error loading Python config: {str(e)}")
        raise


def get_config_value(
    config: Dict[str, Any],
    key: str,
    default: Any = None,
    required: bool = False
) -> Any:
    """
    Get configuration value with optional default and validation
    
    Supports nested keys with dot notation (e.g., 'database.host')
    
    Args:
        config: Configuration dictionary
        key: Configuration key (supports dot notation for nested keys)
        default: Default value if key not found
        required: Whether the key is required (raises error if missing)
        
    Returns:
        Configuration value
        
    Raises:
        KeyError: If required key is missing
    """
    # Handle nested keys
    if '.' in key:
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                if required:
                    raise KeyError(f"Required configuration key not found: {key}")
                return default
        
        return value
    else:
        # Simple key
        if key in config:
            return config[key]
        elif required:
            raise KeyError(f"Required configuration key not found: {key}")
        else:
            return default


def validate_config(
    config: Dict[str, Any],
    required_keys: list,
    optional_keys: Optional[list] = None
) -> tuple[bool, list]:
    """
    Validate configuration has required keys
    
    Args:
        config: Configuration dictionary
        required_keys: List of required configuration keys
        optional_keys: List of optional keys (for documentation)
        
    Returns:
        Tuple of (is_valid, list of missing keys)
    """
    missing_keys = []
    
    for key in required_keys:
        # Support nested keys
        if '.' in key:
            keys = key.split('.')
            value = config
            found = True
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    found = False
                    break
            
            if not found:
                missing_keys.append(key)
        else:
            if key not in config:
                missing_keys.append(key)
    
    is_valid = len(missing_keys) == 0
    
    if not is_valid:
        logger.warning(f"Configuration validation failed. Missing keys: {missing_keys}")
    else:
        logger.info("Configuration validation passed")
    
    return is_valid, missing_keys


def merge_configs(
    *configs: Dict[str, Any],
    deep_merge: bool = True
) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries
    
    Later configs override earlier ones.
    
    Args:
        *configs: Configuration dictionaries to merge
        deep_merge: Whether to deeply merge nested dictionaries
        
    Returns:
        Merged configuration dictionary
    """
    if not configs:
        return {}
    
    if len(configs) == 1:
        return configs[0].copy()
    
    result = configs[0].copy()
    
    for config in configs[1:]:
        if deep_merge:
            result = _deep_merge(result, config)
        else:
            result.update(config)
    
    return result


def _deep_merge(dict1: dict, dict2: dict) -> dict:
    """
    Deep merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def save_config(
    config: Dict[str, Any],
    config_path: str,
    config_type: str = 'json',
    indent: int = 2
):
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
        config_type: Type of config file ('json' or 'yaml')
        indent: Indentation level for formatting
    """
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    if config_type == 'json':
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=indent)
        logger.info(f"Saved JSON configuration to {config_path}")
        
    elif config_type == 'yaml':
        try:
            import yaml
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=indent)
            logger.info(f"Saved YAML configuration to {config_path}")
            
        except ImportError:
            raise ImportError("PyYAML is required to save YAML configs")
    else:
        raise ValueError(f"Unsupported config type for saving: {config_type}")


def get_env_config(prefix: str = 'APP_') -> Dict[str, Any]:
    """
    Load configuration from environment variables
    
    Args:
        prefix: Prefix for environment variables (e.g., 'APP_')
        
    Returns:
        Configuration dictionary from environment variables
    """
    config = {}
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to lowercase
            config_key = key[len(prefix):].lower()
            
            # Try to parse value as JSON (for complex types)
            try:
                config[config_key] = json.loads(value)
            except json.JSONDecodeError:
                # Keep as string if not valid JSON
                config[config_key] = value
    
    logger.info(f"Loaded {len(config)} configuration values from environment")
    return config