"""
Toolbox for operating on columns of table.
"""

from typing import Any, Sequence

import pandas as pd # type: ignore

import flatbread.utils as utils
import flatbread.axes as axes
import flatbread.aggregate.totals as totals
import flatbread.aggregate.percentages as percs


@utils.copy
def order(
    df:         pd.DataFrame,
    column:     Any,
    categories: Any,
) -> pd.DataFrame:
    df[column] = axes.order_categories(df[column], categories)
    return df


@utils.copy
def drop(df: pd.DataFrame, columns: Sequence) -> pd.DataFrame:
    "Drop ``columns`` from ``df``."
    return df.drop(columns, axis=1)


def add_level(
    df:         pd.DataFrame,
    item:       Any,
    level_name: Any,
    level:      int,
) -> pd.DataFrame:
    "Add ``level`` with value ``item`` named ``level_name`` to columns."
    return axes.add_axis_level(
        df,
        item,
        axis       = 1,
        item       = item,
        level      = level,
        level_name = level_name,
    )


def totals(
    df:    pd.DataFrame,
    level: Any = 0,
    **kwargs
) -> pd.DataFrame:
    "Add totals to columns of ``df`` on ``level``."
    return totals.add(df, axis=1, level=level, **kwargs)


def pct(
    df:    pd.DataFrame,
    level: Any = 0,
    add = False,
    **kwargs
) -> pd.DataFrame:
    """
    Add percentages or transform columns of ``df`` into percentages on
    ``level``.
    """
    if add:
        return percs.add(df, axis=1, level=level, **kwargs)
    return percs.transform(df, axis=1, level=level, **kwargs)


def ts_offset(
    df : pd.DataFrame,
    datefield,
    ref_year : int,
    adm_year_field=None,
    to_column=None,
) -> pd.DataFrame:
    """
    Offset dates of the ``datefield`` column in ``df`` so that they align with
    the ``ref_year``. This can be useful when comparing multiple years to each
    other or when plotting data.
    
    If ``datefield`` follows an administrative year, use ``adm_year_field`` to
    specify the column used to calculate the necessary offset.

    Arguments
    ---------
    df : pd.DataFrame
        Target table.
    datefield : scalar
        Name of target date column.
    ref_year : int
        Reference year to which the dates will be offset.
    adm_year_field : scalar, optional
        Name of column containing administrative year if applicable.
        If left empty the offset will be calculated on the datefield year.
    to_column : scalar, optional
        Name of column for the offset dates.
        If left empty ``datefield`` will be overwritten.
    """
    offset = lambda g: g + pd.DateOffset(years=ref_year-g.name)
    has_adm_year = adm_year_field is not None
    grouper = adm_year_field if has_adm_year else df.datefield.dt.year
    s = df.groupby(grouper)[datefield].apply(offset)
    to_column = datefield if to_column is None else to_column
    df[to_column] = s
    return df