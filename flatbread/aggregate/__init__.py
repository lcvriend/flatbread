from functools import wraps

from flatbread.config import CONFIG
from flatbread.axes import get_axis_number


TOTALS_SETTINGS = {'aggregation': ['totals_name', 'subtotals_name']}
PERCS_SETTINGS = {'aggregation': ['ndigits', 'label_abs', 'label_rel']}
AGG_SETTINGS = {'aggregation':
    TOTALS_SETTINGS['aggregation'] +
    PERCS_SETTINGS['aggregation']
}
