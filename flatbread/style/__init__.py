"""
Functions for building up pivot table styling.
"""

from collections import defaultdict
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)


import pandas as pd
from pandas.core.dtypes.inference import is_float, is_integer
from pandas.io.formats.style import Styler
from jinja2 import Environment, ChoiceLoader, FileSystemLoader

import flatbread.style._helpers as helpers
from flatbread.style.table import add_table_style, add_flatbread_style
from flatbread.style.levels import add_level_dividers
from flatbread.style.subtotals import add_subtotals_style
from flatbread.config import HERE


class FlatbreadStyler(Styler):
    env = Environment(
        loader=ChoiceLoader([
            FileSystemLoader(HERE / "style/templates"),
            Styler.loader,
        ])
    )
    template = env.get_template("flatbread.tpl")

    def __init__(
        self,
        pivottable,
        *args,
        **kwargs,
    ):
        self.pita = pivottable
        super().__init__(self.pita.df, *args, **kwargs)

        def default_display_func(x):
            if self.na_rep is not None and pd.isna(x):
                return self.na_rep
            elif is_float(x):
                n_precision = len(str(int(x))) + self.precision
                display_format = f"{x:.{n_precision}n}"
                return display_format
            elif is_integer(x):
                display_format = f"{x:n}"
                return display_format
            else:
                return x

        self._display_funcs = defaultdict(lambda: default_display_func)
        self.pita_styles = self._get_styles()
        self.flatbread_styles = add_flatbread_style(self.uuid, **kwargs)

    def to_html(self, path=None):
        "Return html, if ``path`` is given write to path instead."
        html = self.render()
        if path is not None:
            with open(path, 'w', encoding='utf8') as f:
                f.write(html)
            return None
        return html

    @helpers.dicts_to_tuples
    def _get_styles(self, **kwargs):
        "Build and combine all styling, then return it."
        table = add_table_style(**kwargs)
        levels = add_level_dividers(
            self.pita.df,
            self.uuid,
            totals_name=self.pita.totals_name,
            **kwargs
        )
        subtotals = add_subtotals_style(
            self.pita.df,
            self.uuid,
            subtotals_name=self.pita.subtotals_name,
            **kwargs
        )
        return table + levels + subtotals

    def set_table_styles(self, *args, axis=0, **kwargs):
        super().set_table_styles(*args, axis=axis, overwrite=False)
        self.pita_styles = self._get_styles(**kwargs)
        self.flatbread_styles = add_flatbread_style(self.uuid, **kwargs)

    def render(self, **kwargs):
        if self.table_styles is not None:
            self.table_styles.extend(self.pita_styles)
        else:
            self.table_styles = self.pita_styles
        return super().render(
            flatbread_styles=self.flatbread_styles,
            table_title=self.pita.title,
            caption=self.pita.caption,
            **kwargs
        )
