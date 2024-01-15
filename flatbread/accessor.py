from typing import Callable

import pandas as pd

import flatbread.percentages as pct
import flatbread.agg.aggregation as agg
import flatbread.agg.totals as tot


@pd.api.extensions.register_dataframe_accessor("pita")
class PitaFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def add_agg(
        self,
        aggfunc: str|Callable,
        *args,
        axis: int = 0,
        label: str = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
        **kwargs,
    ) -> pd.DataFrame:
        """
        Add aggregation to df.

        Parameters
        ----------
        aggfunc (str|Callable):
            Function to use for aggregating the data.
        axis (int):
            Axis to aggregate. Default 0.
        label (str|None):
            Label for the aggregation row/column. Default None.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating.
        *args:
            Positional arguments to pass to func.
        **kwargs:
            Keyword arguments to pass to func.

        Returns
        -------
        pd.DataFrame:
            Table with aggregated rows/columns added.
        """
        return agg.add_agg(
            self._obj,
            aggfunc,
            *args,
            axis = axis,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
            **kwargs,
        )

    def add_subagg(
        self,
        aggfunc: str|Callable,
        axis: int = 0,
        levels: int|str|list[int|str] = 0,
        label: str = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
    ) -> pd.DataFrame:
        """
        Add aggregation to specified levels of the df.

        Parameters
        ----------
        aggfunc (str|Callable):
            Function to use for aggregating the data.
        axis (int):
            Axis to aggregate. Default 0.
        levels (int|str|list[int|str]):
            Levels to aggregate. Default 0.
        label (str|None):
            Label for the aggregation row/column. Default None.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating.
        *args:
            Positional arguments to pass to func.
        **kwargs:
            Keyword arguments to pass to func.

        Returns
        -------
        pd.DataFrame:
            Table with aggregated rows/columns added.
        """
        return agg.add_agg(
            self._obj,
            aggfunc,
            axis = axis,
            levels = levels,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )

    def add_percentages(
        self,
        axis: int = 2,
        label_n: str = 'n',
        label_pct: str = 'pct',
        label_totals: str|None = None,
        ndigits: int = -1,
        interleaf: bool = False,
    ) -> pd.DataFrame:
        """
        Add percentage columns to a DataFrame based on specified axis.

        Parameters
        ----------
        - data (pd.DataFrame):
            The input DataFrame.
        - axis (int):
            The axis along which percentages are calculated. Percentages are based on:
            - when axis is 2 then grand total
            - when axis is 1 then column totals
            - when axis is 0 then row totals
            Default is 2.
        - label_n (str):
            Label for the original count columns. Default is 'n'.
        - label_pct (str):
            Label for the percentage columns. Default is 'pct'.
        - label_totals (str|None):
            Label of the totals column/row. If no label is supplied then totals will be assumed to be either the last row, last column or last row/column field. Default is None.
        - ndigits (int):
            Number of decimal places to round the percentages. Default is -1 (no rounding).
        - interleaf (bool):
            If `interleaf` is True then percentages columns will be placed next to count columns. If set to False the percentages columns will have their own separate block in the table. Default is False.

        Returns
        -------
        pd.DataFrame:
            DataFrame with additional columns for percentages.
        """
        return pct.add_percentages(
            self._obj,
            axis = axis,
            label_n = label_n,
            label_pct = label_pct,
            label_totals = label_totals,
            ndigits = ndigits,
            interleaf = interleaf,
        )

    def add_totals(
        self,
        axis: int = 0,
        label: str|None = 'Totals',
        ignore_keys: str|list[str]|None = 'Subtotals',
        _fill: str = '',
    ) -> pd.DataFrame:
        """
        Add totals to df.

        Parameters
        ----------
        axis (int):
            Axis to sum. If axis == 2 then add totals to both rows and columns. Default 0.
        label (str|None):
            Label for the totals row/column. Default 'Totals'.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating. Default 'Subtotals'

        Returns
        -------
        pd.DataFrame:
            Table with total rows/columns added.
        """
        return tot.add_totals(
            self._obj,
            axis = axis,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )

    def add_subtotals(
        self,
        axis: int = 0,
        levels: int|str|list[int|str] = 0,
        label: str|None = 'Subtotals',
        ignore_keys: str|list[str]|None = 'Totals',
        _fill: str = '',
    ) -> pd.DataFrame:
        """
        Add subtotals to df.

        Parameters
        ----------
        axis (int):
            Axis to sum. If axis == 2 then add totals to both rows and columns. Default 0.
        levels (int|str|list[int|str]):
            Levels to sum with func. Default 0.
        label (str|None):
            Label for the subtotals row/column. Default 'Subtotals'.
        ignore_keys (str|list[str]|None):
            Keys of rows to ignore when aggregating. Default 'Totals'

        Returns
        -------
        pd.DataFrame:
            Table with total rows/columns added.
        """
        return tot.add_subtotals(
            self._obj,
            axis = axis,
            levels = levels,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )


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

    def add_percentages(
        self,
        label_n: str = 'n',
        label_pct: str = 'pct',
        label_totals: str|None = None,
        ndigits: int = -1,
    ) -> pd.DataFrame:
        """
        Add percentage column to a Series.

        Parameters
        ----------
        - data (pd.Series):
            The input Series.
        - label_n (str):
            Label for the original count column. Default is 'n'.
        - label_pct (str):
            Label for the percentage column. Default is 'pct'.
        - label_totals (str|None):
            Label of the totals row. If no label is supplied then totals will be assumed to be the last row. Default is None.
        - ndigits (int):
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
        label: str|None = 'Totals',
        ignore_keys: str|list[str]|None = 'Subtotals',
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
        label: str|None = 'Subtotals',
        ignore_keys: str|list[str]|None = 'Totals',
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
