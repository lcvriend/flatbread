"""Flatbread Library
=================

The Flatbread Library provides a collection of modules for presenting data.
"""

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
from flatbread.format import format
from flatbread.config import CONFIG
from flatbread.plot.trendline import TrendLine
from flatbread.utils import sanity, readout, log

__version__ = '0.0.8'
__license__ = 'GPLv3+'
__author__  = 'L.C. Vriend'
__email__   = 'vanboefer@gmail.com'
__credits__ = ['L.C. Vriend']
