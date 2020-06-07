from flatbread.utils import log
from flatbread.core import copy


@copy
@log.entry
def columns(df, columns):
    "Drop `columns` from `df`."

    return df.drop(columns, axis=1)


@copy
@log.entry
def rows(df, rows):
    "Drop `rows` from `df`."

    return df.drop(rows)


@copy
@log.entry
def duplicates(df, **kwargs):
    "Drop `duplicates` from `df`."

    return df.drop_duplicates(**kwargs)
