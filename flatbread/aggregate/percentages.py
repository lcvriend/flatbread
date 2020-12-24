from functools import wraps
from typing import Any

import pandas as pd # type: ignore

import flatbread.config as config
import flatbread.utils as utils
import flatbread.utils.log as log
import flatbread.axes as axes
import flatbread.levels as levels
import flatbread.aggregate.totals as totals
from flatbread.aggregate import AGG_SETTINGS


def round_percentages(
    s: pd.Series,
    ndigits: int = -1
) -> pd.Series:
    "Round percentages in a way that they always add up to 100%."
    if ndigits < 0:
        return s
    cumsum = s.cumsum().round(ndigits)
    prev_baseline = cumsum.shift(1).fillna(0)
    return cumsum - prev_baseline


@log.entry
@config.load_settings(AGG_SETTINGS)
@axes.get_axis_number
@levels.get_level_number
def add(
    df:            pd.DataFrame,
    *,
    axis:           Any  = 0,
    level:          Any  = 0,
    totals_name:    str  = None,
    subtotals_name: str  = None,
    ndigits:        int  = None,
    label_abs:      str  = None,
    label_rel:      str  = None,
    drop_totals:    bool = False,
    **kwargs
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
    axis : {0 or 'index', 1 or 'columns', 2 or 'all'}, default 0
        Axis to use for calculating the percentages:
        0 : percentages of each row by the column totals
        1 : percentages of each column by the row totals
        2 : percentages of each field by the table total
    level : int, level name, default 0
        Level number or name for the level on which to calculate the
        percentages. Level 0 uses row/column totals, otherwise subtotals within
        the specified level are used.
    totals_name : str, default CONFIG.aggregation['totals_name']
        Name identifying the row/column totals.
    subtotals_name : str, default CONFIG.aggregation['subtotals_name']
        Name identifying the row/column subtotals.
    ndigits : int, default CONFIG.aggregation['ndigits']
        Number of digits used for rounding the percentages.
    label_abs : str, default CONFIG.aggregation['label_abs']
        Value used for labelling the absolute columns.
    label_abs : str, default CONFIG.aggregation['label_rel']
        Value used for labelling the relative columns.
    drop_totals : bool, default False
        Drop row/column totals from output.

    Returns
    -------
    pd.DataFrame
    """

    percs = df.pipe(
        transform,
        axis           = axis,
        level          = level,
        totals_name    = totals_name,
        subtotals_name = subtotals_name,
        ndigits        = ndigits,
        drop_totals    = drop_totals,
    ).pipe(
        axes.add_axis_level,
        item  = label_rel,
        axis  = 1,
        level = -1,
    )

    df = df.pipe(
        totals._add_totals,
        axis  = axis,
        level = level,
    ).pipe(
        axes.add_axis_level,
        item  = label_abs,
        axis  = 1,
        level = -1,
    )

    if drop_totals:
        df = df.pipe(
            totals._drop_totals,
            axis           = axis,
            level          = level,
            totals_name    = totals_name,
            subtotals_name = subtotals_name,
        )

    new_tuples = (i for items in zip(df.columns, percs.columns) for i in items)
    columns = pd.MultiIndex.from_tuples(new_tuples)
    return df.join(percs)[columns]


@log.entry
@utils.copy
@config.load_settings(AGG_SETTINGS)
@axes.get_axis_number
@levels.get_level_number
def transform(
    df: pd.DataFrame,
    *,
    axis:           Any  = 0,
    level:          Any  = 0,
    totals_name:    str  = None,
    subtotals_name: str  = None,
    ndigits:        int  = None,
    drop_totals:    bool = False,
    **kwargs
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
    axis : {0 or 'index', 1 or 'columns', 2 or 'all'}, default 0
        Axis to use for calculating the percentages:
        0 : percentages of each row by the column totals
        1 : percentages of each column by the row totals
        2 : percentages of each field by the table total
    level : int, level name, default 0
        Level number or name for the level on which to calculate the
        percentages. Level 0 uses row/column totals, otherwise subtotals within
        the specified level are used.
    totals_name : str, default ONFIG.aggregation['totals_name']
        Name identifying the row/column totals.
    subtotals_name : str, default CONFIG.aggregation['subtotals_name']
        Name identifying the row/column subtotals.
    ndigits : int, default CONFIG.aggregation['ndigits']
        Number of digits used for rounding the percentages.
        Set to -1 to not round.
    drop_totals : bool, default False
        Drop row/column totals from output.

    Returns
    -------
    pd.DataFrame
    """

    kwargs.update(
        dict(
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
            ndigits=ndigits,
            drop_totals=drop_totals,
        )
    )
    if axis < 2:
        return _axis_wise(df, axis=axis, **kwargs)
    else:
        return _table_wise(df, **kwargs)


@config.load_settings(AGG_SETTINGS)
@axes.transpose
@totals.add_totals(axis=0)
@totals.drop_totals(axis=0)
def _axis_wise(
    df:             pd.DataFrame,
    *,
    level:          int = 0,
    totals_name:    str = None,
    subtotals_name: str = None,
    ndigits:        int = None,
    **kwargs
) -> pd.DataFrame:

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


@config.load_settings(AGG_SETTINGS)
@totals.add_totals(axis=2)
@totals.drop_totals(axis=2)
def _table_wise(
    df,
    *,
    level:          int = 0,
    totals_name:    str = None,
    subtotals_name: str = None,
    ndigits:        int = None,
    **kwargs
) -> pd.DataFrame:

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
