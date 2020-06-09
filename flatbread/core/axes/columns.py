from flatbread.core.select import columns as select_columns
from flatbread.core.axes import define
from flatbread.core.aggregation import totals


def select(df, columns):
    return select_columns(df, columns)


def normalize(df, func=None):
    def normalize_name(col):
        return col.lower().replace(' ', '_')
    if func is None:
        func = normalize_name
    df.columns = [func(col) for col in df.columns]
    return df


def rename(df, mapper, level=0):
    return define.rename(df, mapper, axis=1, level=level)


def order(df, column, categories):
    df = df.copy()
    df[column] = define.order_categories(df[column], categories)
    return df


def add_level(df, level_name, level):
    return define.add_idx_level(
        df, level_name,
        axis=1,
        level=level
    )


def totals(df, level=0):
    return totals.add(df, axis=1, level=level, **kwargs)
