from functools import singledispatch
from typing import Callable, Literal, TypeAlias

import pandas as pd


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


@singledispatch
def add_percentages(
    data,
    label: str = 'pct',
    ndigits: int = -1,
):
    raise NotImplementedError('No implementation for this type')


@add_percentages.register
def _(
    data: pd.Series,
    label_n: str = 'n',
    label_pct: str = 'pct',
    ndigits: int = -1,
) -> pd.DataFrame:
    total = data.iloc[-1]
    pcts = (
        data
        .div(total)
        .mul(100)
        .pipe(round_percentages, ndigits=ndigits)
    )
    return pd.concat([data, pcts], keys=[label_n, label_pct], axis=1)


@add_percentages.register
def _(
    data: pd.DataFrame,
    axis: int = 2,
    label_n: str = 'n',
    label_pct: str = 'pct',
    ndigits: int = -1,
) -> pd.DataFrame:
    if axis == 2:
        totals = data.iloc[-1, -1]
    elif axis == 1:
        totals = data.iloc[-1, :]
    else:
        totals = data.iloc[:, -1]
    axis = axis if axis < 2 else None
    pcts = (
        data
        .div(totals, axis=axis)
        .mul(100)
        .pipe(round_percentages, ndigits=ndigits)
    )
    return pd.concat([data, pcts], keys=[label_n, label_pct], axis=1)


def round_percentages(
    s: pd.Series,
    ndigits: int = -1
) -> pd.Series:
    """
    Round percentages in a way that they always add up to 100%.
    Taken from `this SO answer <https://stackoverflow.com/a/13483486/10403856>`_
    """
    if ndigits < 0:
        return s
    cumsum = s.fillna(0).cumsum().round(ndigits)
    prev_baseline = cumsum.shift(1).fillna(0)
    return cumsum - prev_baseline
