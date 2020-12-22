from collections.abc import Iterable

import pandas as pd
from flatbread.utils import log, copy
from flatbread.types import AxisAlias, IndexName, LevelAlias, LevelsAlias
from flatbread.axes import (
    get_axis_number,
    transpose,
    add_category,
    add_item_to_key,
    replace_item_in_key,
    key_to_list,
)
from flatbread.levels import (
    get_level_number,
    validate_index_for_within_operations,
)
from flatbread.aggregate import set_value


@log.entry
@copy
def add(
    df:             pd.DataFrame,
    *,
    axis:           AxisAlias   = 0,
    level:          LevelsAlias = 0,
    totals_name:    IndexName   = None,
    subtotals_name: IndexName   = None,
) -> pd.DataFrame:

    """Add totals to `df` on `level` of `axis`.

    Arguments
    ---------
    df : pd.DataFrame
    axis : AxisAlias
        Axis to add totals:
        0 : add row with column totals
        1 : add column with row totals
        2 : add row and column totals
    level : LevelsAlias
        Level to use for calculating the totals. Level 0 adds row/column
        totals, otherwise subtotals are added within the specified level.
        Multiple levels may be supplied in a list.
    totals_name : IndexName, default=CONFIG.aggregation['totals_name']
        Name for the row/column totals.
    subtotals_name : IndexName, default=CONFIG.aggregation['subtotals_name']
        Name for the row/column subtotals.

    Returns
    -------
    pd.DataFrame
    """

    totals_name = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    if isinstance(level, (int, str)):
        level = [level]
    for level_ in level:
        df = _add(
            df,
            axis=axis,
            level=level_,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        )
    return df


def _add(
    df:             pd.DataFrame,
    *,
    axis:           AxisAlias  = 0,
    level:          LevelAlias = 0,
    totals_name:    IndexName  = None,
    subtotals_name: IndexName  = None,
) -> pd.DataFrame:

    totals_name = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    axis = get_axis_number(axis)
    level = get_level_number(df, axis, level)
    if level == 0:
        if axis < 2:
            return _add_axis(
                df,
                axis=axis,
                totals_name=totals_name,
                subtotals_name=subtotals_name,
            )
        else:
            return df.pipe(
                add,
                axis=0,
                totals_name=totals_name,
                subtotals_name=subtotals_name,
            ).pipe(
                add,
                axis=1,
                totals_name=totals_name,
                subtotals_name=subtotals_name,
            )
    # Add within if level is not 0
    else:
        return _add_within(
            df,
            axis=axis,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        )


@transpose
def _add_axis(
    df:             pd.DataFrame,
    *,
    totals_name:    IndexName = None,
    subtotals_name: IndexName = None,
) -> pd.DataFrame:

    totals_name = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    is_totals_row = lambda x: totals_name in x or subtotals_name in x
    totals = pd.Series(
        df.loc[[not is_totals_row(item) for item in df.index]].sum(),
        name=totals_name
    ).to_frame().T

    if isinstance(df.index, pd.MultiIndex):
        key = replace_item_in_key([''] * df.index.nlevels, totals_name, level=0)
        totals.index = pd.MultiIndex.from_tuples([key])
        for level, item in enumerate(key):
            df.index = add_category(df.index, item, level=level)
    else:
        totals.index.name = df.index.name
        df.index = add_category(df.index, totals_name)
    return pd.concat([df, totals])


def _add_within(
    df:             pd.DataFrame,
    *,
    axis:           int       = 0,
    level:          int       = -1,
    totals_name:    IndexName = None,
    subtotals_name: IndexName = None,
) -> pd.DataFrame:

    totals_name = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    if axis < 2:
        return _add_axis_within(
            df,
            axis=axis,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        )
    else:
        return df.pipe(
            _add_within,
            axis=0,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        ).pipe(
            _add_within,
            axis=1,
            level=level,
            totals_name=totals_name,
            subtotals_name=subtotals_name,
        )


@transpose
def _add_axis_within(
    df:             pd.DataFrame,
    *,
    level:          int       = -1,
    totals_name:    IndexName = None,
    subtotals_name: IndexName = None,
) -> pd.DataFrame:

    validate_index_for_within_operations(df.index, level)
    totals_name = set_value('totals_name', totals_name)
    subtotals_name = set_value('subtotals_name', subtotals_name)

    is_totals_row = lambda x: totals_name in x or subtotals_name in x
    totals = df.loc[
        [not is_totals_row(item) for item in df.index]
    ].groupby(level=list(range(level)), sort=False).sum()

    def make_key(key, item, nlevels):
        key = key_to_list(key)
        key.append(item)
        if len(key) < nlevels:
            key = key + [''] * (nlevels - len(key))
        return tuple(key)

    nlevels = df.index.nlevels
    key = [make_key(key, subtotals_name, nlevels) for key in totals.index]
    totals.index = pd.MultiIndex.from_tuples(key)

    if isinstance(df.index, pd.MultiIndex):
        for idx_level, item in enumerate(totals.index.levels):
            df.index = add_category(df.index, item, level=idx_level)
    else:
        df.index = add_category(df.index, subtotals_name)

    output = df.append(totals)
    for idx in range(level):
        index = df.index.levels[idx]
        output = output.reindex(index, level=idx)
    return output


@copy
@log.entry
def add_totals_group(df, group_name):
    levels = list(range(df.index.nlevels))
    group = df.groupby(level=levels[1:]).sum()
    group.index = pd.MultiIndex.from_tuples(
        [add_item_to_key(key, group_name) for key in group.index]
    )
    return df.append(group)
