"""
Toolbox for operating on rows of table.
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
    categories: Any,
) -> pd.DataFrame:
    df.index = axes.order_categories(df.index, categories)
    return df


def add_level(
    df:         pd.DataFrame,
    item:       Any,
    level_name: Any,
    level:      int,
) -> pd.DataFrame:
    "Add ``level`` filled with ``item`` named ``level_name`` to index."

    return axes.add_axis_level(
        df, item,
        item       = item,
        level      = level,
        level_name = level_name,
    )


def totals(
    df:    pd.DataFrame,
    level: Any = 0,
    **kwargs
) -> pd.DataFrame:
    "Add totals to rows of ``df`` on ``level``."
    return totals.add(df, level=level, **kwargs)


def percs(
    df:    pd.DataFrame,
    level: Any = 0,
    add = False,
    **kwargs
) -> pd.DataFrame:
    "Add percentages or transform rows of ``df`` into percentages on ``level``."
    if add:
        return percs.add(df, level=level, **kwargs)
    return percs.transform(df, level=level, **kwargs)


def timeseries(df, datefield):
    return df.set_index(datefield).sort_index()


def timeseries_offset(df, datefield, yearfield, offset_year):
    """Create ``df`` with offset DateTimeIndex from ``datefield``.
    The offset will be determined by ``yearfield`` and ``offset_year``.
    """

    ts = (
        df
        .set_index(datefield)
        .groupby(yearfield)
        .apply(lambda g: g.shift(freq=pd.DateOffset(years=offset_year-g.name)))
        .reset_index(level=0, drop=True)
    )
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()


@utils.copy
def rows(df: pd.DataFrame, rows: Sequence) -> pd.DataFrame:
    "Drop ``rows`` from ``df``."
    return df.drop(rows)
