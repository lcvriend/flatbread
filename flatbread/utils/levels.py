import pandas as pd
from flatbread.utils.types import LevelAlias, AxisAlias, IndexName


def get_level_number(
    df: pd.DataFrame,
    axis: int,
    level: LevelAlias,
) -> int:

    "Return level as int from `axis` of `df` by `level`."

    if axis == 1:
        index = df.T.index
    else:
        index = df.index

    level = get_level_from_alias(index, level)
    validate_level(index, level)
    level = get_absolute_level(index, level)
    return level


def get_level_from_alias(
    index: pd.Index,
    level: LevelAlias
) -> int:

    "Find level corresponding to `level` in `index`."

    if level in index.names:
        level = index.names.index(level)

    # validation
    if not isinstance(level, int):
        raise KeyError(
            f"Level '{level}' was not found in index."
        )
    return level


def get_absolute_level(
    index: pd.MultiIndex,
    level: int
) -> int:

    "Return `level` as absolute."

    if level < 0:
        level = index.nlevels + level
    return level


def validate_level(
    index: pd.Index,
    level: int
) -> None:

    """Validate `level`.

    Raises exception if:
    - `level` <= nlevels
    """

    if abs(level) > index.nlevels:
        raise IndexError(
            f"Level {level} is out of range for index."
        )
    return None


def validate_index_for_within_operations(
    index: pd.MultiIndex,
    level: int
) -> None:

    """Validate `index` for <within> operations.

    Raises exception if:
    - `index` is not a MultiIndex.
    - `level` is not > 0.
    """

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
