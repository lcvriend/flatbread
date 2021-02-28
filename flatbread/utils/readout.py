"""
Decorators for adding readouts (print statements) to functions. They can be
used to give direct visual feedback to the user during the build process. The
following decorators are provided:

:py:func:`flatbread.utils.readout.message` :
    Add a static message to be printed before/after processing.
:py:func:`flatbread.utils.readout.column` :
    Calculate an aggregate from a specified column in the resuting DataFrame and
    print it.
:py:func:`flatbread.utils.readout.shape` :
    Print the resulting shape of the DataFrame.
:py:func:`flatbread.utils.readout.timer` :
    Measure time it takes for a function to process and print it.
"""

from functools import wraps
import time


def message(msg, when='before', print_func_name=True, table_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if when == 'before':
                _read_out(msg, func if print_func_name else None, table_name)
            result = func(*args, **kwargs)
            if when == 'after':
                _read_out(msg, func if print_func_name else None, table_name)
            return result
        return wrapper
    return decorator


def column(column, agg='max', print_func_name=True, table_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            value = result[column].agg(agg)
            _read_out(str(value), func if print_func_name else None, table_name)
            return result
        return wrapper
    return decorator


def shape(print_func_name=True, table_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            shape = str(result.shape)
            _read_out(shape, func if print_func_name else None, table_name)
            return result
        return wrapper
    return decorator


def timer(print_func_name=True, table_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            elapsed = str(end - start)
            _read_out(elapsed, func if print_func_name else None, table_name)
            return result
        return wrapper
    return decorator


def _read_out(item, func=None, table_name=None):
    add_brackets = lambda x: f"[{x}]"
    func_name = add_brackets(func.__name__) if func is not None else ''
    module_name = add_brackets(func.__module__) if func is not None else ''
    table_name = add_brackets(table_name) if table_name is not None else ''
    meta_data = ''.join([module_name, func_name, table_name])
    readout = ' '.join([meta_data, item])
    print(readout)
    return None
