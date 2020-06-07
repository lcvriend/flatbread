from functools import wraps


def copy(func):
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        df = df.copy()
        result = func(df, *args, **kwargs)
        return result
    return wrapper
