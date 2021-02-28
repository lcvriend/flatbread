"""
Toolbox for operating on columns of table.
"""

from typing import Any, Sequence

import pandas as pd # type: ignore
from pandas._libs import lib

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


def percs(
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


def add_category(
    s:    pd.Series,
    category: Any,
) -> pd.Index:
    "Add ``category`` to categorical series ``s``."

    def add_cat(s, cats):
        if isinstance(s.dtype, pd.CategoricalDtype):
            cats = [item for item in cats if item not in s.cat.categories]
            s = s.cat.add_categories(cats)
        return s

    if lib.is_scalar(category):
        category = [category]

    # if isinstance(index, pd.MultiIndex):
    #     index = index.set_levels(
    #         add_cat(index.levels[level], category),
    #         level=level)
    # else:
    #     index = add_cat(index, category)
    return add_cat(s, category)


@utils.copy
def drop(df: pd.DataFrame, columns: Sequence) -> pd.DataFrame:
    "Drop ``columns`` from ``df``."
    return df.drop(columns, axis=1)
