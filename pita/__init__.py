import pita.utils.log as log
import pita.utils.sanity as sanity
import pita.core.aggregation as agg
import pita.core.assign as assign
import pita.core.load as load
import pita.core.select as select
import pita.core.drop as drop
import pita.core.axes.columns as cols
import pita.core.axes.columns as columns
import pita.core.axes.index as idx
import pita.core.axes.index as index
import pita.core.axes.index as rows
from pita.present.format import formatter
from pita.present.trendline import TrendLine


@log.entry
def init(df, **kwargs):
    return df
