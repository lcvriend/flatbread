"""
Toolbox for manipulating series.
"""

from typing import Any

import pandas as pd


def add_category(
    s: pd.Series,
    category: Any,
) -> pd.Index:
    "Add ``category`` to ``s`` if it's dtype is categorical."
    def add_cat(s, cats):
        if isinstance(s.dtype, pd.CategoricalDtype):
            cats = [item for item in cats if item not in s.cat.categories]
            s = s.cat.add_categories(cats)
        return s
    category = [category] if pd.api.types.is_scalar(category) else category
    return add_cat(s, category)