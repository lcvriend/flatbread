from unittest import TestCase
from functools import wraps


def unittest(column, operation, test, comparison):
    """
    Add unittest as sanity check to function.
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
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            df, *_ = args
            len_in = len(df)
            result = func(*args, **kwargs)
            len_out = len(result)

            if operator == '==':
                assert len_in == len_out, (
                    f"Length of original ({len_in}) is not equal to "
                    f"length of output ({len_out})"
                )
            if operator == '!=':
                assert len_in != len_out, (
                    f"Length of original ({len_in}) is equal to "
                    f"length of output ({len_out})"
                )
            elif operator == '>':
                assert len_in > len_out, (
                    f"Length of original ({len_in}) is not greater than "
                    f"length of output ({len_out})"
                )
            elif operator == '<':
                assert len_in > len_out, (
                    f"Length of original ({len_in}) is not lesser than "
                    f"length of output ({len_out})"
                )
            return result
        return wrapper
    return decorator
