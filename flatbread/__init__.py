from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from flatbread.accessors.dataframe import PitaFrame
    from flatbread.accessors.series import PitaSeries

    class DataFrame(pd.DataFrame):
        pita: PitaFrame

    class Series(pd.Series):
        pita: PitaSeries

from flatbread.config import DEFAULTS
import flatbread.accessors.dataframe
import flatbread.accessors.series
import flatbread.accessors.index
