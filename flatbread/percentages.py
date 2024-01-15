from functools import singledispatch
from typing import Callable, Literal, TypeAlias

import pandas as pd


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


def get_totals(data, axis, label_totals):
    if label_totals is None:
        if axis == 2:
            return data.iloc[-1, -1]
        elif axis == 1:
            return data.iloc[-1, :]
        else:
            return data.iloc[:, -1]

    # if label_totals is given:
    if axis == 2:
        return data.loc[label_totals, label_totals]
    elif axis == 1:
        return data.loc[label_totals, :]
    else:
        return data.loc[:, label_totals]


@singledispatch
def add_percentages(
    data,
    *args,
    label_pct: str = 'pct',
    ndigits: int = -1,
    **kwargs,
):
    raise NotImplementedError('No implementation for this type')


@add_percentages.register
def _(
    data: pd.Series,
    label_n: str = 'n',
    label_pct: str = 'pct',
    label_totals: str|None = None,
    ndigits: int = -1,
) -> pd.DataFrame:
    total = data.iloc[-1] if label_totals is None else data.loc[label_totals]
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
    label_totals: str|None = None,
    ndigits: int = -1,
    interleaf: bool = False,
) -> pd.DataFrame:
    totals = get_totals(data, axis, label_totals)
    axis = axis if axis < 2 else None
    pcts = (
        data
        .div(totals, axis=axis)
        .mul(100)
        .pipe(round_percentages, ndigits=ndigits)
    )
    output = pd.concat([data, pcts], keys=[label_n, label_pct], axis=1)
    if interleaf:
        return output.stack(0).unstack(-1)
    return output


def round_percentages(
    s: pd.Series,
    ndigits: int = -1
) -> pd.Series:
    """
    Round percentages in a way that they always add up to 100%.
    Taken from this SO answer:

    <https://stackoverflow.com/a/13483486/10403856>

    Parameters
    ----------
    s (pd.Series):
        A series of unrounded percentages adding up to 100%.
    ndigits (int):
        Number of digits to round percentages to. Default is -1 (no rounding).

    Returns
    -------
    pd.Series:
        Rounded percentages.
    """
    if ndigits < 0:
        return s
    cumsum = s.fillna(0).cumsum().round(ndigits)
    prev_baseline = cumsum.shift(1).fillna(0)
    return cumsum - prev_baseline
