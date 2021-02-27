import random
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


def dataset_categoricals(
    recipe,
    k=100,
    to_categorical=False,
    n_chars=3
):
    """
    Build a test dataset containing categorical data.

    Arguments
    ---------
    recipe : list of int/float
        Each element in the list represents a column.
        The value represents the number of categories.
        If the value is a float, then it will have missing values.
    k : int, default 100
        Number of rows to create.
    to_categorical : bool, default False
        Whether to convert the columns to categorical dtype.
    n_chars : int, default 3
        The number of characters the values should get.
    """
    alphabet_lower = list(string.ascii_lowercase)
    alphabet_upper = list(string.ascii_uppercase)
    vowels = 'aeiou'

    categories = dict()
    all_values = set()
    for i, n_cats in enumerate(recipe):
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


def dataset_numbers(recipe, k=100):
    """
    Build a test dataset containg floats and/or integers.

    Arguments
    ---------
    recipe : list of int/float
        Each element in the list represents a column.
        The value represents the number range.
        If the value is a float, then the output will be floats.
        If the value is an int, then the output will be integers.
    k : int, default 100
        Number of rows to create.
    """
    data = dict()
    ints = [i for i in recipe if isinstance(i, int)]
    floats = [i for i in recipe if isinstance(i, float)]

    for i, val in enumerate(ints):
        data[f'int{i}'] = [random.randint(0, val) for i in range(k)]

    for i, val in enumerate(floats):
        data[f'float{i}'] = [random.random() * val for i in range(k)]
    return pd.DataFrame(data)
