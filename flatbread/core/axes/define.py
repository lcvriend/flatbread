from decimal import Decimal
import pandas as pd
from flatbread.core import copy


@copy
def rename(df, mapper, axis=0, level=0):
    "Rename index on `axis` and `level` according to `mapper` in `df`."

    return df.rename(mapper, axis=axis, level=level)


@copy
def add_idx_level(df, level_name, axis=0, level=-1):
    "Add `level` with `level_name` to index on `axis` in `df`."

    if axis == 0:
        return add_idx_level_row_wise(df, level_name, level=level)
    elif axis == 1:
        return add_idx_level_col_wise(df, level_name, level=level)
    else:
        pass


@copy
def add_idx_level_col_wise(df, level_name, level=-1):
    cols = (add_item_to_key(key, level_name, level) for key in df.columns)
    df.columns = pd.MultiIndex.from_tuples(cols)
    return df


@copy
def add_idx_level_row_wise(df, level_name, level=-1):
    df = df.T
    df = add_idx_level_col_wise(df, level_name, level=level)
    return df.T


def add_category(index, category, level=0):
    "Add `category` to categorical `index` at specified `level`."

    def add_cat(index, category):
        if isinstance(index, pd.CategoricalIndex):
            category = [item for item in category if item not in list(index.categories)]
            index = index.add_categories(category)
        return index

    if isinstance(category, str):
        category = [category]

    if isinstance(index, pd.MultiIndex):
        index = index.set_levels(
            add_cat(index.levels[level], category),
            level=level)
    else:
        index = add_cat(index, category)
    return index


def add_item_to_key(key, item, level=0):
    "Insert `item` into `key` at a specified `level`."

    key = key_to_list(key)
    if level < 0:
        key.append(item)
    else:
        key.insert(level, item)
    return tuple(key)


def replace_item_in_key(key, item, level=0):
    "Replace item in `key` at `level` with `item`."

    key = key_to_list(key)
    key[level] = item
    return tuple(key)


def key_to_list(key):
    "Convert `key` to list."

    if isinstance(key, (str, int, float, Decimal)):
        return [key]
    else:
        return list(key)


def order_categories(s, categories):
    "Order series `s` according to order in `categories`."

    return pd.Categorical(s, categories, ordered=True)
