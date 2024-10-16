from typing import Any, Literal, TypeAlias

import pandas as pd

from flatbread import DEFAULTS


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


def _sort_index_from_list(
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


def sort_index_from_list(
    data: pd.DataFrame|pd.Series,
    order: list,
    axis: Axis = 0,
    level: int|str|None = None,
) -> pd.DataFrame|pd.Series:
    sorter = lambda idx: idx.map({n:m for m,n in enumerate(order)})
    return data.sort_index(axis=axis, level=level, key=sorter)


def sort_totals(
    data: pd.DataFrame|pd.Series,
    axis: Axis = 0,
    level: int = 0,
    **kwargs,
):
    """
    Sort an index alphabetically except for special labels which should come last.
    """
    def safe_index(lst: list, value: str, default: int = -1) -> int:
        index_map = {v:i for i,v in enumerate(lst)}
        return index_map.get(value, default)

    def assign_order(i) -> tuple[int, Any]:
        return safe_index(labels, i), i

    labels = [
        DEFAULTS['subtotals']['label'],
        DEFAULTS['totals']['label'],
    ]

    output = data.sort_index(
        axis = axis,
        level = level,
        key = lambda idx: idx.map(assign_order),
        **kwargs,
    )
    return output
