"""
Helper functions for dealing with DataFrame levels.
"""

from decimal import Decimal
from functools import wraps
from typing import Any, List, Callable, TypeVar, Tuple, Sequence, cast

import pandas as pd # type: ignore

import flatbread.config as config
import flatbread.utils as utils
from flatbread.aggregate import AGG_SETTINGS


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
    """
    Decorator that transposes df if `axis` == 1, then operates on it and transposes it back. Consumes the `axis` kwarg.
    """
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
    new_index = pd.MultiIndex.from_tuples(cols).rename(names)
    df.index = new_index
    return df


def add_item_to_key(
    key:   Any,
    item:  Any,
    level: int = 0,
) -> Tuple[Any, ...]:
    "Insert `item` into `key` at a specified `level`."
    key = utils.listify(key)
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
    key = utils.listify(key)
    key[level] = item
    return tuple(key)


def check_idx_for_key(index: pd.Index, key: Any) -> bool:
    "Check if key is in index"
    if isinstance(index, pd.MultiIndex):
        return any(key in i for i in index)
    else:
        return any(key == i for i in index)


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
            cats = [item for item in cats if item not in index.categories]
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


@config.load_settings(AGG_SETTINGS)
@transpose
def reindex_na(
    df,
    na_rep: Any = None,
    na_position: str = None,
    **kwargs
):
    for i in range(df.index.nlevels):
        ordered_labels = _get_ordered_labels(df.index, i, na_rep, na_position)
        kwds = {}
        if isinstance(df.index, pd.MultiIndex):
            kwds = dict(level=i)
        df = df.reindex(ordered_labels, **kwds)
    return df


def _get_ordered_labels(
    axis,
    level,
    na_rep,
    na_position,
):
    def move_na(labels):
        if na_rep in labels:
            idx_of_na_rep = labels.index(na_rep)
            labels.pop(idx_of_na_rep)
            if na_position == 'first':
                labels.insert(0, na_rep)
            else:
                labels.append(na_rep)
        return labels

    if isinstance(axis, pd.CategoricalIndex):
        if na_rep in axis.categories:
            labels = move_na(list(axis.categories))
            axis = axis.reorder_categories(labels)
        return pd.CategoricalIndex(
            data=axis.get_level_values(level),
            categories=axis.categories,
            ordered=axis.ordered,
            name=axis.name
        )
    else:
        labels = list(dict.fromkeys(axis.get_level_values(level)))
        labels = move_na(labels)
        return pd.Index(labels, name=axis.name)


@config.load_settings(AGG_SETTINGS)
@transpose
def drop_na(df, na_rep=None, **kwargs):
    index = _drop_na(df.index, na_rep)
    df = df.reindex(index).rename_axis(index.names)
    return df


def _drop_na(axis, na_rep):
    if isinstance(axis, pd.MultiIndex):
        for level in range(axis.nlevels):
            axis = axis.drop(na_rep, level=level, errors='ignore')
    else:
        axis = axis.drop(na_rep, errors='ignore')
    return axis
