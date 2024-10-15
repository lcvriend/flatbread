import functools
from typing import Callable

import pandas as pd


def get_data_mask(index, ignore_keys):
    """
    Create a mask used for separating data from results of flatbread operations. The keys in `ignore_keys` determine which rows/columns need to be ignored. This can be used when chaining multiple flatbread operations.

    Parameters
    ----------
    index (pd.Index):
        The index used for determining if a row/column contains data or not.
    ignore_keys (list[str]):
        List of index keys indicating that a row/column is *not* a data column. If the index is a MultiIndex then a row/column will be ignored if the key is in the keys of the index, else a row/column will be ignored if it is equal to the key in the index.

    Returns
    -------
    pd.Index:
        Boolean index indicating which rows/columns refer to data.
    """
    if isinstance(index, pd.MultiIndex):
        ignored = index.map(lambda i: all(key not in i for key in ignore_keys))
    else:
        ignored = index.map(lambda i: all(key != i for key in ignore_keys))
    return ignored


def persist_ignored(component: str, label: str) -> Callable:
    """
    Remember the labels that need to be ignored when chaining operations. The `ignore_keys` are stored in `df.attrs` in a set.

    Parameters
    ----------
    component (str):
        Key (used in `df.attrs`) referring to the flatbread component to store the `ignore_keys` for, i.e. "totals" or "percentages".
    label (str):
        The label that needs to be added to the `ignore_keys` during chained flatbread operations.

    Returns
    -------
    func:
        A func operating on a df that stores `ignore_keys` in the `df.attrs`.

    Notes
     ----
    The `df.attrs` are currently not retained throughout all pandas operations.

    Example of how ignored keys are stored in attrs:
    ```python
    {'flatbread': {
        'totals': {'ignore_keys': {'Subtotals', 'Totals'}},
        'percentages': {'ignore_keys': {'pct'}}
    }}
    ```
    """
    def get_ignored_keys(ignore_keys, label):
        if ignore_keys is None:
            return [label]
        elif isinstance(ignore_keys, str):
            return [label, ignore_keys]
        return [label, *ignore_keys]

    def set_nested_key(data, keys, value):
        if len(keys) == 1:
            data[keys[0]] = value
        else:
            key = keys[0]
            if key not in data:
                data[key] = {}
            set_nested_key(data[key], keys[1:], value)

    def get_nested_key(data, keys):
        for key in keys:
            if key in data:
                data = data[key]
            else:
                return set()
        return data

    keys = ['flatbread', component, 'ignore_keys']
    def decorator(func):
        @functools.wraps(func)
        def wrapper(df, *args, **kwargs):
            persisted_ignore_keys = get_nested_key(df.attrs, keys)
            ignore_keys = kwargs.pop('ignore_keys', None)
            ignored_label = kwargs[label]
            ignored = get_ignored_keys(ignore_keys, ignored_label)
            all_ignored = persisted_ignore_keys.union(ignored)

            result = func(df, *args, ignore_keys=all_ignored, **kwargs)
            set_nested_key(result.attrs, keys, all_ignored)
            return result
        return wrapper
    return decorator
