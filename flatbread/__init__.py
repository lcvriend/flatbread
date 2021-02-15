"""Flatbread
=========

Pivot tables are a great tool for exploring and presenting your data. Flatbread
extends pandas' pivot table capabilities by adding the `pita` accessor to your
dataframes.

## Styling
The pivot tables viewed through flatbread have their own (customizable)
styling. This makes the view on your data clearly distinguishable from the data itself and can add to the table's readability.

Flatbread's styling uses pandas' Styler. The `style` method will return the
Styler object which then can be used to further style the table, f.e. using the
builtins.

## Aggregates
Flatbread makes it easy to add totals and subtotals to any axis and level of
your table. You can also transform your table into percentages or add them into
the table next to your data.

## NA
Pandas' pivot table only includes records if all groupings have a value. It can
be convenient to see the NA's in your pivoted data or at least have them
factor into the aggregate calculations. Flatbread offers the option to keep the
NA's and either hide or show them in the final output.
"""

import flatbread.pivot
import flatbread.aggregate as aggregate
import flatbread.aggregate as agg
import flatbread.aggregate.totals as totals
import flatbread.aggregate.percentages as percentages
import flatbread.aggregate.percentages as percs
import flatbread.build.drop as drop
import flatbread.build.columns as columns
import flatbread.build.columns as cols
import flatbread.build.rows as rows
import flatbread.build.rows as index
import flatbread.build.rows as idx
import flatbread.build.test as test
import flatbread.style as style
from flatbread.config import CONFIG
from flatbread.plot.trendline import TrendLine
from flatbread.utils import sanity, readout, log

__version__ = '0.0.8'
__license__ = 'GPLv3+'
__author__  = 'L.C. Vriend'
__email__   = 'vanboefer@gmail.com'
__credits__ = ['L.C. Vriend']
