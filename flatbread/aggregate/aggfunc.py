from functools import wraps, partial
from typing import Any

import pandas as pd # type: ignore
from pandas._libs import lib

import flatbread.config as config
import flatbread.utils.log as log
import flatbread.axes as axes
import flatbread.levels as levels
from flatbread.aggregate import AGG_SETTINGS


@log.entry
@config.load_settings(AGG_SETTINGS)
# @axes.get_axis_number
# @levels.get_level_number
def add(
    df:          pd.DataFrame,
    aggfunc:    callable,
    *,
    axis:        Any  = 0,
    level:       Any  = 0,
    ndigits:     int  = None,
    unit:        int  = 100,
    label_ori:   str  = None,
    label_agg:   str  = None,
    drop_totals: bool = False,
    **kwargs
) -> pd.DataFrame:
    # get_axis = lambda x: axes._get_axis_number(x) if lib.is_scalar(x) else x
    # axis = get_axis(axis)
    axis = axes._get_axis_number(axis)

    agged = df.pipe(aggfunc, **kwargs).pipe(
        axes.add_axis_level,
        item  = label_agg,
        axis  = 1,
        level = -1,
    )
    df = df.pipe(
        axes.add_axis_level,
        item  = label_ori,
        axis  = 1,
        level = -1,
    )
    new_tuples = (i for items in zip(df.columns, agged.columns) for i in items)
    columns = pd.MultiIndex.from_tuples(new_tuples)
    return df.join(agged)[columns]
