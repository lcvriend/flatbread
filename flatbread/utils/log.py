"""Log module
==========

The log module provides decorators for logging:

entry :
    Create a build log to be stored in the DataFrame attrs.
to_file :
    Create a file log of the build process.
"""

import logging
from functools import wraps

import pandas as pd # type: ignore
from flatbread.config import HERE
import flatbread.utils.repper as repper


logger = logging.getLogger(__name__)
fh = logging.FileHandler(HERE / "flatbread.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


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
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        df, *args = args
        log = df.attrs.get("log")
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
        result.attrs["log"] = log
        return result
    return wrapper


def to_file(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        shape = result.shape
        repr_func = repper.func(func)
        repr_args = repper.log_args(func, *args, **kwargs)
        repr_rows = str(shape[0]) + " rows"
        repr_cols = str(shape[1]) + " cols"
        info = f"{repr_func}{repr_args}{repr_rows:>12}, {repr_cols}"
        logger.debug(info)
        return result
    return wrapper
