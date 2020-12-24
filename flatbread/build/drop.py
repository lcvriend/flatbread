from typing import Sequence

import pandas as pd # type: ignore

from flatbread.utils import log, copy
import flatbread.utils as utils
import flatbread.utils.log as log


@utils.copy
@log.entry
def columns(df: pd.DataFrame, columns: Sequence) -> pd.DataFrame:
    "Drop `columns` from `df`."

    return df.drop(columns, axis=1)


@utils.copy
@log.entry
def rows(df: pd.DataFrame, rows: Sequence) -> pd.DataFrame:
    "Drop `rows` from `df`."

    return df.drop(rows)


@utils.copy
@log.entry
def duplicates(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    "Drop `duplicates` from `df`."

    return df.drop_duplicates(**kwargs)
