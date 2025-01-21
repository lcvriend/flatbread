from functools import singledispatch

import pandas as pd

import flatbread.agg.aggregation as agg
from flatbread import chaining, config, DEFAULTS


# region TOTALS

@singledispatch
def add_totals(
    data,
    label: str = 'Totals',
    ignore_keys: str|list[str]|None = 'Subtotals',
    _fill: str|None = '',
):
    raise NotImplementedError('No implementation for this type')


@add_totals.register
@config.inject_defaults(DEFAULTS['totals'])
@chaining.persist_ignored('totals', 'label')
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
@config.inject_defaults(DEFAULTS['totals'])
@chaining.persist_ignored('totals', 'label')
def _(
    data: pd.DataFrame,
    axis: int = 2,
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


# region SUBTOTALS

@singledispatch
def add_subtotals(
    data,
    label: str = 'Subtotals',
    level: int|str|list[int|str] = 0,
    ignore_keys: str|list[str]|None = 'Totals',
):
    raise NotImplementedError('No implementation for this type')


@add_subtotals.register
@config.inject_defaults(DEFAULTS['subtotals'])
@chaining.persist_ignored('totals', 'label')
def _(
    data: pd.Series,
    level: int|str|list[int|str] = 0,
    label: str = 'Subtotals',
    ignore_keys: str|list[str]|None = 'Totals',
    _fill: str|None = '',
) -> pd.Series:
    output = agg.add_subagg(
        data,
        'sum',
        level = level,
        label = label,
        ignore_keys = ignore_keys,
        _fill = _fill,
    )
    return output


@add_subtotals.register
@config.inject_defaults(DEFAULTS['subtotals'])
@chaining.persist_ignored('totals', 'label')
def _(
    data: pd.DataFrame,
    axis: int = 0,
    level: int|str|list[int|str] = 0,
    label: str = 'Subtotals',
    ignore_keys: str|list[str]|None = 'Totals',
    _fill: str = '',
) -> pd.DataFrame:
    if axis < 2:
        output = agg.add_subagg(
            data,
            'sum',
            axis = axis,
            level = level,
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
                level = level,
                label = label,
                ignore_keys = ignore_keys,
                _fill = _fill,
            )
            .pipe(
                add_subtotals,
                axis = 1,
                level = level,
                label = label,
                ignore_keys = ignore_keys,
                _fill = _fill,
            )
        )
    return output


#region DROP TOTALS
def drop_totals(
    data: pd.DataFrame|pd.Series,
    ignore_keys: str|list[str]|None = None,
) -> pd.DataFrame|pd.Series:
    if ignore_keys is None:
        ignore_keys = data.attrs['flatbread']['totals']['ignore_keys']
    mask = chaining.get_data_mask(data.index, ignore_keys)
    return data.loc[mask].copy()
