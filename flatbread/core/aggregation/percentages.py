import pandas as pd
from flatbread.utils import log
from flatbread.utils.types import AxisAlias, IndexName, LevelAlias
from flatbread.utils.axes import get_axis_number
from flatbread.core import copy
from flatbread.core.axes.define import add_idx_level
from flatbread.core.aggregation.globals import (
    TOTALS_NAME,
    SUBTOTALS_NAME,
    NDIGITS,
    LABELS_ABS,
    LABELS_REL
)


@log.entry
def add(
    df: pd.DataFrame,
    axis: AxisAlias = 0,
    level: LevelAlias = 0,
    totals_name: IndexName = TOTALS_NAME,
    ndigits: int = NDIGITS,
    label_abs: str = LABELS_ABS,
    label_rel: str = LABELS_REL,
) -> pd.DataFrame:
    percs = df.pipe(
        transform,
        axis        = axis,
        level       = level,
        totals_name = totals_name,
        ndigits     = ndigits
    ).pipe(
        add_idx_level,
        level_name  = label_rel,
        axis        = 1,
        level       = -1,
    )

    df = df.pipe(add_idx_level, level_name=label_abs, axis=1, level=-1)
    new_tuples = (i for items in zip(df.columns, percs.columns) for i in items)
    columns = pd.MultiIndex.from_tuples(new_tuples)
    return df.join(percs)[columns]


def transform(
    df: pd.DataFrame,
    axis: AxisAlias = 0,
    level: LevelAlias = 0,
    totals_name: IndexName = TOTALS_NAME,
    ndigits: int = NDIGITS,
) -> pd.DataFrame:
    axis = get_axis_number(axis)
    if axis == 0:
        return row_wise(
            df,
            level=level,
            totals_name=totals_name,
            ndigits=ndigits)
    elif axis == 1:
        return col_wise(
            df,
            level=level,
            totals_name=totals_name,
            ndigits=ndigits)
    else:
        pass


@copy
@log.entry
def col_wise(
    df,
    level=0,
    totals_name=TOTALS_NAME,
    ndigits=NDIGITS,
):
    if isinstance(df.index, pd.MultiIndex):
        totals = (df.xs(totals_name, level=level, axis=1, drop_level=False)
            .reindex(df.columns, axis=1)
            .bfill(axis=1))
    else:
        totals = df.loc[totals_name]
    return (df.div(totals).multiply(100).round(ndigits))


@copy
@log.entry
def row_wise(
    df,
    level=0,
    totals_name=TOTALS_NAME,
    ndigits=NDIGITS,
):
    if isinstance(df.index, pd.MultiIndex):
        totals = (df.xs(totals_name, level=level, axis=0, drop_level=False)
            .reindex(df.index, axis=0)
            .bfill())
    else:
        totals = df.loc[totals_name]
    return (df.div(totals).multiply(100).round(ndigits))
