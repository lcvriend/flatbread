from functools import singledispatch
from typing import Callable, Literal, TypeAlias

import pandas as pd

from flatbread import chaining


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


def get_label(label, aggfunc):
    if label is not None:
        return label
    if isinstance(aggfunc, str):
        return aggfunc
    if hasattr(aggfunc, '__name__') and aggfunc.__name__ != '<lambda>':
        return aggfunc.__name__
    return 'aggregation'


def get_levels(levels, names):
    find_level = lambda lvl: lvl if isinstance(lvl, int) else names.index(lvl)
    if isinstance(levels, (int, str)):
        return [find_level(levels)]
    return [find_level(level) for level in levels]


# AGGREGATION

@singledispatch
def add_agg(
    data,
    *args,
    aggfunc: str|Callable,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill: str|None = '',
    **kwargs,
):
    raise NotImplementedError('No implementation for this type')


## SERIES
@add_agg.register
def _(
    s: pd.Series,
    aggfunc: str|Callable,
    *args,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill: str|None = '',
    **kwargs,
) -> pd.Series:
    data = s.copy()

    label = get_label(label, aggfunc)
    rows = chaining.get_data_mask(data.index, ignore_keys)

    padding = [_fill] * (data.index.nlevels - 1)
    key = tuple([label, *padding]) if padding else label
    data.loc[key] = data.loc[rows].agg(aggfunc, *args, **kwargs)
    return data


## DATAFRAME
@add_agg.register
def _(
    df: pd.DataFrame,
    aggfunc: str|Callable,
    *args,
    axis: int = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill: str|None = '',
    **kwargs,
) -> pd.DataFrame:
    data = df.copy() if axis == 0 else df.copy().T

    label = get_label(label, aggfunc)
    rows = chaining.get_data_mask(data.index, ignore_keys)

    # create key
    padding = [_fill] * (data.index.nlevels - 1)
    key = tuple([label, *padding]) if padding else label

    data.loc[key, :] = data.loc[rows].agg(aggfunc, *args, **kwargs)

    if axis == 1:
        data = data.T
    return data


# SUBAGGREGATION

@singledispatch
def add_subagg(
    data,
    aggfunc: str|Callable,
    *args,
    levels: int|str|list[int|str] = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    **kwargs,
):
    raise NotImplementedError('No implementation for this type')


## SERIES
@add_subagg.register
def _(
    s: pd.Series,
    aggfunc: str|Callable,
    *args,
    levels: int|str|list[int|str] = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill = '',
    **kwargs,
):
    data = s.copy()
    output = _subagg_implementation(
        data,
        aggfunc,
        *args,
        levels = levels,
        label = label,
        ignore_keys = ignore_keys,
        _fill = _fill,
        **kwargs,
    )
    return output


## DATAFRAME
@add_subagg.register
def _(
    df: pd.DataFrame,
    aggfunc: str|Callable,
    *args,
    axis: int = 0,
    levels: int|str|list[int|str] = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill = '',
    **kwargs,
):
    data = df.copy() if axis == 0 else df.copy().T
    output = _subagg_implementation(
        data,
        aggfunc,
        *args,
        levels = levels,
        label = label,
        ignore_keys = ignore_keys,
        _fill = _fill,
        **kwargs,
    )
    if axis == 1:
        output = output.T
    return output


def _subagg_implementation(
    data: pd.Series|pd.DataFrame,
    aggfunc: str|Callable,
    *args,
    levels: int|str|list[int|str] = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill = '',
    **kwargs,
):
    names = data.index.names
    label = get_label(label, aggfunc)
    levels = get_levels(levels, names)

    # checks
    msg = 'Flatbread cannot perform subaggregation if axis is not MultiIndex'
    assert isinstance(data.index, pd.MultiIndex), msg
    nlevels = data.index.nlevels
    for level in levels:
        assert level < nlevels - 1, f'Level must be smaller than {nlevels - 1}'

    def process_groups(groups):
        processed = []
        for levels, group in groups:
            # create key
            levels = (levels,) if pd.api.types.is_scalar(levels) else levels
            padding = [_fill] * (len(names) - len(levels) - 1)
            key = list(levels) + [label] + padding

            # ignore totals and subtotal rows when aggregating
            rows = chaining.get_data_mask(group.index, ignore_keys)

            # if no data rows were selected, then do not add subagg
            # this makes sure that for example a subtotal is added
            # to a totals row
            if rows.any():
                group.loc[tuple(key)] = (
                    group
                    .loc[rows]
                    .agg(aggfunc, *args, **kwargs)
                )
            processed.append(group)
        return pd.concat(processed)

    output = data
    for level in sorted(levels, reverse=True):
        # once list of length 1 gets handled as tuple in pandas
        # then this check is redundant (just pass `list(range(level+1))`)
        grouper = 0 if level == 0 else list(range(level + 1))
        output = output.groupby(level=grouper).pipe(process_groups)
    return output
