from functools import wraps, partial
from typing import Any

import pandas as pd # type: ignore
from pandas._libs import lib

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
# @axes.get_axis_number
# @levels.get_level_number
def add(
    df:            pd.DataFrame,
    *,
    axis:           Any  = 0,
    level:          Any  = None,
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

    get_axis = lambda x: axes._get_axis_number(x) if lib.is_scalar(x) else x
    axis = get_axis(axis)

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
# @axes.get_axis_number
# @levels.get_level_number
def transform(
    df: pd.DataFrame,
    *,
    axis:           Any  = 0,
    level:          Any  = None,
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
    f = partial(levels._get_level_number, df)
    get_axis = lambda x: axes._get_axis_number(x) if lib.is_scalar(x) else x
    get_level = lambda x, y: f(x, y) if lib.is_scalar(x) else x

    axis = get_axis(axis)
    get_level = get_level(axis, level)

    settings = dict(
        level          = level,
        totals_name    = totals_name,
        subtotals_name = subtotals_name,
        ndigits        = ndigits,
        drop_totals    = drop_totals,
    )
    kwargs.update(settings)

    if isinstance(axis, int):
        if axis < 2:
            return _axis_wise(df, axis=axis, **kwargs)
        else:
            return _table_wise(df, axis=axis, **kwargs)
    else:
        return _table_wise_multilevel(
            df,
            axlevels = axis,
            **kwargs
        )


@axes.transpose
@totals.add_totals(axis=0)
@totals.drop_totals(axis=0)
def _axis_wise(
    df:             pd.DataFrame,
    level:          int,
    totals_name:    str,
    subtotals_name: str,
    ndigits:        int,
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


@totals.add_totals(axis=2)
@totals.drop_totals(axis=2)
def _table_wise(
    df:             pd.DataFrame,
    level:          int,
    subtotals_name: str,
    ndigits:        int,
    **kwargs
) -> pd.DataFrame:

    if level == 0:
        totals = df.iloc[-1, -1]
        if df.index.nlevels > 1 or df.columns.nlevels > 1:
            frame = pd.DataFrame().reindex_like(df)
            frame.iloc[-1, -1] = totals
            totals = frame.bfill().bfill(axis=1)
    else:
        totals = (
            df.xs(subtotals_name, level=level, drop_level=False)
            .xs(subtotals_name, axis=1, level=level, drop_level=False)
            .reindex_like(df).bfill().bfill(axis=1)
        )

    result = df.div(totals).multiply(100)
    return result.pipe(round_percentages, ndigits=ndigits)


# @totals.add_totals(axis=2)
# @totals.drop_totals(axis=2)
def _table_wise_multilevel(
    df:             pd.DataFrame,
    axlevels:       Any,
    totals_name:    str,
    subtotals_name: str,
    ndigits:        int,
    **kwargs
) -> pd.DataFrame:

    axlevels = [min(level) for level in axlevels]

    row_totals = totals_name if axlevels[0] == 0 else subtotals_name
    col_totals = totals_name if axlevels[1] == 0 else subtotals_name

    totals = (
        df.xs(row_totals, level=axlevels[0], drop_level=False)
        .xs(col_totals, axis=1, level=axlevels[1], drop_level=False)
        .reindex_like(df).bfill().bfill(axis=1)
    )

    result = df.div(totals).multiply(100)
    return result.pipe(round_percentages, ndigits=ndigits)
