"""Readout module
==============

The readout module contains decorators for for adding readouts (print
statements) to functions. They can be used to give direct visual feedback to the
user during the build process. The following decorators are provided:

printout :
    Add a simple message to be printed before/after processing.
column :
    Calculate an aggregate from a specified column in the resuting DatFrame and
    print it.
shape :
    Print the resulting shape of the DataFrame.
"""

from functools import wraps


def printout(msg, when='before'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if when == 'before':
                print(msg)
            result = func(*args, **kwargs)
            if when == 'after':
                print(msg)
            return result
        return wrapper
    return decorator


def column(column, agg='max', table=''):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            value = result[column].agg(agg)
            items = [column, str(value)]
            readout = ' '.join(items)
            print(readout)
            return result
        return wrapper
    return decorator


def shape(table=''):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            items = [table, str(result.shape)]
            readout = ' '.join(items)
            print(readout)
            return result
        return wrapper
    return decorator
