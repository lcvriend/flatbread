from decimal import Decimal
from functools import wraps
from typing import Any, List, Callable, TypeVar, Tuple, Sequence, cast

import pandas as pd # type: ignore

import flatbread.utils as utils


F = TypeVar('F', bound=Callable[..., Any])

AXES_ALIAS = {
    0: 0,
    1: 1,
    2: 2,
    'idx': 0,
    'index': 0,
    'rows': 0,
    'columns': 1,
    'cols': 1,
    'both': 2,
    'all': 2,
}


def transpose(func):
    """Decorator that transposes df if `axis` == 1, then operates on it and transposes it back. Consumes the `axis` kwarg."""

    @wraps(func)
    def wrapper(df, *args, **kwargs):
        axis = kwargs.pop('axis', 0)
        df = df.T if axis == 1 else df
        result = func(df, *args, **kwargs)
        return result.T if axis == 1 else result
    if func.__doc__ is not None:
        wrapper.__doc__ = f"Operate on `axis`. {func.__doc__}"
    return wrapper


def get_axis_number(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):
        axis = kwargs.get('axis') or 0
        kwargs['axis'] = _get_axis_number(axis)
        return func(*args, **kwargs)
    return cast(F, wrapper)


def _get_axis_number(axis: Any) -> int:
    assert (axis in AXES_ALIAS), f"Axis should be one of {AXES_ALIAS.keys()}"
    return AXES_ALIAS[axis]


@utils.copy
@transpose
def add_axis_level(
    df:         pd.DataFrame,
    item:       Any,
    level:      int = -1,
    level_name: Any = None,
) -> pd.DataFrame:
    "Add `level` with `level_name` to axis in `df`."

    cols = (add_item_to_key(key, item, level) for key in df.index)
    names = add_item_to_key(df.index.names, level_name, level)
    df.index = pd.MultiIndex.from_tuples(cols).rename(names)
    return df


def add_item_to_key(
    key:   Any,
    item:  Any,
    level: int = 0,
) -> Tuple[Any, ...]:
    "Insert `item` into `key` at a specified `level`."

    key = key_to_list(key)
    if level < 0:
        key.append(item)
    else:
        key.insert(level, item)
    return tuple(key)


def replace_item_in_key(
    key:   Any,
    item:  Any,
    level: int = 0,
) -> Tuple[Any, ...]:
    "Replace item in `key` at `level` with `item`."

    key = key_to_list(key)
    key[level] = item
    return tuple(key)


def key_to_list(key: Any) -> List[Any]:
    "Convert `key` to list."

    if isinstance(key, (str, int, float, Decimal)):
        return [key]
    else:
        return list(key)


def order_categories(
    s:          pd.Series,
    categories: Sequence,
) -> pd.Series:
    "Order `categories` in series `s`."

    return pd.Categorical(s, categories, ordered=True)


def add_category(
    index:    pd.Index,
    category: Any,
    level:    int = 0
) -> pd.Index:
    "Add `category` to categorical `index` at specified `level`."

    def add_cat(index, cats):
        if isinstance(index, pd.CategoricalIndex):
            cats = [item for item in cats if item not in list(index.categories)]
            index = index.add_categories(cats)
        return index

    if isinstance(category, str):
        category = [category]

    if isinstance(index, pd.MultiIndex):
        index = index.set_levels(
            add_cat(index.levels[level], category),
            level=level)
    else:
        index = add_cat(index, category)
    return index
