"""
Functions for adding totals/subtotals to tables.
"""

from collections.abc import Iterable
from functools import wraps
from typing import Any

import pandas as pd # type: ignore

import flatbread.utils as utils
import flatbread.utils.log as log
import flatbread.config as config
import flatbread.axes as axes
import flatbread.levels as levels
from flatbread.aggregate import TOTALS_SETTINGS


@log.entry
@utils.copy
@config.load_settings(TOTALS_SETTINGS)
def add(
    df:             pd.DataFrame,
    *,
    axis:           Any = 0,
    level:          Any = 0,
    totals_name:    str = None,
    subtotals_name: str = None,
    **kwargs
) -> pd.DataFrame:
    """
    Add totals to `df` on `level` of `axis`.

    Arguments
    ---------
    df : pd.DataFrame
    axis : {0, 'index', 1, 'columns', 2, 'all'} or tuple, default 0
        Axis to add totals:

        * index (0) : add row with column totals
        * columns (1) : add column with row totals
        * all (2) : add row and column totals

        Tuple (size 2) mapping level(s) to rows/columns may also be supplied
        (will ignore ``level``).
    level : int, level name, or sequence of such, default 0
        Level number or name for the level to use for calculating the totals.
        Level 0 adds row/column totals, otherwise subtotals are added within
        the specified level. Multiple levels may be supplied in a list.
    totals_name : str, default 'Total'
        Name for the row/column totals.
    subtotals_name : str, default 'Subtotal'
        Name for the row/column subtotals.

    Returns
    -------
    pd.DataFrame
        DataFrame with added (sub)totals.
    """
    axlevels = levels.get_axlevels(df, axis, level)
    for ax, lvls in enumerate(axlevels):
        for level in lvls:
            df = df.pipe(
                _add,
                axis           = ax,
                level          = level,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
            )
    return df


@axes.get_axis_number
@levels.get_level_number
def _add(
    df:             pd.DataFrame,
    *,
    axis:           int = 0,
    level:          int = 0,
    totals_name:    str = None,
    subtotals_name: str = None,
    **kwargs
) -> pd.DataFrame:
    if level == 0:
        if axis < 2:
            return _add_to_axis(
                df,
                axis=axis,
                totals_name=totals_name,
                subtotals_name=subtotals_name,
            )
        else:
            return df.pipe(
                add,
                axis=0,
                totals_name=totals_name,
                subtotals_name=subtotals_name,
            ).pipe(
                add,
                axis=1,
                totals_name=totals_name,
                subtotals_name=subtotals_name,
            )
    # Add within if level is not 0
    else:
        return _add_within_axis(
            df,
            axis=axis,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        )


@axes.transpose
def _add_to_axis(
    df:             pd.DataFrame,
    *,
    totals_name:    str = None,
    subtotals_name: str = None,
    **kwargs
) -> pd.DataFrame:
    test = lambda x,lbl: lbl in x if isinstance(x, tuple) else lbl == x
    is_totals_row = lambda x: test(x, totals_name) or test(x, subtotals_name)
    no_totals = [not is_totals_row(item) for item in df.index]
    totals = pd.Series(df.loc[no_totals].sum(), name=totals_name).to_frame().T

    if isinstance(df.index, pd.MultiIndex):
        nlevels = df.index.nlevels
        key = axes.replace_item_in_key([''] * nlevels, totals_name, level=0)
        totals.index = pd.MultiIndex.from_tuples([key])
        for level, item in enumerate(key):
            df.index = axes.add_category(df.index, item, level=level)
    else:
        totals.index.name = df.index.name
        df.index = axes.add_category(df.index, totals_name)
    return pd.concat([df, totals])


# @levels.validate_index_for_within_operations
def _add_within_axis(
    df:             pd.DataFrame,
    *,
    axis:           int = 0,
    level:          int = -1,
    totals_name:    str = None,
    subtotals_name: str = None,
    **kwargs
) -> pd.DataFrame:
    kwargs.update(
        dict(
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        )
    )
    if axis < 2:
        return _add_to_axis_level(df, axis=axis, **kwargs)
    else:
        assert df.index.nlevels > level, f"index has no level {level}"
        assert df.columns.nlevels > level, f"columns have no level {level}"

        return df.pipe(
            _add_within_axis, axis=0, **kwargs
        ).pipe(
            _add_within_axis, axis=1, **kwargs
        )


@axes.transpose
def _add_to_axis_level(
    df:             pd.DataFrame,
    *,
    level:          int = -1,
    totals_name:    str = None,
    subtotals_name: str = None,
    **kwargs
) -> pd.DataFrame:
    is_totals_row = lambda x: totals_name in x or subtotals_name in x
    totals = df.loc[
        [not is_totals_row(item) for item in df.index]
    ].groupby(level=list(range(level)), sort=False).sum()

    def make_key(key, item, nlevels):
        key = utils.listify(key)
        key.append(item)
        if len(key) < nlevels:
            key = key + [''] * (nlevels - len(key))
        return tuple(key)

    nlevels = df.index.nlevels
    key = [make_key(key, subtotals_name, nlevels) for key in totals.index]
    totals.index = pd.MultiIndex.from_tuples(key)

    if isinstance(df.index, pd.MultiIndex):
        for idx_level, item in enumerate(totals.index.levels):
            df.index = axes.add_category(df.index, item, level=idx_level)
    else:
        df.index = axes.add_category(df.index, subtotals_name)

    output = df.append(totals)

    for i in range(level):
        # get the labels in order
        labels = list(dict.fromkeys(df.index.get_level_values(i)))
        output = output.reindex(labels, level=i)
    return output


################################################################################### DECORATORS
################################################################################


def add_totals(axis):
    def decorator(func):
        @wraps(func)
        def wrapper(df, **kwargs):
            df = _add_totals(df, axis, **kwargs)
            result = func(df, **kwargs)
            return result
        return wrapper
    return decorator


@config.load_settings(TOTALS_SETTINGS)
def _add_totals(df, axis=0, totals_name=None, subtotals_name=None, **kwargs):
    level = kwargs.get('level') or 0
    totals_name = totals_name if level == 0 else subtotals_name

    index = df.columns if axis == 1 else df.index
    is_total = lambda x: totals_name in x
    has_totals = any([is_total(item) for item in index])

    if not has_totals:
        df = df.pipe(add, axis=axis, level=level)
    return df


def drop_totals(axis):
    def decorator(func):
        @wraps(func)
        def wrapper(df, **kwargs):
            drop_totals = kwargs.get('drop_totals', False)
            result = func(df, **kwargs)
            if drop_totals:
                result = _drop_totals(result, axis, **kwargs)
            return result
        return wrapper
    return decorator


@config.load_settings(TOTALS_SETTINGS)
def _drop_totals(df, axis=0, totals_name=None, subtotals_name=None, **kwargs):
    level = kwargs.get('level') or 0
    totals_name = totals_name if level == 0 else subtotals_name

    def exclude_totals(df, axis):
        index = df.columns if axis == 1 else df.index
        is_total = lambda x: totals_name in x
        if isinstance(index, pd.MultiIndex):
            return [not is_total(item[level]) for item in index]
        return [not is_total(item) for item in index]

    rows = exclude_totals(df, axis=0)
    columns = exclude_totals(df, axis=1)

    if axis == 0:
        return df.loc[rows]
    if axis == 1:
        return df.loc[:, columns]

    return df.loc[rows, columns]
