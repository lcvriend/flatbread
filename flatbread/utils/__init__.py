"""
General utility functions.

:py:mod:`flatbread.utils.log`
"""

from functools import wraps
from pandas._libs.lib import is_scalar


def copy(func):
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        df = df.copy()
        result = func(df, *args, **kwargs)
        return result
    return wrapper


def listify(x):
    if x is None:
        return []
    return [x] if is_scalar(x) else list(x)
