"""
Build tables with fake data for testing purposes.
"""

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
        If the element is a number then it represents the output range.
        The element type determines the output type:
        - A float will create floats
        - An int will create integers
        If the element is a tuple then the constituent values are used as
        inputs for a gaussian distribution where the first item is mu (mean)
        and the second sigma (std). The type of the mean will determine the
        output (float or int).
    k : int, default 100
        Number of rows to create.
    """
    data = dict()

    is_tup = lambda x: isinstance(x, tuple)
    is_int = lambda x: isinstance(x, int)
    is_flt = lambda x: isinstance(x, float)

    ints = [i for i in recipe if is_int(i) or (is_tup(i) and is_int(i[0]))]
    floats = [i for i in recipe if is_flt(i) or (is_tup(i) and is_flt(i[0]))]

    for i, val in enumerate(ints):
        formula = lambda x: random.randint(0, x)
        if is_tup(val):
            formula = lambda x: int(random.gauss(x[0], x[1]))
        data[f'int{i}'] = [formula(val) for i in range(k)]

    for i, val in enumerate(floats):
        formula = lambda x: random.random() * x
        if is_tup(val):
            formula = lambda x: random.gauss(x[0], x[1])
        data[f'float{i}'] = [formula(val) for i in range(k)]
    return pd.DataFrame(data)
