import pandas as pd
# from pandas.core.computation.scope import ensure_scope
from flatbread.core import copy
from flatbread.utils import log
import inspect


@copy
@log.entry
def values(
    df,
    values,
    column,
    criteria=None,
    **kwargs,
):
    """
    Assign `values` to `column` in `df` if row meets `criteria`.

    Parameters
    ==========
    df : DataFrame
        Designated DataFrame.
    values : scalar, Series
        Value(s) to apply to `column`.
    column :
        Column name.
    criteria : str, optional
        The query string to evaluate.
    **kwargs
    """

    if criteria is None:
        df[column] = values
    else:
        df.loc[df.eval(criteria, level=3, **kwargs), column] = values
    return df


@copy
@log.entry
def calculated_values(
    df,
    values,
    column,
    criteria=None,
    **kwargs,
):

    values = df.eval(values, level=3, **kwargs)
    if criteria is None:
        df[column] = values
    else:
        df.loc[df.eval(criteria, level=2, **kwargs), column] = values
    return df
