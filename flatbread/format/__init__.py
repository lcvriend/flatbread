from flatbread.config import CONFIG


def set_value(key, value=None):
    if value is None:
        return CONFIG.format[key]
    return value


def format(df, na_rep=None):
    na_rep = set_value('na_rep', na_rep)
    return df.style.format(lambda x: f'{x:n}', na_rep=na_rep)
