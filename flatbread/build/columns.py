from typing import Any

import pandas as pd # type: ignore

import flatbread.axes as axes
from flatbread.utils import copy
from flatbread.aggregate import totals


@copy
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
    "Add `level` with value `item` named `level_name` to columns."

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
    return totals.add(df, axis=1, level=level, **kwargs)
