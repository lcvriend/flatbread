from flatbread.config import read_config

DEFAULTS = read_config()

import flatbread.accessors.dataframe
import flatbread.accessors.series
import flatbread.accessors.index
