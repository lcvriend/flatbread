import json
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent


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

    Constructors
    ------------
    from_json :
        Construct config object from json file.
    """

    configfile = HERE / 'config.json'

    def __init__(self, settings):
        self.__dict__ = settings

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
