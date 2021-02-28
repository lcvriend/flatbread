"""
Provides decorators for checking if all goes well within the processing
pipeline. The decorator tests if the output DataFrame meets a specified
requirement. If the check fails an assertion error is raised. The following
decorators are provided:

:py:func:`flatbread.utils.sanity.unittest` :
    Perform a unittest from the TestCase class on a column of the data.
    First an aggregation is performed on the column, then the resulting value is
    tested against the the comparison scalar.
:py:func:`flatbread.utils.sanity.length` :
    Check if the length of the input DataFrame is equal to/smaller than/greater than the output DataFrame.
"""

from unittest import TestCase
from functools import wraps


def unittest(column, aggregation, test, comparison):
    """
    Decorator adds unittest as a sanity check to a function. The check
    consists of an operation (`aggregation`) which aggregates the values in
    `column` into a scalar. This result will be compared to the `comparison`
    scalar using `test`. If the check fails an AssertionException is raised.

    Parameters
    ----------
    column : str
        Column name.
    aggregation : str, func
        Aggregation operation to perform on column.
        Should return scalar for comparison.
    test : str
        Any comparison method from the unittest.TestCase suite.
        Specify the method without the 'assert'.
        If method contains more than one word, then space out the words:
            e.g. assertGreaterEqual -> 'greater equal'
    comparison : scalar
        The value to compare the result to.

    Returns
    -------
    func
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            value = result[column].agg(aggregation)
            method = test.title().replace(' ', '').replace('_', '')
            message = f"[{func.__module__}][{func.__name__}]"
            tester = getattr(TestCase(), f"assert{method}")
            tester(value, comparison, msg=message)
            return result
        return wrapper
    return decorator


def length(operator):
    """
    Decorator adds a length test as sanity check to a function. If the check
    fails an AssertionException is raised. The input length will be tested
    against the output length using `operator`.

    Parameters
    ----------
    operator : str
        Operator to use for comparing in and output
        <  : lesser than
        <= : lesser than or equal to
        == : equal to
        != : not equal to
        >  : smaller than
        >= : smaller than or equal to

    Returns
    -------
    func
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
                f"input {len_in} {operator} output {len_out} is False : "
                f"[{func.__module__}][{func.__name__}]"
            )

            return result
        return wrapper
    return decorator
