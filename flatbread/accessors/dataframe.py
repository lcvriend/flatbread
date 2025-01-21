from typing import Any, Callable

import pandas as pd

import flatbread.percentages as pct
import flatbread.agg.aggregation as agg
import flatbread.agg.totals as tot
import flatbread.tooling as tool
from flatbread.render.display import PitaDisplayMixin


@pd.api.extensions.register_dataframe_accessor("pita")
class PitaFrame(PitaDisplayMixin):
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    #region aggregation
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
        level: int|str|list[int|str] = 0,
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
            level = level,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )

    #region percentages
    def as_percentages(
        self,
        axis: int = 2,
        label_totals: str|None = None,
        ignore_keys: str|list[str]|None = None,
        ndigits: int|None = None,
        base: int = 1,
        apportioned_rounding: bool = True,
    ) -> pd.DataFrame:
        """
        Transform data to percentages based on specified axis.

        Parameters
        ----------
        data (pd.DataFrame):
            The input DataFrame.
        axis (int):
            The axis along which percentages are calculated. Percentages are based on:
            - when axis is 2 then grand total
            - when axis is 1 then column totals
            - when axis is 0 then row totals
            Default is 2.
        label_totals (str|None):
            Label of the totals column/row. If no label is supplied then totals will be assumed to be either the last row, last column or last row/column field. Default is None.
        ignore_keys (str|list[str]|None):
            Keys of rows/columns to ignore when calculating percentages.
        ndigits (int):
            Number of decimal places to round the percentages. Default is -1 (no rounding).
        base (int):
            The whole quantity against which to calculate the fraction.

        Returns
        -------
        pd.DataFrame:
            DataFrame with data transformed to percentages.
        """
        return pct.as_percentages(
            self._obj,
            axis = axis,
            label_totals = label_totals,
            ignore_keys = ignore_keys,
            ndigits = ndigits,
            base = base,
            apportioned_rounding = apportioned_rounding,
        )

    def as_pct(self, *args, **kwargs):
        return self.as_percentages(*args, **kwargs)

    def add_percentages(
        self,
        axis: int = 2,
        label_n: str|None = None,
        label_pct: str|None = None,
        label_totals: str|None = None,
        ignore_keys: str|list[str]|None = None,
        ndigits: int|None = None,
        base: int = 1,
        apportioned_rounding: bool = True,
        interleaf: bool = False,
    ) -> pd.DataFrame:
        """
        Add percentage columns to a DataFrame based on specified axis.

        Parameters
        ----------
        data (pd.DataFrame):
            The input DataFrame.
        axis (int):
            The axis along which percentages are calculated. Percentages are based on:
            - when axis is 2 then grand total
            - when axis is 1 then row totals
            - when axis is 0 then column totals
            Default is 2.
        label_n (str):
            Label for the original count columns. Default is 'n'.
        label_pct (str):
            Label for the percentage columns. Default is 'pct'.
        label_totals (str|None):
            Label of the totals column/row. If no label is supplied then totals will be assumed to be either the last row, last column or last row/column field. Default is None.
        ignore_keys (str|list[str]|None):
            Keys of rows/columns to ignore when calculating percentages.
        ndigits (int):
            Number of decimal places to round the percentages. Default is -1 (no rounding).
        base (int):
            The whole quantity against which to calculate the fraction.
        interleaf (bool):
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
            ignore_keys = ignore_keys,
            ndigits = ndigits,
            base = base,
            apportioned_rounding = apportioned_rounding,
            interleaf = interleaf,
        )

    def add_pct(self, *args, **kwargs):
        return self.add_percentages(*args, **kwargs)

    #region totals
    def add_totals(
        self,
        axis: int = 2,
        label: str|None = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
    ) -> pd.DataFrame:
        """
        Add totals to df.

        Parameters
        ----------
        axis (int):
            Axis to sum. If axis == 2 then add totals to both rows and columns. Default 2.
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
        axis: int = 2,
        level: int|str|list[int|str] = 0,
        label: str|None = None,
        ignore_keys: str|list[str]|None = None,
        _fill: str = '',
    ) -> pd.DataFrame:
        """
        Add subtotals to df.

        Parameters
        ----------
        axis (int):
            Axis to sum. If axis == 2 then add totals to both rows and columns. Default 2.
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
            level = level,
            label = label,
            ignore_keys = ignore_keys,
            _fill = _fill,
        )

    def sort_totals(
        self,
        axis: int = 0,
        level: int = 0,
        **kwargs
    ):
        return tool.sort_totals(
            self._obj,
            axis = axis,
            level = level,
            **kwargs,
        )

    def drop_totals(
        self
    ):
        return tot.drop_totals(self._obj)

    # region tooling
    def add_level(
        self,
        value: Any,
        level: int = 0,
        level_name: Any = None,
        axis: int = 0,
    ):
        """
        Add a level containing the specified value to a DataFrame axis.

        Parameters
        ----------
        data (pd.DataFrame):
            Input DataFrame.
        value (Any):
            Value to fill the new level with.
        level (int, optional):
            Position to insert the new level. Defaults to 0 (start).
        level_name (Any, optional):
            Name for the new level. Defaults to None.
        axis (Axis):
            Axis to modify (0 for index, 1 for columns). Defaults to 0.

        Returns
        -------
        pd.DataFrame:
            DataFrame with the new level added to the specified axis.
        """
        return tool.add_level(
            self._obj,
            value = value,
            level = level,
            level_name = level_name,
            axis = axis,
        )
