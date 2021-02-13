import json
import locale
from functools import wraps
from typing import Any, Dict, List, Callable, TypeVar, Union
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

    @property
    def sections(self):
        return list(self.__dict__.keys())

    def save(self, path=None):
        "Save settings permanently. Optionally supply path."
        if not path:
            path = self.configfile
        with open(path, 'w', encoding='utf8') as f:
            json.dump(self.__dict__, f, indent=4)

    def reload(self):
        "Reload json file."
        with open(self.configfile, 'r', encoding='utf8') as f:
            self.__dict__ = json.load(f)

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

    @classmethod
    def from_json(cls):
        """Construct class from 'config.json', defaults to
        'config.defaults.json' if it does not exist."""
        if not cls.configfile.exists():
            cls.configfile = HERE / 'config.defaults.json'
        settings = cls.load(cls.configfile)
        return cls(settings)

    @staticmethod
    def load(configfile):
        "Load json file."
        with open(configfile, 'r', encoding='utf8') as f:
            return json.load(f)


CONFIG = Config.from_json()


def get_value(
    settings: Dict,
    key: str,
    value: Any = None,
) -> Any:
    "If `value` is None, load value from CONFIG."
    if value is None:
        return settings[key]
    return value


def load_settings(
    settings_to_load: Union[str, List[str], Dict[str, List[str]]]
) -> Callable[[F], F]:
    """Decorate function with a settings loader.
    If argument is None, then value will be loaded from CONFIG.
    Can load one or more sections or load specific settings from multiple
    settings.

    Arguments
    ---------
    settings_to_load : str, list of str, dict of list of str
        str:
            String refers to name of section to be loaded.
        list of str:
            Strings refer to names of sections to be loaded.
        dict of list of str:
            Keys refer to the names of the sections to be loaded,
            strings in list refer to the settings to be loaded from section.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(settings_to_load, str):
                "print! this is a string"
                section = CONFIG[settings_to_load]
                settings = {
                    key:get_value(section, key, kwargs.get(key))
                    for key in section
                }
            elif isinstance(settings_to_load, list):
                settings = {
                    key:get_value(CONFIG[section], key, kwargs.get(key))
                    for section in settings_to_load
                    for key in CONFIG[section]
                }
            else:
                settings = {
                    key:get_value(CONFIG[section], key, kwargs.get(key))
                    for section, keys in settings_to_load.items()
                    for key in keys
                }
            kwargs.update(settings)
            return func(*args, **kwargs)
        return wrapper
    return decorator
