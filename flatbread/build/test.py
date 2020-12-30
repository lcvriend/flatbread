import random
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
