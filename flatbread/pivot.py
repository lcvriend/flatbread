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

    @load_settings(['aggregation', 'format'])
    def __init__(self, pandas_obj, **kwargs):
        self._obj           = pandas_obj
        self._df            = pandas_obj
        self._uuid          = pandas_obj.style.uuid
        self.pipeline       = list()
        self.index          = None
        self.columns        = None
        self.na             = 'drop'
        self.na_cat         = None
        self.na_position    = 'last'
        self.na_rep         = None
        self.totals_name    = None
        self.subtotals_name = None
        self.label_abs      = None
        self.label_rel      = None
        self.ndigits        = 1
        self.drop_totals    = False
        self.percentages    = None

    def __call__(
        self,
        values         = None,
        index          = None,
        columns        = None,
        aggfunc        = None,
        fill_value     = None,
        add_totals     = False,
        axis           = 0,
        level          = 0,
        observed       = True,
        **kwargs
    ):

        self.values = values
        self.index = index
        self.columns = columns
        self.aggfunc = aggfunc

        if index or columns:
            self._pivot(
                aggfunc        = aggfunc,
                values         = values,
                index          = index,
                columns        = columns,
                fill_value     = fill_value,
                observed       = observed,
            )

        if add_totals:
            self.totals(
                axis           = axis,
                level          = level,
                **kwargs
            )
        return self

    def style(self, formatter=None, **kwargs):
        default = lambda x: f'{x:n}'
        formatter = default if formatter is None else formatter
        styler = self.df.style.set_uuid(self._uuid
        ).format(formatter, na_rep=self.na_rep)

        rules = style.get_style(self.df, self._uuid, **kwargs)
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
        check_namespace = lambda x,y: getattr(self, y, None) if x is None else x
        totals_name = check_namespace(totals_name, 'totals_name')
        subtotals_name = check_namespace(subtotals_name, 'subtotals_name')

        axlevels = self._get_axlevels(axis, level)
        for ax, levels in enumerate(axlevels):
            for level in levels:
                self.df = self.df.pipe(
                    aggtotals.add,
                    axis           = ax,
                    level          = level,
                    totals_name    = totals_name,
                    subtotals_name = subtotals_name,
                )
        self._cast()
        return self

    def percs(
        self,
        axis           = 0,
        level          = 0,
        how            = 'add',
        drop_totals    = False,
        totals_name    = None,
        subtotals_name = None,
        label_abs      = None,
        label_rel      = None,
        ndigits        = 1,
    ):
        if how == 'add':
            self.df = self.df.pipe(
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
        elif how == 'transform':
            self.df = self.df.pipe(
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
        self._cast()
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
            aggfunc      = aggfunc,
            values       = values,
            index        = index,
            columns      = columns,
            fill_value   = fill_value,
            observed     = observed,
        ).pipe(self.__reindex_na)
        self._cast()

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

    def _cast(self):
        def get_dtype(col):
            if self.percentages == 'transform' or self.label_rel in col:
                return float
            else:
                return self.dtypes.get(self.aggfunc, float)

        dtypes_to_set = {col:get_dtype(col) for col in self.df.columns if get_dtype(col)}
        self.df = self.df.astype(dtypes_to_set)


    def _get_axlevels(self, axis, level):
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
