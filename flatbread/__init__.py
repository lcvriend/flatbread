from flatbread.utils import log
from flatbread.utils import sanity
from flatbread.core import aggregation
from flatbread.core import aggregation as agg
from flatbread.core import assign
from flatbread.core import load
from flatbread.core import select
from flatbread.core import drop
from flatbread.core.axes import columns
from flatbread.core.axes import columns as cols
from flatbread.core.axes import index
from flatbread.core.axes import index as idx
from flatbread.core.axes import index as rows
from flatbread import present
from flatbread.present.format import formatter
from flatbread.present.trendline import TrendLine

@log.entry
def init(df, **kwargs):
    return df
