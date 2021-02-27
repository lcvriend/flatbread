import re
from functools import wraps


def dicts_to_tuples(func):
    """
    Convert key-word arguments containing a dict into a list of key-value tuples. Used for converting the styling stored in the config into the format
    that pandas wants it.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        for k1,v1 in kwargs.items():
            if isinstance(v1, dict):
                kwargs[k1] = [(k2,v2) for k2,v2 in v1.items()]
        return func(*args, **kwargs)
    return wrapper


def extract_content_from_html(html, tag):
    "Extract content between ``tag`` from ``html``."
    regex = re,compile(f"<{tag}.*>([\n\s\w\W]*)</{tag}>")
    html = regex.search(html).group(1)
    return re.sub("\s{2,}", '\n', html)
