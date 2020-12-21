from functools import wraps

from flatbread.config import CONFIG
from flatbread.axes import get_axis_number


def set_value(key, value=None):
    if value is None:
        return CONFIG.aggregation[key]
    return value
