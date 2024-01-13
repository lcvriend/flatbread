from functools import singledispatch
from typing import Callable, Literal, TypeAlias

import pandas as pd


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


def offset_date_field(
    df: pd.DataFrame,
    date_field: str,
    year_field: str,
) -> pd.DataFrame:
    offset_year = df[year_field].max()

    def shift_dates(group):
        offset = pd.DateOffset(years = offset_year - group.name)
        return group.shift(freq = offset)

    return (
        df
        .set_index(date_field, drop=False)
        .groupby(year_field, group_keys=False)
        .apply(shift_dates)
        .rename_axis(date_field + '_offs')
        .reset_index()
    )


def _custom_sort_index(
    df: pd.DataFrame,
    order: list|pd.CategoricalDtype,
    axis: Axis = 0,
    level: int|str|None = None,
) -> pd.DataFrame:
    index = df.index if axis in [0, 'index'] else df.columns
    if isinstance(index, pd.MultiIndex):
        index = index.levels[level]
    order = [i for i in order if i in index]
    return df.reindex(order, axis=axis, level=level)


def custom_sort_index(
    df: pd.DataFrame,
    order: list|pd.CategoricalDtype,
    axis: Axis = 0,
    level: int|str|None = None,
):
    sorter = lambda idx: idx.map({n:m for m,n in pd.Series(order).items()})
    return df.sort_index(axis=axis, level=level, key=sorter)
