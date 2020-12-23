from functools import wraps

from flatbread.config import CONFIG
from flatbread.axes import get_axis_number


TOTALS_LABELS = ['totals_name', 'subtotals_name']
PERCS_LABELS = ['ndigits', 'label_abs', 'label_rel']


def get_value(key, value=None):
    if value is None:
        return CONFIG.aggregation[key]
    return value


def set_labels(labels_to_fetch):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            labels = {
                label:get_value(label, kwargs.get(label))
                for label in labels_to_fetch
            }
            kwargs.update(labels)
            return func(*args, **kwargs)
        return wrapper
    return decorator
