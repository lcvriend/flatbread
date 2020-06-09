"""Sanity Module
=============

The sanity module provides decorators for checking the pipeline. The decorator
tests if the output DataFrame meets a specified requirement. If the check fails
an assertion error is raised. The following decorators are provided:

unittest :
    Perform a unittest from the TestCase class on a column of the data.
    First an aggregation is performed on the column, then the resulting value is
    tested against the the comparison scalar.
length :
    Check if the length of the input DataFrame is equal to/smaller than/greater than the output DataFrame.
"""

from unittest import TestCase
from functools import wraps


def unittest(column, operation, test, comparison):
    """Add unittest as sanity check to function.
    If check fails AssertionException is raised.
    Aggregation `operation` will be performed on `column`.
    Result will be compared to `comparison` using `test`.

    Parameters
    ==========
    column : str
        Column name.
    operation : str, func
        Aggregation operation to perform on column.
        Should return scalar for comparison.
    test : str
        Any comparison method from the unittest.TestCase suite.
        Specify the method without the 'assert'.
        If method contains more than one word, then space out the words:
            e.g. assertGreaterEqual -> 'greater equal'
    comparison : scalar
        The value to compare the result to.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            value = result[column].agg(operation)
            method = test.title().replace(' ', '').replace('_', '')
            tester = getattr(TestCase(), f"assert{method}")
            tester(value, comparison)
            return result
        return wrapper
    return decorator


def length(operator):
    """Add a length test as sanity check to function.
    If check fails AssertionException is raised.
    The input will be tested against output using `operator`.

    Parameters
    ==========
    operator : str
        Operator to use for comparing in and output
        <  : lesser than
        <= : lesser than or equal to
        == : equal to
        != : not equal to
        >  : smaller than
        >= : smaller than or equal to
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            df, *_ = args
            len_in = len(df)
            result = func(*args, **kwargs)
            len_out = len(result)

            operators = {
                '<'  : '__lt__',
                '<=' : '__le__',
                '==' : '__eq__',
                '!=' : '__ne__',
                '>'  : '__gt__',
                '>=' : '__ge__',
            }

            compare = getattr(len_in, operators[operator])
            assert compare(len_out), (
                f"False: input {len_in} {operator} output {len_out}"
            )

            return result
        return wrapper
    return decorator
