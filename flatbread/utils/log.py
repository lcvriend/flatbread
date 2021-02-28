"""
Logging the build process:

:py:func:`flatbread.utils.log.entry` :
    Decorator for creating a log to be stored in the DataFrame attrs under
    'flatbread_log'.
"""

from functools import wraps

import pandas as pd # type: ignore


def create_log_entry(func, result, *args, **kwargs):
    return dict(
        timestamp = pd.Timestamp.now(),
        func_name = func.__name__,
        module    = func.__module__,
        full_name = f"{func.__module__}.{func.__name__}",
        func      = func,
        args      = args,
        kwargs    = kwargs,
        rows      = result.shape[0],
        cols      = result.shape[1],
    )


def entry(func):
    """
    Decorator for logging the build process and storing it in the attrs of
    the df under 'flatbread_log'. The first item in the log contains the
    original df.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        df, *args = args
        log = df.attrs.get("flatbread_log")
        log_entry = create_log_entry(func, result, *args, **kwargs)
        if log is None:
            log = [
                dict(
                    timestamp = pd.Timestamp.now(),
                    dataframe = df,
                    rows      = df.shape[0],
                    cols      = df.shape[1],
                )
            ]
        log.append(log_entry)
        result.attrs["flatbread_log"] = log
        return result
    return wrapper
