"""Constants for data-viewer formatting"""
from flatbread import DEFAULTS


SMART_FORMATS = {
    'percentages': {
        'labels': [DEFAULTS['percentages']['label_pct']],
        'options': {
            'style': 'percent',
            'minimumFractionDigits': 0,
            'maximumFractionDigits':
                DEFAULTS['percentages']['ndigits'] if DEFAULTS['percentages']['ndigits'] >= 0 else 21,
        }
    },
    'difference': {
        'labels': ['diff'],
        'options': {
            'signDisplay': 'always',
        }
    }
}

DEFAULT_DTYPES: dict[str, str] = {
    'object':         'str',
    'string':         'str',
    'bool':           'bool',
    'boolean':        'bool',
    'category':       'category',
    'datetime64[ns]': 'datetime',
    'float64':        'float',
    'Float64':        'float',
    'int8':           'int',
    'int16':          'int',
    'int32':          'int',
    'int64':          'int',
    'Int8':           'int',
    'Int16':          'int',
    'Int32':          'int',
    'Int64':          'int',
}

NUMBER_PRESETS = {"default", "currency", "percentage", "compact", "diffs"}
DATE_PRESETS = {"default", "date", "datetime"}

DTYPE_TO_PRESETS = {
    "float": NUMBER_PRESETS,
    "int": NUMBER_PRESETS,
    "datetime": DATE_PRESETS
}
