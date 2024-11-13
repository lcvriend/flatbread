from functools import singledispatch
from typing import Literal, TypeAlias
import warnings

import pandas as pd

from flatbread import DEFAULTS, chaining, config


Axis: TypeAlias = Literal[0, 1, 2, 'index', 'columns', 'both']


def get_totals(data, axis, label_totals):
    if label_totals is None:
        if axis == 0:
            return data.iloc[:, -1]
        elif axis == 1:
            return data.iloc[-1, :]
        else:
            return data.iloc[-1, -1]

    # if label_totals is given:
    if axis == 0:
        return data.loc[:, label_totals]
    elif axis == 1:
        return data.loc[label_totals, :]
    else:
        return data.loc[label_totals, label_totals]


@singledispatch
def as_percentages(
    data,
    *args,
    label_pct: str = 'pct',
    ndigits: int = -1,
    base: int = 1,
    apportioned_rounding: bool = True,
    **kwargs,
):
    raise NotImplementedError('No implementation for this type')


@as_percentages.register
@config.inject_defaults(DEFAULTS['percentages'])
def _(
    data: pd.Series,
    *,
    label_pct: str = 'pct',
    label_totals: str|None = None,
    ndigits: int = -1,
    base: int = 1,
    apportioned_rounding: bool = True,
    **kwargs,
) -> pd.Series:
    rounding = round_apportioned if apportioned_rounding else round
    total = data.iloc[-1] if label_totals is None else data.loc[label_totals]
    return (
        data
        .div(total)
        .mul(base)
        .pipe(rounding, ndigits=ndigits)
        .rename(label_pct)
    )


@as_percentages.register
@config.inject_defaults(DEFAULTS['percentages'])
@chaining.persist_ignored('percentages', 'label_pct')
def _(
    df: pd.DataFrame,
    axis: int = 2,
    *,
    label_totals: str|None = None,
    ignore_keys: str|list[str]|None = 'pct',
    ndigits: int = -1,
    base: int = 1,
    apportioned_rounding: bool = True,
    **kwargs,
) -> pd.DataFrame:
    # reverse axis for consistency
    rounding = round_apportioned if apportioned_rounding else round
    axis = 0 if axis == 1 else 1 if axis == 0 else None

    cols = chaining.get_data_mask(df.columns, ignore_keys)
    data = df.loc[:, cols]

    totals = get_totals(data, axis, label_totals)

    pcts = (
        data
        .div(totals, axis=axis)
        .mul(base)
        .pipe(rounding, ndigits=ndigits)
    )
    return pcts


@singledispatch
def add_percentages(
    data,
    *args,
    label_pct: str = 'pct',
    ndigits: int = -1,
    base: int = 1,
    apportioned_rounding: bool = True,
    **kwargs,
):
    raise NotImplementedError('No implementation for this type')


@add_percentages.register
@config.inject_defaults(DEFAULTS['percentages'])
def _(
    data: pd.Series,
    *,
    label_n: str = 'n',
    label_pct: str = 'pct',
    label_totals: str|None = None,
    ndigits: int = -1,
    base: int = 1,
    apportioned_rounding: bool = True,
    **kwargs,
) -> pd.DataFrame:
    pcts = data.pipe(
        as_percentages,
        label_pct = label_pct,
        label_totals = label_totals,
        ndigits = ndigits,
        base = base,
        apportioned_rounding = apportioned_rounding,
    )
    output = pd.concat([data, pcts], keys=[label_n, label_pct], axis=1)
    return output


@add_percentages.register
@config.inject_defaults(DEFAULTS['percentages'])
@chaining.persist_ignored('percentages', 'label_pct')
def _(
    df: pd.DataFrame,
    axis: int = 2,
    *,
    label_n: str = 'n',
    label_pct: str = 'pct',
    label_totals: str|None = None,
    ignore_keys: str|list[str]|None = 'pct',
    ndigits: int = -1,
    base: int = 1,
    apportioned_rounding: bool = True,
    interleaf: bool = False,
    **kwargs,
) -> pd.DataFrame:

    cols = chaining.get_data_mask(df.columns, ignore_keys)
    data = df.loc[:, cols]

    # totals = get_totals(data, axis, label_totals)
    # axis = axis if axis < 2 else None
    # pcts = (
    #     data
    #     .div(totals, axis=axis)
    #     .mul(100)
    #     .pipe(round_apportioned, ndigits=ndigits)
    # )
    pcts = data.pipe(
        as_percentages,
        axis = axis,
        label_totals = label_totals,
        ignore_keys = ignore_keys,
        ndigits = ndigits,
        base = base,
        apportioned_rounding = apportioned_rounding,
    )

    # check if there are already percentages in the table
    if cols.all():
        # if not then add them, original table gets `label_n`
        # percentages get `label_pct` as key
        keys = [label_n, label_pct]
        output = pd.concat([df, pcts], keys=keys, axis=1)
    else:
        # if percentages are present then transform them first
        # keys are already present in the original df
        # so we do not add new keys
        pcts = pcts.rename(columns={label_n: label_pct})
        output = pd.concat([df, pcts], axis=1)
    if interleaf:
        # return output.stack(0).unstack(-1)
        keys = [label_n, label_pct]
        return output.swaplevel(axis=1).sort_index(axis=1, level=0)
    return output


def round_apportioned(
    s: pd.Series,
    *,
    ndigits: int = -1
) -> pd.Series:
    """
    Round percentages in a way that they always add up to total.
    Taken from this SO answer:

    <https://stackoverflow.com/a/13483486/10403856>

    Parameters
    ----------
    s (pd.Series):
        A series of unrounded percentages adding up to total.
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
    rounded = cumsum - prev_baseline
    keep_na = rounded.mask(s.isna())
    return keep_na
