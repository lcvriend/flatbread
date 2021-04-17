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
