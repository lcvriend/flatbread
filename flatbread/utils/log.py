import sys
import logging
# from io import StringIO
from functools import wraps

import pandas as pd
from flatbread.config import here
import flatbread.utils.repper as repper


log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
# log_capture = StringIO()
# ch = logging.StreamHandler(sys.stdout)
# ch = logging.StreamHandler(log_capture)
# ch.setLevel(logging.DEBUG)
# log.addHandler(ch)
fh = logging.FileHandler(here / "flatbread.log", "w")
fh.setLevel(logging.DEBUG)
log.addHandler(fh)


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


def max_value(column):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(column, ':', result[column].max())
            return result
        return wrapper
    return decorator


def shape(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(result.shape)
        return result
    return wrapper


################


def log_shape(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        shape = result.shape
        repr_func = repper.func(func)
        repr_args = repper.log_args(func, *args, **kwargs)
        repr_rows = str(shape[0])+' rows'
        repr_cols = str(shape[1])+' cols'
        info = f"{repr_func}{repr_args}{repr_rows:>12}, {repr_cols}"
        log.debug(info)

        return result
    return wrapper


def log_colsize(func):
    @wraps(func)
    def wrapper(*args, log_col=None, **kwargs):
        result = func(*args, **kwargs)
        if log_col is not None:
            n_rows = result[log_col].notna().sum()
            n_nans = len(result) - n_rows

            col_name = f"..column '{log_col}'"
            repr_col = f"{col_name:<{MAX_LENGTH_COL1}}"
            repr_args = repper.log_args(func, *args, **kwargs)
            repr_rows = f"{n_rows} rows"
            repr_nans = f"{n_nans} NaNs"

            info = f"{repr_col}{repr_args}{repr_rows:>12}, {repr_nans}"
            log.debug(info)
        return result
    return wrapper


def build(goal):
    line = (11 + len(goal)) * '='
    return f"BUILD {goal.upper()}\n{line}"
