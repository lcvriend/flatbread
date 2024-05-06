import functools
import json
from pathlib import Path
from typing import Callable


def read_config():
    config_path = Path('~/.flatbread/config.json').expanduser()
    if not config_path.exists():
        package_path = Path(__file__).resolve().parent
        config_path = package_path / 'config/config.defaults.json'
    json_string = config_path.read_text()
    config = json.loads(json_string)
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
