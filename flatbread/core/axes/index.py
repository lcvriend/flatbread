import pandas as pd
import flatbread.core.select
import flatbread.core.axes.define
from flatbread.core.axes.define import add_idx_level


def select(df, criteria, **kwargs):
    return flatbread.core.select.rows(df, criteria, **kwargs)


def rename(df, mapper, level=0):
    return flatbread.core.axes.define.rename(df, mapper, level=level)


def set_index(df, index):
    df.index = index
    return df


def add_level(df, level_name, level):
    return add_idx_level(df, level_name, level=level)


def totals(df, level=0):
    return flatbread.core.aggregation.totals.add(df, level=level, **kwargs)


def timeseries_offset(df, datefield, yearfield, year):
    """
    Create `df` with offset DateTimeIndex from `datefield`.
    The offset will be determined by `yearfield` and `year`.
    """

    ts = (
        df
        .set_index(datefield)
        .groupby(yearfield)
        .apply(lambda g: g.shift(freq=pd.DateOffset(years=year-g.name)))
        .reset_index(level=0, drop=True)
    )
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()
