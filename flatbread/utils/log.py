"""Log module
==========

The log module provides decorators for logging:

entry :
    Create a build log to be stored in the DataFrame attrs.
to_file :
    Create a file log of the build process.
"""

import sys
import logging
from functools import wraps

import pandas as pd
from flatbread.config import here
import flatbread.utils.repper as repper


logger = logging.getLogger(__name__)
fh = logging.FileHandler(here / "flatbread.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def create_log_entry(func, result, *args, **kwargs):
    row = dict(
        func   = repper.func(func),
        args   = repper.args(*args),
        kwargs = repper.kwargs(**kwargs),
        rows   = result.shape[0],
        cols   = result.shape[1],
    )
    return pd.DataFrame(
        index=[pd.Timestamp.now()],
        data=row,
    )


def entry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        df, *args = args
        log = df.attrs.get('log')
        # result_log = result.attrs.get('log')
        # if result_log is not None:
        #     log = log.update(result_log)

        log_entry = create_log_entry(func, result, *args, **kwargs)
        if log is None:
            log = log_entry
        else:
            log = log.append(log_entry)
        result.attrs['log'] = log

        return result
    return wrapper


################


def to_file(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        shape = result.shape
        repr_func = repper.func(func)
        repr_args = repper.log_args(func, *args, **kwargs)
        repr_rows = str(shape[0])+' rows'
        repr_cols = str(shape[1])+' cols'
        info = f"{repr_func}{repr_args}{repr_rows:>12}, {repr_cols}"
        logger.debug(info)

        return result
    return wrapper
