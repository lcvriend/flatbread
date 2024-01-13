from functools import singledispatch

import pandas as pd

import flatbread.agg.aggregation as agg


# TOTALS

@singledispatch
def add_totals(
    data,
    label: str = 'Totals',
    ignore_keys: str|list[str]|None = 'Subtotals',
    _fill: str|None = '',
):
    raise NotImplementedError('No implementation for this type')


@add_totals.register
def _(
    data: pd.Series,
    label: str = 'Totals',
    ignore_keys: str|list[str]|None = 'Subtotals',
    _fill: str|None = '',
) -> pd.Series:
    output = agg.add_agg(
        data,
        'sum',
        label = label,
        ignore_keys = ignore_keys,
        _fill = _fill,
    )
    return output


@add_totals.register
def _(
    data: pd.DataFrame,
    axis: int = 0,
    label: str = 'Totals',
    ignore_keys: str|list[str]|None = 'Subtotals',
    _fill: str|None = '',
) -> pd.DataFrame:
    if axis < 2:
        output = agg.add_agg(
            data,
            'sum',
            axis = axis,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill
        )
    else:
        output = (
            data
            .pipe(
                add_totals,
                axis = 0,
                label = label,
                ignore_keys = ignore_keys,
                _fill = _fill,
            )
            .pipe(
                add_totals,
                axis = 1,
                label = label,
                ignore_keys = ignore_keys,
                _fill = _fill,
            )
        )
    return output


# SUBTOTALS

@singledispatch
def add_subtotals(
    data,
    label: str = 'Subtotals',
    levels: int|str|list[int|str] = 0,
    ignore_keys: str|list[str]|None = 'Totals',
):
    raise NotImplementedError('No implementation for this type')


@add_subtotals.register
def _(
    data: pd.DataFrame,
    axis: int = 0,
    levels: int|str|list[int|str] = 0,
    label: str = 'Subtotals',
    ignore_keys: str|list[str]|None = 'Totals',
    _fill: str = '',
) -> pd.DataFrame:
    if axis < 2:
        output = agg.add_subagg(
            data,
            'sum',
            axis = axis,
            levels = levels,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )
    else:
        output = (
            data
            .pipe(
                add_subtotals,
                axis = 0,
                levels = levels,
                label = label,
                ignore_keys = ignore_keys,
                _fill = _fill,
            )
            .pipe(
                add_subtotals,
                axis = 1,
                levels = levels,
                label = label,
                ignore_keys = ignore_keys,
                _fill = _fill,
            )
        )
    return output
