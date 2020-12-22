from decimal import Decimal
from functools import wraps
from typing import Any, List, Tuple, Sequence

import pandas as pd

from flatbread.types import AxisAlias, LevelAlias
from flatbread.utils import copy


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
    @wraps(func)
    def wrapper(df, **kwargs):
        axis = kwargs.pop('axis', 0)
        df = df.T if axis == 1 else df
        result = func(df, **kwargs)
        return result.T if axis == 1 else result
    if func.__doc__ is not None:
        wrapper.__doc__ = f"Operate on `axis`. {func.__doc__}"
    return wrapper


def get_axis_number(axis: AxisAlias) -> int:
    assert (axis in AXES_ALIAS), f"Axis should be one of {AXES_ALIAS.keys()}"
    return AXES_ALIAS[axis]


@copy
@transpose
def add_axis_level(
    df:         pd.DataFrame,
    item:       Any,
    level:      LevelAlias = -1,
    level_name: Any        = None,
) -> pd.DataFrame:
    "Add `level` with `level_name` to axis in `df`."

    cols = (add_item_to_key(key, item, level) for key in df.index)
    names = add_item_to_key(df.index.names, level_name, level)
    df.index = pd.MultiIndex.from_tuples(cols).rename(names)
    return df


def add_item_to_key(
    key:   Any,
    item:  Any,
    level: LevelAlias = 0,
) -> Tuple[Any]:
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
    level: LevelAlias = 0,
) -> Tuple[Any]:
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
    category: str,
    level:    LevelAlias = 0
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
