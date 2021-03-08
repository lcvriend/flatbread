import re
from functools import wraps


def dicts_to_tuples(func):
    """
    Decorator for converting key-word arguments containing a dict into a list
    of key-value tuples. Used for converting the styling stored in the config 
    into the format that pandas wants it.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs = _dicts_to_tuples(kwargs)
        return func(*args, **kwargs)
    return wrapper


def _dicts_to_tuples(dct):
    for k1,v1 in dct.items():
        if isinstance(v1, dict):
            dct[k1] = [(k2,v2) for k2,v2 in v1.items()]
    return dct


def add_remove_important(rules, add_remove):
    """
    Add or remove '!important' to the prop values for each rule in ``rules``.
    """
    def add_important_to_props(props):
        return [
            (prop,f"{val} !important")
            for prop, val in props
            if '!important' not in val
        ]

    regex = re.compile(r"\s!important")
    remove_important = lambda p: regex.sub('', p)
    def remove_important_from_props(props):
        return [(prop,remove_important(val)) for prop, val in props]

    selector = dict(
        add = add_important_to_props,
        remove = remove_important_from_props,
    )
    func = selector[add_remove]
    return [{
        'selector': rule['selector'],
        'props': func(rule['props'])
        } for rule in rules
    ]


def clean_up_double_css_rules(rules):
    """
    Go through ``rules`` (list of selector/properties) and combine duplicates.
    If selectors occur more than once, then combine them.
    If a property within a selector occurs more than once, keep only last value.
    """
    def keep_last_prop(props):
        props = {prop:val for prop,val in props}
        return [(prop,val) for prop,val in props.items()]
    dct = {}
    if not rules:
        return []
    for rules in rules:
        selector = rules['selector']
        props = rules['props']
        if selector in dct:
            dct[selector]= keep_last_prop(dct[selector] + props)
        else:
            dct[selector] = keep_last_prop(props)
    return [{'selector': k, 'props': v} for k,v in dct.items()]


def drop_rules_with_no_props(func):
    """
    Remove rules with no props from output.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return _drop_rules_with_no_props(result)
    return wrapper


def _drop_rules_with_no_props(rules):
    return [rule for rule in rules if rule['props']]


def extract_content_from_html(html, tag):
    "Extract content between ``tag`` from ``html``."
    regex = re,compile(f"<{tag}.*>([\n\s\w\W]*)</{tag}>")
    html = regex.search(html).group(1)
    return re.sub("\s{2,}", '\n', html)
