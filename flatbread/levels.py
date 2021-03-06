"""
Helper functions for dealing with DataFrame levels.
"""

from functools import wraps, partial
from typing import Any, Callable, TypeVar, Union, cast

import pandas as pd # type: ignore
from pandas._libs.lib import is_scalar

import flatbread.axes as axes
import flatbread.utils as utils


F = TypeVar('F', bound=Callable[..., Any])


def get_level_number(func: F) -> F:
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        level = kwargs.get('level') or 0
        axis = kwargs.get('axis') or 0
        kwargs['level'] = _get_level_number(df, axis, level)
        return func(df, *args, **kwargs)
    return cast(F, wrapper)


def _get_level_number(
    df: pd.DataFrame,
    axis: int,
    level: Union[str, int],
) -> int:
    "Return level as int from ``axis`` of ``df`` by ``level``."
    if axis == 1:
        index = df.T.index
    else:
        index = df.index

    if not isinstance(level, int):
        level = _get_level_from_name(index, level)
    _validate_level(index, level)
    level = _get_absolute_level(index, level)
    return level


def validate_index_for_within_operations(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        df, *_ = args
        _validate_index_for_within_operations(df, kwargs['level'])
        return func(*args, **kwargs)
    return wrapper


def _validate_index_for_within_operations(
    df: pd.DataFrame,
    level: int
) -> None:
    """Validate ``index`` for <within> operations.

    Raises exception if:
    - ``index`` is not a MultiIndex.
    - ``level`` is not > 0.
    """
    index = df.index
    if index.nlevels == 1:
        raise ValueError(
            "Operation can only be performed on index with multiple levels."
        )
    if level == 0:
        raise ValueError(
            "Operation can only be performed on inner level of index."
        )
    if level >= index.nlevels:
        raise IndexError(
            f"Level {level} is out of range for index."
        )
    return None


def _get_level_from_name(
    index: pd.Index,
    level_name: Any
) -> int:
    "Find level corresponding to ``level_name`` in ``index``."
    if not level_name in index.names:
        raise KeyError(
            f"Level '{level_name}' was not found in index."
        )
    return index.names.index(level_name)


def _get_absolute_level(
    index: pd.MultiIndex,
    level: int
) -> int:
    "Return ``level`` as absolute."
    if level < 0:
        level = index.nlevels + level
    return level


def _validate_level(
    index: pd.Index,
    level: int
) -> None:
    """Validate ``level``.

    Raise exception if:
    - ``level`` <= nlevels
    """
    if abs(level) > index.nlevels:
        raise IndexError(
            f"Level {level} is out of range for index."
        )
    return None


def get_axlevels(df, axis, level=None):
    """
    Return tuple of levels. First element maps to rows, second to columns.
    Both axis and levels are converted to their number(s). It is also possible
    to pass ``axis`` a tuple directly. In this case ``level`` will be ignored.

    Arguments
    ---------
    axis : scalar, sequence of scalars, tuple of levels
    level : scalar, sequence of scalars

    Returns
    -------
    tuple
        Tuple mapping levels to axes.
    """
    get_level = partial(_get_level_number, df)
    level = utils.listify(level)
    if isinstance(axis, (int, str)):
        axis = axes._get_axis_number(axis)
        if axis == 0:
            level = [get_level(0, item) for item in level]
            return (level, [])
        elif axis == 1:
            level = [get_level(1, item) for item in level]
            return ([], level)
        else:
            row_level = [get_level(0, item) for item in level]
            col_level = [get_level(1, item) for item in level]
            return [row_level, col_level]
    else:
        axlevels = [utils.listify(item) for item in utils.listify(axis)]
        return (
            [get_level(0, item) for item in axlevels[0]],
            [get_level(1, item) for item in axlevels[1]],
        )
