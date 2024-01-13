from functools import singledispatch
from typing import Callable, Literal, TypeAlias

import pandas as pd


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


def get_label(label, aggfunc):
    if label is not None:
        return label
    if isinstance(aggfunc, str):
        return aggfunc
    if hasattr(aggfunc, '__name__') and aggfunc.__name__ != '<lambda>':
        return aggfunc.__name__
    return 'aggregation'


def get_ignored_keys(ignore_keys, label):
    if ignore_keys is None:
        return [label]
    elif isinstance(ignore_keys, str):
        return [label, ignore_keys]
    return [label, *ignore_keys]


def get_levels(levels, names):
    find_level = lambda lvl: lvl if isinstance(lvl, int) else names.index(lvl)
    if isinstance(levels, (int, str)):
        return [find_level(levels)]
    return [find_level(level) for level in levels]


def get_data_rows(index, ignore_keys):
    if isinstance(index, pd.MultiIndex):
        ignored = index.map(lambda i: all(key not in i for key in ignore_keys))
    else:
        ignored = index.map(lambda i: all(key != i for key in ignore_keys))
    return ignored


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
    ignored = get_ignored_keys(ignore_keys, label)
    rows = get_data_rows(data.index, ignored)

    padding = [_fill] * (data.index.nlevels - 1)
    key = tuple([label, *padding]) if padding else label
    data.loc[key] = data.loc[rows].agg(aggfunc, *args, **kwargs)
    return data


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
    ignored = get_ignored_keys(ignore_keys, label)
    rows = get_data_rows(data.index, ignored)

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
    nlevels = data.index.nlevels
    names = data.index.names

    label = get_label(label, aggfunc)
    ignored = get_ignored_keys(ignore_keys, label)
    levels = get_levels(levels, names)

    assert isinstance(df.index, pd.MultiIndex), 'Axis is not a MultiIndex'
    for level in levels:
        assert level < nlevels - 1, f'Level must be smaller than {nlevels - 1}'

    def process_groups(groups):
        processed = []
        for levels, group in groups:
            # create key
            levels = (levels,) if isinstance(levels, str) else levels
            padding = [_fill] * (len(names) - len(levels) - 1)
            key = list(levels) + [label] + padding

            # ignore totals and subtotal rows when aggregating
            rows = get_data_rows(group.index, ignored)

            # if no data rows were selected, then do not add subagg
            # this makes sure that for example a subtotal is added
            # to a totals row
            if rows.any():
                group.loc[tuple(key), :] = (
                    group
                    .loc[rows]
                    .agg(aggfunc, *args, **kwargs)
                )
            processed.append(group)
        return pd.concat(processed)

    output = data
    for level in sorted(levels, reverse=True):
        # once list of length 1 gets handled as tuple in pandas
        # this code may be simplified
        grouper = 0 if level == 0 else list(range(level + 1))
        output = output.groupby(level=grouper).pipe(process_groups)

    if axis == 1:
        output = output.T
    return output
