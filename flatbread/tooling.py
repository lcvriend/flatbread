from functools import singledispatch
from typing import Any, Literal, TypeAlias

import pandas as pd

from flatbread import DEFAULTS


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


def offset_date_field(
    df: pd.DataFrame,
    date_field: str,
    year_field: str,
) -> pd.DataFrame:
    offset_year = df[year_field].max()

    def shift_dates(group):
        offset = pd.DateOffset(years = offset_year - group.name)
        return group.shift(freq = offset)

    return (
        df
        .set_index(date_field, drop=False)
        .groupby(year_field, group_keys=False)
        .apply(shift_dates)
        .rename_axis(date_field + '_offs')
        .reset_index()
    )


def _sort_index_from_list(
    df: pd.DataFrame,
    order: list|pd.CategoricalDtype,
    axis: Axis = 0,
    level: int|str|None = None,
) -> pd.DataFrame:
    index = df.index if axis in [0, 'index'] else df.columns
    if isinstance(index, pd.MultiIndex):
        index = index.levels[level]
    order = [i for i in order if i in index]
    return df.reindex(order, axis=axis, level=level)


def sort_index_from_list(
    data: pd.DataFrame|pd.Series,
    order: list,
    axis: Axis = 0,
    level: int|str|None = None,
) -> pd.DataFrame|pd.Series:
    sorter = lambda idx: idx.map({n:m for m,n in enumerate(order)})
    return data.sort_index(axis=axis, level=level, key=sorter)


def sort_totals(
    data: pd.DataFrame|pd.Series,
    axis: Axis = 0,
    level: int = 0,
    **kwargs,
):
    """
    Sort an index alphabetically except for special labels which should come last.
    """
    def safe_index(lst: list, value: str, default: int = -1) -> int:
        index_map = {v:i for i,v in enumerate(lst)}
        return index_map.get(value, default)

    def assign_order(i) -> tuple[int, Any]:
        return safe_index(labels, i), i

    labels = [
        DEFAULTS['subtotals']['label'],
        DEFAULTS['totals']['label'],
    ]

    output = data.sort_index(
        axis = axis,
        level = level,
        key = lambda idx: idx.map(assign_order),
        **kwargs,
    )
    return output


@singledispatch
def add_level(
    data,
    item: Any,
    level: int = 0,
    level_name: Any = None,
    axis: Axis = 0,
):
    raise NotImplementedError('No implementation for this type')


@add_level.register
def _(
    data: pd.DataFrame,
    value: Any,
    level: int = 0,
    level_name: Any = None,
    axis: Axis = 0,
) -> pd.DataFrame:
    """
    Add a level containing the specified value to a DataFrame axis.

    Parameters
    ----------
    data (pd.DataFrame):
        Input DataFrame.
    value (Any):
        Value to fill the new level with.
    level (int, optional):
        Position to insert the new level. Defaults to 0 (start).
    level_name (Any, optional):
        Name for the new level. Defaults to None.
    axis (Axis):
        Axis to modify (0 for index, 1 for columns). Defaults to 0.

    Returns
    -------
    pd.DataFrame:
        DataFrame with the new level added to the specified axis.
    """
    data = data.copy()
    target = data.index if axis in [0, 'index'] else data.columns

    if not isinstance(target, pd.MultiIndex):
        original_name = target.name
        target = pd.MultiIndex.from_arrays([target], names=[original_name])

    new_keys = [add_value_to_key(key, value, level) for key in target]
    new_names = add_value_to_key(target.names, level_name, level)
    new_index = pd.MultiIndex.from_tuples(new_keys, names=new_names)

    if axis in [0, 'index']:
        data.index = new_index
    else:
        data.columns = new_index
    return data


@add_level.register
def _(
    data: pd.Series,
    value: Any,
    level: int = 0,
    level_name: Any = None,
    axis: Axis = 0,
) -> pd.DataFrame:
    """
    Add a level containing the specified value to a Series index.

    Parameters
    ----------
    data (pd.Series):
        Input Series.
    value (Any):
        Value to fill the new level with.
    level (int, optional):
        Position to insert the new level. Defaults to 0 (start).
    level_name (Any, optional):
        Name for the new level. Defaults to None.
    axis (Axis):
        Added for symmetry with DataFrame method.

    Returns
    -------
    pd.Series:
        Series with the new level added to the specified axis.
    """
    data = data.copy()
    target = data.index

    if not isinstance(target, pd.MultiIndex):
        original_name = target.name
        target = pd.MultiIndex.from_arrays([target], names=[original_name])

    new_keys = [add_value_to_key(key, value, level) for key in target]
    new_names = add_value_to_key(target.names, level_name, level)
    new_index = pd.MultiIndex.from_tuples(new_keys, names=new_names)
    data.index = new_index
    return data


def add_value_to_key(
    key: Any|tuple[Any, ...],
    value: Any,
    level: int = 0,
) -> tuple[Any, ...]:
    """
    Insert an value into a key (tuple or single value refering to a column position) at a specified level.

    Parameters
    ----------
    key (Any|tuple[Any, ...]):
        Original key.
    value (Any):
        Item to insert into the key.
    level (int, optional):
        Position to insert the value. Defaults to 0.

    Returns
    -------
    Tuple[Any, ...]:
        New key with the value inserted.
    """
    key = list(key) if isinstance(key, (tuple, list)) else [key]
    if level >= 0:
        key.insert(level, value)
    elif level == -1:
        key.append(value)
    else:
        key.insert(level + 1, value)
    return tuple(key)
