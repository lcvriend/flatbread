"""
Toolbox for manipulating tables.
"""

import pandas as pd
import flatbread.axes as axes


def combine_dfs(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    label1: str,
    label2: str,
    add_labels_to: str = 'bottom',
) -> pd.DataFrame:
    """
    Combine two similarly structured tables into one.
    Columns of each table will be labeled accordingly.
    These labels can be added either to the bottom or the top of the multiindex.
    When adding to the top the two tables will be joined.
    When adding to the bottom the two tables zipped together.
    """
    bottom = add_labels_to == 'bottom'
    level = -1 if bottom else 0

    df1 = df1.pipe(
        axes.add_axis_level,
        item  = label1,
        axis  = 1,
        level = level,
    )
    df2 = df2.pipe(
        axes.add_axis_level,
        item  = label2,
        axis  = 1,
        level = level,
    )
    do_zip = lambda l,r: (i for items in zip(l,r) for i in items)
    do_append = lambda l,r: list(l) + list(r)
    method = do_zip if bottom else do_append
    names = list(df1.columns.names)
    new_tuples = [i for i in method(df1.columns, df2.columns)]
    columns = pd.MultiIndex.from_tuples(new_tuples, names=names)
    return df1.join(df2).reindex(columns, axis=1)


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