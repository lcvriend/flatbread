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


def get_label_indeces(index, label, level=None):
    """
    Return indeces of the ``index`` containing ``label``.
    If ``level`` is given, then only that specific level within the index will
    be tested for the label.
    """
    is_tuple = lambda x: isinstance(x, tuple)
    has_label = lambda x, lbl: lbl in x if is_tuple(x) else lbl == x
    if level is None:
        return [i for i, key in enumerate(index) if has_label(key, label)]

    level = index.get_level_values(level)
    mask = [i == 0 or x != level[i-1] for i, x in enumerate(level)]
    return [i for i, x in enumerate(level) if has_label(x, label) and mask[i]]
