from functools import partial

import pandas as pd
from pandas._libs import lib

from flatbread.aggregate import totals as aggtotals
from flatbread.aggregate import percentages as percs
from flatbread.build import columns as cols
from flatbread import axes
from flatbread import levels
from flatbread import style
from flatbread.config import HERE, load_settings


@pd.api.extensions.register_dataframe_accessor("pita")
class PivotTable:
    dtypes = {
        'count': 'Int64',
        'size':  'Int64',
    }

    @load_settings(['aggregation', 'na', 'format'])
    def __init__(
        self,
        pandas_obj,
        na             = None,
        na_cat         = None,
        na_position    = None,
        na_rep         = None,
        totals_name    = None,
        subtotals_name = None,
        label_abs      = None,
        label_rel      = None,
        ndigits        = None,
        percs_method   = None,
        **kwargs
    ):
        self._obj           = pandas_obj
        self._df            = pandas_obj
        self.pipeline       = list()
        self.index          = None
        self.columns        = None
        self.na             = na
        self.na_cat         = na_cat
        self.na_position    = na_position
        self.na_rep         = na_rep
        self.totals_name    = totals_name
        self.subtotals_name = subtotals_name
        self.label_abs      = label_abs
        self.label_rel      = label_rel
        self.ndigits        = ndigits
        self.percs_method   = percs_method

    def __call__(
        self,
        values     = None,
        index      = None,
        columns    = None,
        aggfunc    = None,
        fill_value = None,
        add_totals = False,
        axis       = 0,
        level      = 0,
        observed   = True,
        **kwargs
    ):
        """View DataFrame as a spreadsheet-style pivot table. Operations may be
        chained.

        Arguments
        ---------
        ### PIVOT_TABLE
        values : column to aggregate, optional
        index : column, Grouper, array, or list of the previous
            If an array is passed, it must be the same length as the data. The
            list can contain any of the other types (except list). Keys to
            group by on the pivot table index. If an array is passed, it is
            being used as the same manner as column values.
        columns : column, Grouper, array, or list of the previous
            If an array is passed, it must be the same length as the data. The
            list can contain any of the other types (except list). Keys to
            group by on the pivot table column. If an array is passed, it is
            being used as the same manner as column values.
        aggfunc : function, list of functions, dict, default size or count
            Contrary to `pivot_table` default behavior, `pita` will act as a
            crosstab. If no values are given, then `size` is used to aggregate
            otherwise `count`.
            If list of functions passed, the resulting pivot table will have
            hierarchical columns whose top level are the function names
            (inferred from the function objects themselves). If dict is passed,
            the key is column to aggregate and value is function or list of
            functions.
        fill_value : scalar, default None
            Value to replace missing values with (in the resulting pivot table,
            after aggregation).
        observed : bool, default False
            This only applies if any of the groupers are Categoricals. If True:
            only show observed values for categorical groupers. If False: show
            all values for categorical groupers.

        ### TOTALS
        add_totals : bool, default False
            Add (sub)totals to table
        axis : {0 or 'index', 1 or 'columns', 2 or 'all', None}, default 0
            Axis to add totals:
            0 : add row with column totals
            1 : add column with row totals
            2 : add row and column totals
            If None supply `level` with a tuple for each axis.
        level : int, level name, or sequence of such, tuple of levels, default 0
            Level number/name of the level to use for calculating the totals.
            Level 0 adds row/column totals, otherwise subtotals are added within
            the specified level. Multiple levels may be supplied in a list. If
        totals_name : str, default CONFIG.aggregation['totals_name']
            Name for the row/column totals.
        subtotals_name : str, default CONFIG.aggregation['subtotals_name']
            Name for the row/column subtotals.

        ### NA
        na : {'drop', 'keep', 'hide'}, default 'drop'
            How to handle records that do not fall into any category of a group:
            drop : exclude these records from the view completely
            keep : keep these records and assign them to a `na_cat` group
            hide : these records but hide them from output
            If keep/hide is selected then totals and percentages will be
            calculated over the whole dataset.
        na_cat : scalar, default '-'
            Name for NA-category, assigned to records if `na` is keep/hide.
            This name will show up in the axes.
        na_position : {'first', 'last'}, default 'last'
            Position the NA-group should get on the axes.
        na_rep : default ''
            How to represent NA values *within* the data.
        """

        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v

        # PIVOT
        self.values   = values
        self.index   = index
        self.columns = columns
        self.aggfunc = aggfunc

        if index or columns:
            self._pivot(
                aggfunc    = aggfunc,
                values     = values,
                index      = index,
                columns    = columns,
                fill_value = fill_value,
                observed   = observed,
            )

        if add_totals:
            self.totals(
                axis  = axis,
                level = level,
                **kwargs
            )
        return self

    def style(self, formatter=None, **kwargs):
        default = lambda x: f'{x:n}'
        formatter = default if formatter is None else formatter
        styler = self.df.style.format(formatter, na_rep=self.na_rep)
        rules = style.get_style(self.df, styler.uuid, **kwargs)
        styler.set_table_styles(rules, overwrite=False)
        return styler

    def totals(
        self,
        axis           = 0,
        level          = 0,
        totals_name    = None,
        subtotals_name = None,
        **kwargs
    ):
        """Add totals to output.

        Arguments
        ---------
        axis : {0 or 'index', 1 or 'columns', 2 or 'all', None}, default 0
            Axis to add totals:
            0 : add row with column totals
            1 : add column with row totals
            2 : add row and column totals
            If None supply `level` with a tuple for each axis.
        level : int, level name, or sequence of such, tuple of levels, default 0
            Level number/name of the level to use for calculating the totals.
            Level 0 adds row/column totals, otherwise subtotals are added within
            the specified level. Multiple levels may be supplied in a list. If
        totals_name : str, default CONFIG.aggregation['totals_name']
            Name for the row/column totals.
        subtotals_name : str, default CONFIG.aggregation['subtotals_name']
            Name for the row/column subtotals.
        """

        check_namespace = lambda x,y: getattr(self, y, None) if x is None else x
        totals_name = check_namespace(totals_name, 'totals_name')
        subtotals_name = check_namespace(subtotals_name, 'subtotals_name')

        axlevels = self.__get_axlevels(axis, level)
        for ax, levels in enumerate(axlevels):
            for level in levels:
                self._df = self._df.pipe(
                    aggtotals.add,
                    axis           = ax,
                    level          = level,
                    totals_name    = totals_name,
                    subtotals_name = subtotals_name,
                )
        self.__cast()
        return self

    def percs(
        self,
        axis           = 0,
        level          = 0,
        how            = None,
        totals_name    = None,
        subtotals_name = None,
        label_abs      = None,
        label_rel      = None,
        ndigits        = 1,
        drop_totals    = False,
    ):
        """Add percentages to `df` on `level` of `axis` rounded to `ndigits`.

        This operation will result in a table containing the absolute values as
        well as the percentage values. The absolute and percentage columns will
        be labelled by an added level to the column index.

        (Sub)totals are required to calculate the percentages. If (sub)totals
        are present (`totals_name` and `subtotals_name` are used to identify
        totals within the table) these will be used. When no (sub)totals are
        found, they will be added to the table. Set `drop_totals` to False to
        exlude them from the output.

        Arguments
        ---------
        df : pd.DataFrame
        axis : {0 or 'index', 1 or 'columns', 2 or 'all'}, default 0
            Axis to use for calculating the percentages:
            0 : percentages of each row by the column totals
            1 : percentages of each column by the row totals
            2 : percentages of each field by the table total
        level : int, level name, default 0
            Level number or name for the level on which to calculate the
            percentages. Level 0 uses row/column totals, otherwise subtotals within
            the specified level are used.
        totals_name : str, default CONFIG.aggregation['totals_name']
            Name identifying the row/column totals.
        subtotals_name : str, default CONFIG.aggregation['subtotals_name']
            Name identifying the row/column subtotals.
        ndigits : int, default CONFIG.aggregation['ndigits']
            Number of digits used for rounding the percentages.
        label_abs : str, default CONFIG.aggregation['label_abs']
            Value used for labelling the absolute columns.
        label_abs : str, default CONFIG.aggregation['label_rel']
            Value used for labelling the relative columns.
        drop_totals : bool, default False
            Drop row/column totals from output.
        """


        self.percs_method = how if how is not None else self.percs_method
        if self.percs_method == 'add':
            self._df = self._df.pipe(
                percs.add,
                axis           = axis,
                level          = level,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
                label_abs      = label_abs,
                label_rel      = label_rel,
                ndigits        = ndigits,
                drop_totals    = drop_totals,
            )
        elif self.percs_method == 'transform':
            self._df = self._df.pipe(
                percs.transform,
                axis           = axis,
                level          = level,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
                label_abs      = label_abs,
                label_rel      = label_rel,
                ndigits        = ndigits,
                drop_totals    = drop_totals,
            )
        self.__cast()
        return self

    @property
    def df(self):
        df = self._df if self._df is not None else self._obj
        return df.pipe(self.__hide_na)

    @df.setter
    def df(self, df):
        self._df = df

    def _pivot(
        self,
        aggfunc    = None,
        values     = None,
        index      = None,
        columns    = None,
        fill_value = None,
        observed   = None,
    ):
        if aggfunc is None:
            aggfunc = 'size' if values is None else 'count'

        self.df = self.__drop_na(self._obj).pivot_table(
            aggfunc    = aggfunc,
            values     = values,
            index      = index,
            columns    = columns,
            fill_value = fill_value,
            observed   = observed,
        ).pipe(self.__reindex_na)
        self.__cast()

    def __drop_na(self, df):
        fillna = lambda s: cols.add_category(s, self.na_cat).fillna(self.na_cat)
        to_list = lambda x: [x] if lib.is_scalar(x) else x

        df = df.copy()
        if self.na == 'drop':
            return df.dropna(subset=to_list(self.columns))
        else:
            all_items     = to_list(self.columns) + to_list(self.index)
            selection     = [item for item in all_items if item is not None]
            df[selection] = df[selection].apply(fillna)
            return df

    def __reindex_na(self, df):
        df = df.copy()
        return df.pipe(
            axes.reindex_na,
            axis=0,
            na_rep=self.na_cat,
            na_position=self.na_position,
        ).pipe(
            axes.reindex_na,
            axis=1,
            na_rep=self.na_cat,
            na_position=self.na_position,
        )

    def __hide_na(self, df):
        if self.na == 'hide':
            df = df.copy()
            return df.pipe(
                axes.drop_na,
                axis=0,
                na_rep=self.na_cat,
            ).pipe(
                axes.drop_na,
                axis=1,
                na_rep=self.na_cat,
            )
        return df

    def __cast(self):
        def get_dtype(col):
            if self.percs_method== 'transform' or self.label_rel in col:
                return float
            else:
                return self.dtypes.get(self.aggfunc, float)

        dtypes_to_set = {col:get_dtype(col) for col in self._df.columns if get_dtype(col)}
        self._df = self._df.astype(dtypes_to_set)


    def __get_axlevels(self, axis, level):
        get_level = partial(levels._get_level_number, self._obj)

        def listify(x):
            if x is None:
                return []
            return [x] if isinstance(x, (int, str)) else x

        level = listify(level)
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
            axlevels = [listify(item) for item in listify(axis)]
            return (
                [get_level(0, item) for item in axlevels[0]],
                [get_level(1, item) for item in axlevels[1]],
            )

    def _repr_html_(self):
        return self.style().render()
