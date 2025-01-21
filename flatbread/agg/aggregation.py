from functools import singledispatch
from typing import Callable, Literal, TypeAlias
import warnings

import pandas as pd

from flatbread import chaining

# Ignore lexsort warning as agg is meant to keep the original order of the df in tact
warnings.filterwarnings(
    'ignore',
    category=pd.errors.PerformanceWarning,
    message='indexing past lexsort depth may impact performance.',
    module='flatbread.agg.aggregation',
)


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


# region AGGREGATION

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


# region #series
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


# region #dataframe
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


# region SUBAGG

@singledispatch
def add_subagg(
    data,
    aggfunc: str|Callable,
    *args,
    level: int|str|list[int|str] = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    **kwargs,
):
    raise NotImplementedError('No implementation for this type')


# region #series
@add_subagg.register
def _(
    s: pd.Series,
    aggfunc: str|Callable,
    *args,
    level: int|str|list[int|str] = 0,
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
        level = level,
        label = label,
        ignore_keys = ignore_keys,
        _fill = _fill,
        **kwargs,
    )
    return output


# region #dataframe
@add_subagg.register
def _(
    df: pd.DataFrame,
    aggfunc: str|Callable,
    *args,
    axis: int = 0,
    level: int|str|list[int|str] = 0,
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
        level = level,
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
    level: int|str|list[int|str] = 0,
    label: str|None = None,
    ignore_keys: str|list[str]|None = None,
    _fill = '',
    **kwargs,
):
    names = data.index.names
    label = get_label(label, aggfunc)
    levels = get_levels(level, names)

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

            # only add subagg if there are two or more data rows selected
            # - skip total rows, etc.
            # - skip if there is only one row selected
            if sum(rows) > 1:
                subagged = group.loc[rows].agg(aggfunc, *args, **kwargs)
                group.loc[tuple(key),:] = subagged
            processed.append(group)
        return pd.concat(processed)

    output = data
    for level in sorted(levels, reverse=True):
        # once list of length 1 gets handled as tuple in pandas
        # then this check is redundant (just pass `list(range(level+1))`)
        grouper = 0 if level == 0 else list(range(level + 1))
        output = output.groupby(level=grouper, sort=False).pipe(process_groups)
    return output
