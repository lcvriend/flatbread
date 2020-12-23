from functools import wraps
from typing import Optional

import pandas as pd

from flatbread import totals
from flatbread.aggregate import set_value
from flatbread.axes import get_axis_number, transpose, add_axis_level
from flatbread.types import AxisAlias, IndexName, LevelAlias
from flatbread.utils import log, copy


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
