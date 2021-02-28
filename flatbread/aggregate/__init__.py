"""
Aggregation for flatbread's pivot tables. Modules contain functions for adding
aggregates to a flatbread table:

:py:mod:`flatbread.aggregate.percentages` :
    Add percentages to flatbread table or transform data to percentages.
:py:mod:`flatbread.aggregate.totals` :
    Add totals/subtotals to flatbread table.
"""

from flatbread.config import CONFIG


TOTALS_SETTINGS = {'aggregation': ['totals_name', 'subtotals_name']}
PERCS_SETTINGS = {'aggregation': ['ndigits', 'label_abs', 'label_rel']}
AGG_SETTINGS = 'aggregation'
