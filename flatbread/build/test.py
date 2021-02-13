import random
import re
import string

import pandas as pd


CATEGORIES = dict(
    cat1     = ['A', 'B'],
    cat2     = ['x', 'y', 'z'],
    cat3     = [1, 2],
    color    = ['red', 'blue', 'green', 'yellow'],
    shape    = ['round', 'square', 'triangle'],
    material = ['plastic', 'metal', 'wood'],
    taste    = ['sweet', 'sour', 'salty', 'bitter', None],
    smell    = ['fruity', 'pungent', 'nutty', 'chemical', 'minty', None],
    touch    = ['smooth', 'rough', None]
)


def dataset(k=100, categories=CATEGORIES, to_categories=False, seed=None):
    if seed is not None:
        random.seed = seed

    populations = {
        key:{item:random.randint(1,40) for item in items}
        for key, items in categories.items()
    }
    data = {key:random.choices(
        list(pop.keys()),
        weights=list(pop.values()),
        k=k) for key, pop in populations.items()
    }
    data.update(dict(weight=[random.randint(5, 200) for i in range(k)]))
    df = pd.DataFrame.from_dict(data)
    if to_categories:
        categoricals = {
            key:pd.CategoricalDtype(
                [val for val in values if val is not None],
                ordered=True,
            )
            for key, values in categories.items()
        }
        df = df.astype(categoricals)
    return df


def dataset_from_recipe(
    cats_recipe,
    k=100,
    to_categorical=False,
    n_chars=3
):
    alphabet_lower = list(string.ascii_lowercase)
    alphabet_upper = list(string.ascii_uppercase)
    vowels = 'aeiou'

    categories = dict()
    all_values = set()
    for i, n_cats in enumerate(cats_recipe):
        get_chars = lambda: random.sample(alphabet_lower, k=n_chars)
        choices = set()
        while len(choices) < n_cats:
            proposed_value = ''.join(get_chars())
            if proposed_value in all_values:
                continue
            if not any(char in vowels for char in proposed_value):
                continue
            choices.add(proposed_value)
        all_values.update(choices)
        if isinstance(n_cats, float):
            choices.add(None)
        categories[alphabet_upper[i]] = choices

    populations = {
        key:{item:random.randint(1,40) for item in items}
        for key, items in categories.items()
    }
    data = {key:random.choices(
        list(pop.keys()),
        weights=list(pop.values()),
        k=k) for key, pop in populations.items()
    }
    data.update(dict(num=[random.randint(5, 200) for i in range(k)]))
    df = pd.DataFrame.from_dict(data)
    if to_categorical:
        categoricals = {
            key:pd.CategoricalDtype(
                [val for val in values if val is not None],
                ordered=True,
            )
            for key, values in categories.items()
        }
        df = df.astype(categoricals)
    return df


def extract_part(html, part):
    html = re.search(f"<{part}.*>[\w\W]*</{part}>", html).group()
    html = re.sub("\s{2,}", '\n', html)
    print(html)
    return None
