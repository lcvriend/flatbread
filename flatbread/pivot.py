from functools import partial

import pandas as pd
from pandas._libs import lib

import flatbread.build.columns as cols
import flatbread.aggregate as agg
import flatbread.aggregate.totals as aggtotals
import flatbread.aggregate.percentages as percs
import flatbread.axes as axes
import flatbread.levels as levels
import flatbread.format.style as style
from flatbread.format import format as format_table
from flatbread.config import HERE, load_settings
from flatbread.aggregate import AGG_SETTINGS


@pd.api.extensions.register_dataframe_accessor("pita")
class Pivot:
    dtypes = {
        'count': 'Int64',
        'size':  'Int64',
    }

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        pass
    #     # verify there is a column latitude and a column longitude
    #     if 'latitude' not in obj.columns or 'longitude' not in obj.columns:
    #         raise AttributeError("Must have 'latitude' and 'longitude'.")

    @load_settings(AGG_SETTINGS)
    def __call__(
        self,
        values         = None,
        index          = None,
        columns        = None,
        aggfunc        = None,
        fill_value     = None,
        totals         = False,
        percentages    = False,
        axis           = 2,
        level          = 0,
        totals_name    = None,
        subtotals_name = None,
        label_abs      = None,
        label_rel      = None,
        ndigits        = 1,
        na             = 'drop',
        na_rep         = None,
        na_position    = 'last',
        observed       = True,
    ):

        data = self._obj.copy()

        if aggfunc is None:
            aggfunc = 'size' if values is None else 'count'
        if na != 'drop':
            to_list = lambda x: [x] if lib.is_scalar(x) else x
            all_items = to_list(columns) + to_list(index)
            selection = [item for item in all_items if item is not None]
            fillna = lambda s: s.pipe(cols.add_category, na_rep).fillna(na_rep)
            data[selection] = data[selection].apply(fillna)

        output = data.pivot_table(
            values       = values,
            index        = index,
            columns      = columns,
            aggfunc      = aggfunc,
            fill_value   = fill_value,
            margins      = False,
            margins_name = totals_name,
            dropna       = True,
            observed     = observed,
        )

        output = output.pipe(
            axes.reindex_na,
            axis=0,
            na_rep=na_rep,
            na_position=na_position,
        ).pipe(
            axes.reindex_na,
            axis=1,
            na_rep=na_rep,
            na_position=na_position,
        )

        if totals:
            output = output.pipe(
                aggtotals.add,
                axis           = axis,
                level          = level,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
            )

        percs_level = min(self._get_level_numbers(axis, level))
        if percentages == 'add':
            output = output.pipe(
                percs.add,
                axis           = axis,
                level          = percs_level,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
                label_abs      = label_abs,
                label_rel      = label_rel,
                ndigits        = ndigits,
                drop_totals    = not totals,
            )
        elif percentages == 'transform':
            output = output.pipe(
                percs.transform,
                axis           = axis,
                level          = percs_level,
                totals_name    = totals_name,
                subtotals_name = subtotals_name,
                label_abs      = label_abs,
                label_rel      = label_rel,
                ndigits        = ndigits,
                drop_totals    = not totals,
            )

        if na == 'hide':
            output = output.pipe(
                axes.drop_na,
                axis=0,
                na_rep=na_rep,
            ).pipe(
                axes.drop_na,
                axis=1,
                na_rep=na_rep,
            )

        def get_dtype(col):
            if percentages == 'transform' or label_rel in col:
                return float
            else:
                return self.dtypes.get(aggfunc, 'float')

        dtypes_to_set = {col:get_dtype(col) for col in output.columns}
        output = output.astype(dtypes_to_set)
        return output

    def format(self, *args, **kwargs):
        df = self(*args, **kwargs).copy()
        styler = df.pipe(format_table)
        styler.set_table_styles(
            style.get_style(df),
            overwrite=False,
        )
        return styler

    def _output_dtype(self, aggfunc=None):
        return self.dtypes.get(aggfunc, float)

    def _get_level_numbers(self, axis, level):
        get_level = partial(levels._get_level_number, self._obj)
        if isinstance(level, (str, int)):
            level = [level]
        if axis == 2:
            # validate columns, then index
            (get_level(axis-1, i) for i in level)
            axis = 0
        return [get_level(axis, i) for i in level]
