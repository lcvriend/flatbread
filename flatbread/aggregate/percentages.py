from functools import wraps
from typing import Optional

import pandas as pd

from flatbread import totals
from flatbread.aggregate import set_value
from flatbread.axes import get_axis_number, transpose, add_axis_level
from flatbread.types import AxisAlias, IndexName, LevelAlias
from flatbread.utils import log, copy


def _add_totals(df, axis=0, **kwargs):
    level = kwargs.get('level') or 0

    totals_name = set_value('totals_name', kwargs.get('totals_name'))
    subtotals_name = set_value('subtotals_name', kwargs.get('subtotals_name'))
    totals_name = totals_name if level == 0 else subtotals_name

    index = df.columns if axis == 1 else df.index
    is_total = lambda x: totals_name in x
    has_totals = any([is_total(item) for item in index])

    if not has_totals:
        df = df.pipe(totals.add, axis=axis, level=level)
    return df


def _drop_totals(df, axis=0, **kwargs):
    level = kwargs.get('level') or 0

    totals_name = set_value('totals_name', kwargs.get('totals_name'))
    subtotals_name = set_value('subtotals_name', kwargs.get('subtotals_name'))
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


def add_totals(axis):
    def decorator(func):
        @wraps(func)
        def wrapper(df, **kwargs):
            df = _add_totals(df, axis, **kwargs)
            result = func(df, **kwargs)
            return result
        return wrapper
    return decorator


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


def round_percentages(s, ndigits=-1):
    "Round percentages in a way that they always add up to 100%."
    if ndigits < 0:
        return s
    cumsum = s.cumsum().round(ndigits)
    prev_baseline = cumsum.shift(1).fillna(0)
    return cumsum - prev_baseline


@log.entry
def add(
    df:            pd.DataFrame,
    *,
    axis:           AxisAlias     = 0,
    level:          LevelAlias    = 0,
    totals_name:    IndexName     = None,
    subtotals_name: IndexName     = None,
    ndigits:        Optional[int] = None,
    label_abs:      Optional[str] = None,
    label_rel:      Optional[str] = None,
    drop_totals:    bool          = False,
) -> pd.DataFrame:

    """Add percentages to `df` on `level` of `axis` rounded to `ndigits`.

    This operation will result in a table containing the absolute values as well
    as the percentage values. The absolute and percentage columns will be
    labelled by an added level to the column index.

    (Sub)totals are required to calculate the percentages. If (sub)totals are
    present (`totals_name` and `subtotals_name` are used to identify totals
    within the table) these will be used. When no (sub)totals are found, they
    will be added to the table. Set `drop_totals` to False to exlude them from
    the output.

    Arguments
    ---------
    df : pd.DataFrame
    axis : AxisAlias
        Axis to use for calculating the percentages:
        0 : percentages of each row by the column totals
        1 : percentages of each column by the row totals
        2 : percentages of each field by the table total
    level : LevelAlias
        Level to use for calculating the percentages. Level 0 takes row/column
        totals, otherwise use subtotals within the specified level.
    totals_name : IndexName, default=CONFIG.aggregation['totals_name']
        Name identifying the row/column totals.
    subtotals_name : IndexName, default=CONFIG.aggregation['subtotals_name']
        Name identifying the row/column subtotals.
    ndigits : int, default=CONFIG.aggregation['ndigits']
        Number of digits used for rounding the percentages.
    label_abs : str, default=CONFIG.aggregation['label_abs']
        Value used for labelling the absolute columns.
    label_abs : str, default=CONFIG.aggregation['label_rel']
        Value used for labelling the relative columns.
    drop_totals : bool, default=False
        Drop row/column totals from output.

    Returns
    -------
    pd.DataFrame
    """

    ndigits        = set_value('ndigits', ndigits)
    totals_name    = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)
    label_abs      = set_value('label_abs', label_abs)
    label_rel      = set_value('label_rel', label_rel)

    percs = df.pipe(
        transform,
        axis           = axis,
        level          = level,
        totals_name    = totals_name,
        subtotals_name = subtotals_name,
        ndigits        = ndigits,
        drop_totals    = drop_totals,
    ).pipe(
        add_axis_level,
        item  = label_rel,
        axis  = 1,
        level = -1,
    )

    df = df.pipe(
        _add_totals,
        axis  = axis,
        level = level,
    ).pipe(
        add_axis_level,
        item  = label_abs,
        axis  = 1,
        level = -1,
    )

    if drop_totals:
        df = df.pipe(
            _drop_totals,
            axis           = axis,
            level          = level,
            totals_name    = totals_name,
            subtotals_name = subtotals_name,
        )

    new_tuples = (i for items in zip(df.columns, percs.columns) for i in items)
    columns = pd.MultiIndex.from_tuples(new_tuples)
    return df.join(percs)[columns]


@log.entry
@copy
def transform(
    df: pd.DataFrame,
    *,
    axis:           AxisAlias  = 0,
    level:          LevelAlias = 0,
    totals_name:    IndexName  = None,
    subtotals_name: IndexName  = None,
    ndigits:        int        = None,
    drop_totals:    bool       = False,
) -> pd.DataFrame:

    """Transform values of `df` to percentages on `level` of `axis` rounded to
    `ndigits`.

    (Sub)totals are required to calculate the percentages. If (sub)totals are
    present (`totals_name` and `subtotals_name` are used to identify totals
    within the table) these will be used. When no (sub)totals are found, they
    will be added to the table. Set `drop_totals` to False to exlude them from
    the output.

    Arguments
    ---------
    df : pd.DataFrame
    axis : AxisAlias
        Axis to use for calculating the percentages:
        0 : percentages of each row by the column totals
        1 : percentages of each column by the row totals
        2 : percentages of each field by the table total
    level : LevelAlias
        Level to use for calculating the percentages. Level 0 takes row/column
        totals, otherwise use subtotals within the specified level.
    totals_name : IndexName, default=CONFIG.aggregation['totals_name']
        Name identifying the row/column totals.
    subtotals_name : IndexName, default=CONFIG.aggregation['subtotals_name']
        Name identifying the row/column subtotals.
    ndigits : int, default=CONFIG.aggregation['ndigits']
        Number of digits used for rounding the percentages.
        Set to -1 to not round.
    drop_totals : bool, default=False
        Drop row/column totals from output.

    Returns
    -------
    pd.DataFrame
    """

    ndigits        = set_value('ndigits', ndigits)
    totals_name    = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    axis = get_axis_number(axis)
    if axis < 2:
        return _axis_wise(
            df,
            axis=axis,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
            ndigits=ndigits,
            drop_totals=drop_totals,
        )
    else:
        return _table_wise(
            df,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
            ndigits=ndigits,
            drop_totals=drop_totals,
        )


@transpose
@add_totals(axis=0)
@drop_totals(axis=0)
def _axis_wise(
    df:             pd.DataFrame,
    *,
    level:          LevelAlias = 0,
    totals_name:    IndexName  = None,
    subtotals_name: IndexName  = None,
    ndigits:        int        = None,
    **kwargs
) -> pd.DataFrame:

    ndigits        = set_value('ndigits', ndigits)
    totals_name    = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    if level > 0:
        totals_name = subtotals_name
    if isinstance(df.index, pd.MultiIndex):
        totals = (
            df.xs(totals_name, level=level, drop_level=False)
            .reindex(df.index)
            .bfill()
        )
    else:
        totals = df.loc[totals_name]

    result = df.div(totals).multiply(100)
    return result.pipe(round_percentages, ndigits=ndigits)



@add_totals(axis=2)
@drop_totals(axis=2)
def _table_wise(
    df,
    *,
    level          = 0,
    totals_name    = None,
    subtotals_name = None,
    ndigits        = None,
    **kwargs
) -> pd.DataFrame:

    ndigits        = set_value('ndigits', ndigits)
    totals_name    = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    if level > 0:
        totals_name = subtotals_name
    if isinstance(df.index, pd.MultiIndex):
        totals = (
            df.xs(totals_name, level=level, drop_level=False)
            .xs(totals_name, axis=1, level=level, drop_level=False)
            .reindex_like(df, method='bfill')
        )
    else:
        totals = df.loc[totals_name, totals_name]

    result = df.div(totals).multiply(100)
    return result.pipe(round_percentages, ndigits=ndigits)
