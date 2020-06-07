from itertools import accumulate, takewhile
from flatbread.config import config


def func(func):
    module = '.'.join(func.__module__.split('.')[2:])
    func_name = f"[{module}.{func.__name__}]"
    return f"{func_name:<{MAX_LENGTH_COL1}}"


def args(*args):
    output = []
    for arg in args[1:]:
        if arg is None:
            continue
        output.append(represent_arg(arg))
    return ', '.join(output)


def kwargs(**kwargs):
    output = []
    for kw, arg in kwargs.items():
        if arg is None:
            continue
        kw = f"{kw}:"
        arg = kw + represent_arg(arg)
        output.append(arg)
    return ', '.join(output)


def represent_arg(arg):
    types = (int, float, str, list, tuple, set)
    if not isinstance(arg, types):
        return str(type(arg)).split("'")[1].split('.')[-1]
    elif isinstance(arg, str):
        return '"' + arg + '"'
    else:
        return repr(arg)


################


MAX_LENGTH_COL1 = config['repper']['max_length_col1']
MAX_LENGTH_COL2 = config['repper']['max_length_col2']
BRACKETS = {list: '[]', set: '{}', tuple: '()'}


def log_args(*args, **kwargs):
    limit     = MAX_LENGTH_COL2
    mortar    = ', '
    n_args    = len(args) + len(kwargs)
    spaces    = (n_args - 1) * len(mortar)
    repr_args = list()

    for arg in args[2:]:
        arg = rep_arg(arg, limit)
        if arg is None:
            continue
        if limit - len(arg) < spaces:
            break
        limit -= len(arg)
        repr_args.append(arg)

    for kw, arg in kwargs.items():
        kw = f"{kw}:"
        arg = kw + rep_arg(arg, limit-len(kw))
        if arg is None:
            continue
        if limit - len(arg) < spaces:
            break
        limit -= len(arg)
        repr_args.append(arg)

    if len(repr_args) < len(args[2:]):
        repr_args.append('...')

    return f"{mortar.join(repr_args):<{MAX_LENGTH_COL2}}"


def rep_list(collection, limit):
    l_bracket, r_bracket = BRACKETS[type(collection)]
    items = [repr(item) for item in collection]
    lengths = accumulate([len(item) + 2 for item in items])
    items = [item for item, length in zip(items, lengths) if length < limit-4]
    if len(items) < len(collection):
        items.append('...')
    return l_bracket + ', '.join(items) + r_bracket


def rep_arg(arg, limit):
    types = (int, float, str, list, tuple, set)
    # if callable(arg) or isinstance(arg, pd.DataFrame):
    #     return None
    if not isinstance(arg, types):
        return str(type(arg)).split("'")[1].split('.')[-1]

    if isinstance(arg, tuple(BRACKETS.keys())):
        return rep_list(arg, limit)
    elif isinstance(arg, str):
        if len(arg) > limit-2:
            arg = arg[:limit-5] + '...'
        return '"' + arg + '"'
    else:
        item = repr(arg)
        if len(item) > limit:
            item = item[:limit-3] + '...'
        return item
