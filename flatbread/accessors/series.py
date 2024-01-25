from typing import Callable

import pandas as pd

import flatbread.percentages as pct
import flatbread.agg.aggregation as agg
import flatbread.agg.totals as tot


@pd.api.extensions.register_series_accessor("pita")
class PitaSeries:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def add_agg(
        self,
        aggfunc: str|Callable,
        *args,
        label: str = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
        **kwargs,
    ) -> pd.Series:
        """
        Add aggregate to a Series.

        Parameters
        ----------
        aggfunc (str|Callable):
            Function to use for aggregating the data.
        label (str|None):
            Label for the aggregated row. Default None.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating.
        *args:
            Positional arguments to pass to func.
        **kwargs:
            Keyword arguments to pass to func.

        Returns
        -------
        pd.Series:
            Series with aggregated row added.
        """
        return agg.add_agg(
            self._obj,
            aggfunc,
            *args,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
            **kwargs,
        )

    def add_subagg(
        self,
        aggfunc: str|Callable,
        levels: int|str|list[int|str] = 0,
        label: str = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
    ) -> pd.Series:
        """
        Add aggregates of specified levels to a Series.

        Parameters
        ----------
        aggfunc (str|Callable):
            Function to use for aggregating the data.
        levels (int|str|list[int|str]):
            Levels to aggregate with func. Default 0.
        label (str|None):
            Label for the aggregated rows. Default None.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating.
        *args:
            Positional arguments to pass to func.
        **kwargs:
            Keyword arguments to pass to func.

        Returns
        -------
        pd.Series:
            Table with aggregated rows added.
        """
        return agg.add_agg(
            self._obj,
            aggfunc,
            levels = levels,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )

    def value_counts(
        self,
        fillna: str = '<NA>',
        label_n: str = 'count',
        add_pct: bool = False,
        label_pct: str = 'pct',
        ndigits: int = -1,
    )-> pd.Series|pd.DataFrame:
        """
        Similar to pandas `value_counts` except *null* values are by default also counted and a total is added. Optionally, percentages may also be added to the output.

        Parameters
        ----------
        fillna (str):
            What value to give *null* values. Set to None to not count null values. Default is '<NA>'.
        label_n (str):
            Name for the count column. Default is 'count'.
        add_pct (bool):
            Whether to add a percentage column. Default is False.
        label_pct (str):
            Name for the percentage column. Default is 'pct'.
        ndigits (int):
            Number of decimal places to round the percentages. Default is -1 (no rounding).

        Returns
        -------
        pd.Series:
            Series reporting the count of each value in the original series.
        """
        s = self._obj if fillna is None else self._obj.fillna(fillna)
        result = s.value_counts().rename(label_n).pipe(tot.add_totals)
        if add_pct:
            return result.pipe(
                pct.add_percentages,
                label_n = label_n,
                label_pct = label_pct,
                ndigits = ndigits,
            )
        return result

    def as_percentages(
        self,
        label_pct: str = None,
        label_totals: str|None = None,
        ndigits: int = None,
    ) -> pd.Series:
        """
        Transform data into percentages.

        Parameters
        ----------
        data (pd.Series):
            The input Series.
        label_pct (str):
            Label for the percentage column. Default is 'pct'.
        label_totals (str|None):
            Label of the totals row. If no label is supplied then totals will be assumed to be the last row. Default is None.
        ndigits (int):
            Number of decimal places to round the percentages. Default is -1 (no rounding).

        Returns
        -------
        pd.Series:
            Series transformed into percentages.
        """
        return pct.as_percentages(
            self._obj,
            label_pct = label_pct,
            label_totals = label_totals,
            ndigits = ndigits,
        )

    def add_percentages(
        self,
        label_n: str|None = None,
        label_pct: str|None = None,
        label_totals: str|None = None,
        ndigits: int|None = None,
    ) -> pd.DataFrame:
        """
        Add percentage column to a Series.

        Parameters
        ----------
        data (pd.Series):
            The input Series.
        label_n (str):
            Label for the original count column. Default is 'n'.
        label_pct (str):
            Label for the percentage column. Default is 'pct'.
        label_totals (str|None):
            Label of the totals row. If no label is supplied then totals will be assumed to be the last row. Default is None.
        ndigits (int):
            Number of decimal places to round the percentages. Default is -1 (no rounding).

        Returns
        -------
        pd.DataFrame:
            DataFrame with the original Series and an additional column for the percentages.
        """
        return pct.add_percentages(
            self._obj,
            label_n = label_n,
            label_pct = label_pct,
            label_totals = label_totals,
            ndigits = ndigits,
        )

    def add_totals(
        self,
        label: str|None = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
    ) -> pd.Series:
        """
        Add totals to a Series.

        Parameters
        ----------
        label (str|None):
            Label for the totals row. Default 'Totals'.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating. Default 'Subtotals'

        Returns
        -------
        pd.Series:
            Series with totals row added.
        """
        return tot.add_totals(
            self._obj,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )

    def add_subtotals(
        self,
        levels: int|str|list[int|str] = 0,
        label: str|None = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
    ) -> pd.Series:
        """
        Add subtotals to a Series.

        Parameters
        ----------
        levels (int|str|list[int|str]):
            Levels to add subtotals to. Default 0.
        label (str|None):
            Label for the subtotals rows. Default 'Subtotals'.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating. Default 'Totals'

        Returns
        -------
        pd.Series:
            Series with subtotal rows added.
        """
        return tot.add_subtotals(
            self._obj,
            levels = levels,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )