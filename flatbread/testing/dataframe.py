from typing import Callable, Any

import pandas as pd

def make_test_df(
    nrows: int,
    ncols: int,
    data_gen_f: Callable[[int, int], Any] | None = None,
    idx_levels: int | None = None,
    col_levels: int | None = None,
    idx_prefix: str = "R",
    col_prefix: str = "C",
    idx_names: bool | list[str] | None = True,
    col_names: bool | list[str] | None = True,
    idx_dupes: list[int] | None = None,
    col_dupes: list[int] | None = None,
    dtype: Any = None
) -> pd.DataFrame:
    """
    Create a test DataFrame with custom data and multi-level indices.

    Parameters
    ----------
    nrows : int
        Number of rows
    ncols : int
        Number of columns
    data_gen_f : callable, optional
        Function that takes (row, col) indices and returns data.
        If None, generates labels like "R0C0", "R0C1", etc.
    idx_levels : int, optional
        Number of index levels. If None and idx_dupes is provided,
        will be derived from len(idx_dupes). Defaults to 1 if neither
        is provided.
    col_levels : int, optional
        Number of column levels. If None and col_dupes is provided,
        will be derived from len(col_dupes). Defaults to 1 if neither
        is provided.
    idx_prefix : str
        Prefix for index labels
    col_prefix : str
        Prefix for column labels
    idx_names : bool or list of str or None
        If True, uses default names (prefix + level number)
        If list, uses provided names
        If False/None, no names
    col_names : bool or list of str or None
        Same as idx_names but for columns
    idx_dupes : list of int, optional
        Number of times to duplicate each label at each level.
        If shorter than idx_levels, will be extended with 1s.
        If idx_levels is None, determines number of levels.
    col_dupes : list of int, optional
        Number of times to duplicate each label at each level.
        If shorter than col_levels, will be extended with 1s.
        If col_levels is None, determines number of levels.
    dtype : any, optional
        Data type for the DataFrame

    Returns
    -------
    pd.DataFrame
        Test DataFrame with specified structure

    Examples
    --------
    >>> # Basic usage
    >>> df = make_test_df(3, 2)

    >>> # Derive levels from duplicates
    >>> df = make_test_df(
    ...     nrows=4,
    ...     ncols=3,
    ...     idx_dupes=[2, 3],  # Creates 2 index levels
    ...     idx_names=['Year', 'Quarter']
    ... )

    >>> # Explicit levels with duplicates
    >>> df = make_test_df(
    ...     nrows=6,
    ...     ncols=4,
    ...     idx_levels=3,
    ...     idx_dupes=[2, 1],  # Will be extended to [2, 1, 1]
    ...     data_gen_f=lambda r, c: r * c
    ... )
    """
    def validate_level_inputs(levels, duplicates):
        # Derive or validate levels and duplicates
        if duplicates is not None and levels is None:
            levels = len(duplicates)
        elif levels is None:
            levels = 1
        elif duplicates is not None and len(duplicates) > levels:
            raise ValueError("duplicates cannot be longer than levels")

        # Normalize duplicates
        if duplicates is not None:
            duplicates = list(duplicates)
            duplicates.extend([1] * (levels - len(duplicates)))
        else:
            duplicates = [1] * levels
        return levels, duplicates

    idx_levels, idx_dupes = validate_level_inputs(idx_levels, idx_dupes)
    col_levels, col_dupes = validate_level_inputs(col_levels, col_dupes)

    # Handle default data generator
    if data_gen_f is None:
        data_gen_f = lambda r, c: f"{idx_prefix}{r}{col_prefix}{c}"

    # Generate data
    data = [[data_gen_f(r, c) for c in range(ncols)] for r in range(nrows)]

    def make_level_labels(
        n_items: int,
        n_levels: int,
        prefix: str,
        duplicates: list[int],
    ) -> list[list[str]]:
        labels = []
        for level in range(n_levels):
            if level == (n_levels - 1):
                level_labels = [f"{prefix.lower()}{j}" for j in range(n_items)]
            else:
                div_factor = n_items // duplicates[level] + 1
                level_labels = [
                    f"{prefix}_L{level}_G{j}"
                    for j in range(div_factor)
                    for _ in range(duplicates[level])
                ][:n_items]
            labels.append(level_labels)
        return labels

    def make_names(
        prefix: str,
        n_levels: int,
        names: bool | list[str] | None,
    ) -> list[str] | None:
        if names is True:
            return [f"{prefix}{i}" for i in range(n_levels)]
        elif isinstance(names, list):
            return names
        return None

    # Create indices
    idx_labels = make_level_labels(nrows, idx_levels, idx_prefix, idx_dupes)
    col_labels = make_level_labels(ncols, col_levels, col_prefix, col_dupes)

    idx_names = make_names(idx_prefix, idx_levels, idx_names)
    col_names = make_names(col_prefix, col_levels, col_names)

    # Create index/columns
    def make_index(n_levels, labels, names):
        if n_levels == 1:
            return pd.Index(labels[0], name=names[0] if names else None)
        else:
            return pd.MultiIndex.from_arrays(labels, names=names)

    index = make_index(idx_levels, idx_labels, idx_names)
    columns = make_index(col_levels, col_labels, col_names)

    return pd.DataFrame(data, index=index, columns=columns, dtype=dtype)
