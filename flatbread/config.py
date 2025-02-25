import functools
import json
from pathlib import Path
from typing import Callable


def deep_merge(base: dict, update: dict) -> dict:
    """
    Deep merge two dictionaries, preserving structure from both.

    - When both dicts have a dict at the same key, merge recursively
    - When update has keys not in base, add them
    - When types mismatch (e.g., dict in one, value in other), prefer update

    Parameters
    ----------
    base : dict
        Base dictionary to merge into
    update : dict
        Dictionary with values to update base with

    Returns
    -------
    dict
        Merged dictionary
    """
    merged = base.copy()
    for key, update_val in update.items():
        if key not in merged:
            # Add keys from update that don't exist in base
            merged[key] = update_val
        elif isinstance(update_val, dict) and isinstance(merged[key], dict):
            # Recursively merge nested dictionaries
            merged[key] = deep_merge(merged[key], update_val)
        else:
            # Override base value with update value
            merged[key] = update_val
    return merged


def find_project_config(max_levels: int = 5) -> Path|None:
    """
    Find project-level .flatbread.json, traversing up from current directory.

    Parameters
    ----------
    max_levels : int, default 5
        Maximum number of directory levels to traverse upward

    Returns
    -------
    Path or None
        Path to the config file if found, None otherwise
    """
    current_dir = Path.cwd()
    home_dir = Path.home()

    # Check current directory and up to max_levels parent directories
    for _ in range(max_levels + 1):
        config_path = current_dir / ".flatbread.json"
        if config_path.is_file():
            return config_path

        # Stop if we've reached the filesystem root or home directory
        if current_dir == current_dir.parent or current_dir == home_dir:
            break

        # Move up one directory
        current_dir = current_dir.parent

    return None


def read_config():
    """
    Read configuration with priority: project > user > defaults.

    Returns
    -------
    dict
        Merged configuration dictionary
    """
    # 1. Look for project config first
    project_config = None
    if project_path := find_project_config():
        project_config = json.loads(project_path.read_text())

    # 2. Look for user config
    user_config = None
    user_config_path = Path('~/.flatbread.json').expanduser()
    if user_config_path.exists():
        user_config = json.loads(user_config_path.read_text())

    # 3. Get default config
    package_path = Path(__file__).resolve().parent
    config = json.loads((package_path / 'config/config.defaults.json').read_text())

    # Merge configs with right precedence
    if user_config:
        config = deep_merge(config, user_config)
    if project_config:
        config = deep_merge(config, project_config)

    return config


def inject_defaults(defaults: dict) -> Callable:
    """
    Load defaults if keywords are None or undefined when calling a function.

    Arguments
    ---------
    defaults (dict):
        Dictionary of keywords and default values.

    Return
    ------
    func:
        Function that will load defaults.

    Notes
    -----
    This decorator will override any default values set in the function definition.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for key, val in defaults.items():
                if kwargs.get(key) is None:
                    kwargs[key] = val
            return func(*args, **kwargs)
        return wrapper
    return decorator
