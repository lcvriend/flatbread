import json
import locale
from functools import wraps
from typing import Any, Dict, List, Callable, TypeVar
from pathlib import Path


F = TypeVar('F', bound=Callable[..., Any])


HERE = Path(__file__).resolve().parent


class Config:
    """Config
    ======
    Object for loading and storing settings.

    Loads 'config.json' if it exists or else 'config.defaults.json' from library
    folder. Sections are accessed by dot notation.

    Methods
    -------
    save :
        Save settings.
    defaults :
        Load default settings (without overwriting any stored saved settings).
    factory_reset :
        Restore default settings (overwrite any stored saved settings).
    get_path : str
        Return item in `paths` as Path object.
    set_locale : str
        Set locale if one was provided in 'format' section under ['locale'].

    Constructors
    ------------
    from_json :
        Construct config object from json file.
    """

    configfile = HERE / 'config.json'

    def __init__(self, settings):
        self.__dict__ = settings
        self.set_locale()

    def __getitem__(self, key):
        return self.__dict__[key]

    def save(self):
        "Save settings permanently."
        with open(HERE / 'config.json', 'w', encoding='utf8') as f:
            json.dump(self.__dict__, f, indent=4)

    def defaults(self):
        "Set settings to defaults."
        self.configfile = HERE / 'config.defaults.json'
        self.__dict__ = self.load(self.configfile)

    def factory_reset(self):
        "Reset settings (deletes saved settings too)."
        if not self.configfile.suffixes[0] == '.defaults':
            self.configfile.unlink(missing_ok=True)
            self.defaults()

    @property
    def basepath(self):
        if self.general['store_output_in_cwd']:
            return Path()
        return HERE

    def get_path(self, key):
        "Get path from `paths` relative to `basepath` as Path object."
        return self.basepath / self.paths[key]

    def set_locale(self):
        "Set locale if one was provided."
        if self.format['locale']:
            locale.setlocale(locale.LC_ALL, self.format['locale'])

    @staticmethod
    def load(configfile):
        "Load json file."
        with open(configfile, 'r', encoding='utf8') as f:
            return json.load(f)

    @classmethod
    def from_json(cls):
        """Construct class from 'config.json', defaults to
        'config.defaults.json' if it does not exist."""
        if not cls.configfile.exists():
            cls.configfile = HERE / 'config.defaults.json'
        settings = cls.load(cls.configfile)
        return cls(settings)


CONFIG = Config.from_json()


def get_value(
    section: str,
    key: str,
    value: Any = None,
) -> Any:
    "If `value` is None, load value from CONFIG."
    if value is None:
        return CONFIG[section][key]
    return value


def load_settings(
    settings_to_load: Dict[str, List[str]]
) -> Callable[[F], F]:
    """Decorate function with a settings loader.
    If argument in is None, then value
    will be loaded from CONFIG.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            settings = {
                key:get_value(section, key, kwargs.get(key))
                for section, keys in settings_to_load.items()
                for key in keys
            }
            kwargs.update(settings)
            return func(*args, **kwargs)
        return wrapper
    return decorator
