import flatbread.utils.log as log
import flatbread.utils.sanity as sanity
import flatbread.core.aggregation as agg
import flatbread.core.assign as assign
import flatbread.core.load as load
import flatbread.core.select as select
import flatbread.core.drop as drop
import flatbread.core.axes.columns as cols
import flatbread.core.axes.columns as columns
import flatbread.core.axes.index as idx
import flatbread.core.axes.index as index
import flatbread.core.axes.index as rows
from flatbread.present.format import formatter
from flatbread.present.trendline import TrendLine


@log.entry
def init(df, **kwargs):
    return df
