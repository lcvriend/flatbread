"""
The :py:class:`flatbread.pivot.PivotTable` extension to the
DataFrame. It is accessible through the ``pita`` accessor. The goal is to
provide a bit more functionality to pandas pivot table capabilities while
also remaining as close as possible to pandas native objects.
"""

import pandas as pd

from flatbread.aggregate import totals as aggtotals
from flatbread.aggregate import percentages
from flatbread.build import series
from flatbread import axes
from flatbread.style import FlatbreadStyler
from flatbread.config import HERE, load_settings


@pd.api.extensions.register_dataframe_accessor("pita")
class PivotTable:
    """
    DataFrame accessor ``pita`` extending pivot table capabilities.
    """
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
        pct_how        = None,
        aggfunc        = None,
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
        self.pct_how        = pct_how
        self.aggfunc        = aggfunc
        self.title          = None
        self.caption        = None
        self.style          = FlatbreadStyler(self)

    @load_settings(['aggregation', 'na'])
    def __call__(
        self,
        values     = None,
        index      = None,
        columns    = None,
        aggfunc    = None,
        fill_value = None,
        observed   = True,
        add_totals = False,
        axis       = 0,
        level      = 0,
        **kwargs
    ):
        """
        View DataFrame as a spreadsheet-style pivot table.

        **Pivot data**

        If index and/or columns are given, then the data will first be pivoted
        using ``pivot_table``.

        See: :py:meth:`pandas.DataFrame.pivot_table`

        **Missing values**

        If ``na`` is ``keep`` or ``hide`` then the missing values will be
        handled before grouping. Normally, when pivoting records that do not
        fall into a group are dropped. Instead these records will be assigned
        to a special NA-group, that can factor into the calculations for
        percentages/totals.

        **Totals**

        Set ``add_totals`` to True to add (sub)totals to ``axis`` and ``level``
        of the output.

        **Further processing**

        Additional operations may be chained to add more features to the output:

        :meth:`flatbread.pivot.PivotTable.totals`
            Add (sub)totals to the output.
        :meth:`flatbread.pivot.PivotTable.percs`
            Add percentages to the output or transform to percentages.
        :meth:`flatbread.pivot.PivotTable.style`
            Add formatting and styling to the output.

        Arguments
        ---------
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
            Contrary to ``pivot_table`` default behavior, ``pita`` will act as
            a crosstab. If no values are given, then ``size`` is used to
            aggregate otherwise ``count``.

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
        add_totals : bool, default False
            Add (sub)totals to table.
        axis : {0, 'index', 1, 'columns', 2, 'all'} or tuple, default 0
            Axis to add totals:

            * index (0) : add row with column totals
            * columns (1) : add column with row totals
            * all (2) : add row and column totals

            Tuple (size 2) mapping level(s) to rows/columns may also be
            supplied (will ignore ``level``).
        level : int, level name, or sequence of such, default 0
            Level number or name for the level to use for calculating the
            totals. Level 0 adds row/column totals, otherwise subtotals are
            added within the specified level. Multiple levels may be supplied
            in a list.
        totals_name : str, default 'Total'
            Name for the row/column totals.
        subtotals_name : str, default 'Subtotal'
            Name for the row/column subtotals.
        na : {'drop', 'keep', 'hide'}, default 'drop'
            How to handle records that do not fall into any category of a group:

            * drop : exclude these records from the view completely
            * keep : keep these records and assign them to a `na_cat` group
            * hide : these records but hide them from output

            If keep/hide is selected then totals and percentages will be
            calculated over the whole dataset.
        na_cat : scalar, default '-'
            Name for NA-category, assigned to records if `na` is keep/hide.
            This name will show up in the axes.
        na_position : {'first', 'last'}, default 'last'
            Position the NA-group should get on the axes.
        na_rep : default ''
            How to represent NA values *within* the data.

        Returns
        -------
        PivotTable
            An Excel style pivot table
        """

        self.style = FlatbreadStyler(self)

        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v

        # PIVOT
        self.values  = values
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

        # TOTALS
        if add_totals:
            self.totals(
                axis  = axis,
                level = level,
                **kwargs
            )
        self.style.data = self.df
        return self

    @load_settings(['aggregation', 'na'])
    def totals(
        self,
        axis           = 0,
        level          = 0,
        totals_name    = None,
        subtotals_name = None,
        **kwargs
    ):
        """
        Add (sub)totals to output.

        Arguments
        ---------
        axis : {0, 'index', 1, 'columns', 2, 'all'} or tuple, default 0
            Axis to add totals:

            * index (0) : add row with column totals
            * columns (1) : add column with row totals
            * all (2) : add row and column totals

            Tuple (size 2) mapping level(s) to rows/columns may also be
            supplied (will ignore ``level``).
        level : int, level name, or sequence of such, default 0
            Level number or name for the level to use for calculating the
            totals. Level 0 adds row/column totals, otherwise subtotals are
            added within the specified level. Multiple levels may be supplied
            in a list.
        totals_name : str, default 'Total'
            Name for the row/column totals.
        subtotals_name : str, default 'Subtotal'
            Name for the row/column subtotals.

        Returns
        -------
        PivotTable
            An Excel style pivot table
        """
        totals_name = self.__update_namespace(
            'totals_name', totals_name)
        subtotals_name = self.__update_namespace(
            'subtotals_name', subtotals_name)

        self._df = self._df.pipe(
            aggtotals.add,
            axis           = axis,
            level          = level,
            totals_name    = totals_name,
            subtotals_name = subtotals_name,
        )
        self.__cast()
        return self

    @load_settings(['aggregation', 'na'])
    def pct(
        self,
        axis           = 0,
        level          = 0,
        how            = None,
        ndigits        = None,
        unit           = 100,
        label_abs      = None,
        label_rel      = None,
        totals_name    = None,
        subtotals_name = None,
        drop_totals    = False,
        **kwargs
    ):
        """
        Add percentages to output or transform output to percentages.

        (Sub)totals are required to calculate the percentages. If (sub)totals
        are present (``totals_name`` and ``subtotals_name`` are used to identify
        totals within the table) these will be used. When no (sub)totals are
        found, they will be added to the table. Set ``drop_totals`` to False to
        exlude them from the output.

        Set ``unit`` in order to calculate other fractions.

        Arguments
        ---------
        axis : {0 or 'index', 1 or 'columns', 2 or 'all'}, default 0
            Axis to use for calculating the percentages:

            * 0 : percentages of each row by the column totals
            * 1 : percentages of each column by the row totals
            * 2 : percentages of each field by the table total
        level : int, level name, default 0
            Level number or name for the level on which to calculate the
            percentages. Level 0 uses row/column totals, otherwise subtotals
            within the specified level are used.
        how : {'add', 'transform'}, default 'add'

        ndigits : int, default 1
            Number of digits used for rounding the percentages.
            Set to -1 for no rounding.
        unit : int, default 100,
            Unit of prevalence.
        totals_name : str, default 'Total'
            Name identifying the row/column totals.
        subtotals_name : str, default 'Subtotal'
            Name identifying the row/column subtotals.
        drop_totals : bool, default False
            Drop row/column totals from output.

        Returns
        -------
        PivotTable
            An Excel style pivot table
        """
        totals_name = self.__update_namespace(
            'totals_name', totals_name)
        subtotals_name = self.__update_namespace(
            'subtotals_name', subtotals_name)

        self.pct_how = how if how is not None else self.pct_how
        if self.pct_how == 'add':
            self._df = self._df.pipe(
                percentages.add,
                axis           = axis,
                level          = level,
                ndigits        = ndigits,
                unit           = unit,
                label_abs      = label_abs,
                label_rel      = label_rel,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
                drop_totals    = drop_totals,
            )
        elif self.pct_how == 'transform':
            self._df = self._df.pipe(
                percentages.transform,
                axis           = axis,
                level          = level,
                ndigits        = ndigits,
                unit           = unit,
                label_abs      = label_abs,
                label_rel      = label_rel,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
                drop_totals    = drop_totals,
            )
        self.__cast()
        return self

    def to_html(self, path=None):
        "Return html, if ``path`` is given write to path instead."
        return self.style.to_html(path=path)

    @property
    def df(self):
        "Return the underlying DataFrame (without styling)."
        df = self._df if self._df is not None else self._obj
        return df.pipe(self.__hide_na)

    @df.setter
    def df(self, df):
        self._df = df

    def add_caption(self, caption):
        "Add caption to table."
        self.caption = caption
        return self

    def add_title(self, title):
        "Add title to table."
        self.title = title
        return self

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
        add_cat = series.add_category
        fillna = lambda s: add_cat(s, self.na_cat).fillna(self.na_cat)
        to_list = lambda x: [x] if pd.api.types.is_scalar(x) else x

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
            test = lambda x,lbl: lbl in x if isinstance(x, tuple) else x == lbl
            if self.pct_how == 'transform' or test(col, self.label_rel):
                return float
            else:
                return self.dtypes.get(self.aggfunc, float)

        dtypes_to_set = {col:get_dtype(col) for col in self._df.columns if get_dtype(col)}
        self._df = self._df.astype(dtypes_to_set)

    def __update_namespace(self, var_name, val):
        val = getattr(self, var_name, None) if val is None else val
        setattr(self, var_name, val)
        return val

    def _repr_html_(self):
        return self.style.render()
