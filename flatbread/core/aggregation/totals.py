import pandas as pd
import flatbread.utils.log as log
from flatbread.utils.types import AxisAlias, IndexName, LevelAlias
from flatbread.utils.axes import get_axis_number
from flatbread.utils.levels import (
    get_level_number,
    validate_index_for_within_operations,
)
from flatbread.core import copy
from flatbread.core.axes.define import (
    add_category,
    add_item_to_key,
    replace_item_in_key,
    key_to_list,
)
from flatbread.core.aggregation.globals import TOTALS_NAME, SUBTOTALS_NAME


@log.entry
def add(
    df: pd.DataFrame,
    axis: AxisAlias = 0,
    level: LevelAlias = 0,
    totals_name: IndexName = TOTALS_NAME,
    subtotals_name: IndexName = SUBTOTALS_NAME,
) -> pd.DataFrame:

    "Add totals row/column to `level` of `axis` in `df`."

    axis = get_axis_number(axis)
    level = get_level_number(df, axis, level)
    if level == 0:
        if axis == 0:
            return _add_row(
                df,
                totals_name=totals_name,
            )
        elif axis == 1:
            return _add_col(
                df,
                totals_name=totals_name,
            )
        else:
            return add(
                add(
                    df,
                    axis=0,
                    totals_name=totals_name
                ),
                axis=1,
                totals_name=totals_name
            )
    # Add within if level is not 0
    else:
        return _add_within(
            df, axis=axis, level=level, totals_name=subtotals_name)


@copy
def _add_row(
    df: pd.DataFrame,
    totals_name: IndexName = TOTALS_NAME
) -> pd.DataFrame:

    # df.index = add_category(df.index, totals_name)
    totals = pd.Series(
        df.sum(), name=totals_name
    ).to_frame().T

    if isinstance(df.index, pd.MultiIndex):
        key = replace_item_in_key([''] * df.index.nlevels, totals_name, level=0)
        totals.index = pd.MultiIndex.from_tuples([key])
        for level, item in enumerate(key):
            df.index = add_category(df.index, item, level=level)
    else:
        df.index = add_category(df.index, totals_name)
    return pd.concat([df, totals])


def _add_col(
    df: pd.DataFrame,
    totals_name: IndexName = TOTALS_NAME,
) -> pd.DataFrame:

    df = df.T
    df = df.pipe(_add_row, totals_name=totals_name)
    return df.T


def _add_within(
    df: pd.DataFrame,
    axis: int = 0,
    level: int = -1,
    totals_name: IndexName = SUBTOTALS_NAME,
) -> pd.DataFrame:

    if axis == 0:
        return _add_row_within(
            df,
            level=level,
            totals_name=totals_name,
        )
    elif axis == 1:
        return _add_col_within(
            df,
            level=level,
            totals_name=totals_name,
        )
    else:
        return _add_within(
            _add_within(
                df,
                axis=0,
                level=level,
                totals_name=totals_name
            ),
            axis=1,
            level=level,
            totals_name=totals_name
        )


@copy
def _add_row_within(
    df: pd.DataFrame,
    level: int = -1,
    totals_name: IndexName = SUBTOTALS_NAME,
) -> pd.DataFrame:

    validate_index_for_within_operations(df.index, level)
    totals = df.groupby(level=list(range(level)), sort=False).sum()

    def make_key(key, item, nlevels):
        key = key_to_list(key)
        key.append(item)
        if len(key) < nlevels:
            key = key + [''] * (nlevels - len(key))
        return tuple(key)

    key = [make_key(key, totals_name, df.index.nlevels) for key in totals.index]
    totals.index = pd.MultiIndex.from_tuples(key)

    if isinstance(df.index, pd.MultiIndex):
        for idx_level, item in enumerate(totals.index.levels):
            df.index = add_category(df.index, item, level=idx_level)
    else:
        df.index = add_category(df.index, totals_name)

    output = df.append(totals)
    for idx in range(level):
        index = df.index.levels[idx]
        output = output.reindex(index, level=idx)
    return output


def _add_col_within(
    df: pd.DataFrame,
    level: int = -1,
    totals_name: IndexName = SUBTOTALS_NAME,
) -> pd.DataFrame:

    df = df.T
    df = df.pipe(_add_row_within, level=level, totals_name=totals_name)
    return df.T


@copy
@log.entry
def add_totals_group(df, group_name):
    levels = list(range(df.index.nlevels))
    group = df.groupby(level=levels[1:]).sum()
    group.index = pd.MultiIndex.from_tuples(
        [add_item_to_key(key, group_name) for key in group.index]
    )
    return df.append(group)
