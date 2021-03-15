"""
Styling for flatbread's pivot tables. Contains
:py:class:`flatbread.style.FlatbreadStyler` which subclasses :py:class:`pandas.io.formats.style.Styler`.
Modules contain functions for building up the styling for flatbread's tables:

:py:mod:`flatbread.style.levels` :
    Add borders between groups and total rows/columns.
:py:mod:`flatbread.style.subtotals` :
    Add styling for subtotal rows/columns.
:py:mod:`flatbread.style.table` :
    Add styling for table and table container.
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
from uuid import uuid4


import pandas as pd
from pandas.core.dtypes.inference import is_float, is_integer
from pandas.io.formats.style import Styler
from jinja2 import Environment, ChoiceLoader, FileSystemLoader

import flatbread.style._helpers as helpers
from flatbread.style.table import (
    add_table_style,
    add_column_styles,
    add_flatbread_style,
)
from flatbread.style.levels import add_level_dividers
from flatbread.style.totals import add_totals_style
from flatbread.style.subtotals import add_subtotals_style
from flatbread.config import HERE, load_settings


class FlatbreadStyler(Styler):
    env = Environment(
        loader=ChoiceLoader([
            FileSystemLoader(HERE / "style/templates"),
            Styler.loader,
        ])
    )
    template = env.get_template("flatbread.tpl")

    @load_settings({'general': [
        'add_important_to_props_on_render',
        'add_important_to_props_on_export',
    ]})
    def __init__(
        self,
        pivottable,
        *args,
        add_important_to_props_on_render=None,
        add_important_to_props_on_export=None,
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
        self.pita_styles = {}
        self.column_styles = {}
        self.na_rep = self.pita.na_rep
        self.add_important_to_props_on_render = add_important_to_props_on_render
        self.add_important_to_props_on_export = add_important_to_props_on_export

    def to_html(self, path=None):
        "Return html, if ``path`` is given write to path instead."
        html = self.render(export=True)
        if path is not None:
            with open(path, 'w', encoding='utf8') as f:
                f.write(html)
            return None
        return html

    @helpers.dicts_to_tuples
    @helpers.drop_rules_with_no_props
    def _get_styles(self, **kwargs):
        "Build and combine all styling, then return it."
        table = add_table_style(**kwargs)
        levels = add_level_dividers(
            self.pita.df,
            self.uuid,
            totals_name=self.pita.totals_name,
            **kwargs
        )
        totals = add_totals_style(
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
        return table + levels + totals + subtotals

    def set_table_styles(self, *args, axis=0, **kwargs):
        if args:
            super().set_table_styles(*args, axis=axis, overwrite=False)
        if kwargs:
            self.pita_styles = kwargs
        return self

    def clear(self):
        super().clear()
        self.pita_styles = dict()

    def render(self, export=False, **kwargs):
        self.data = self.pita.df
        self.index = self.data.index
        self.columns = self.data.columns

        kwargs = {} if kwargs is None else kwargs
        style_pivottable = self._get_styles(
            **self.pita_styles, **kwargs)
        style_container = add_flatbread_style(self.uuid, **kwargs)

        if self.table_styles is not None:
            self.table_styles.extend(style_pivottable)
        else:
            self.table_styles = style_pivottable

        # because all styling is built up at in one go
        # we need to clean up duplicates
        # this could be avoided if set_table_styles
        # only targets the items that are actually changed
        # this would require a restructuring of the code
        self.table_styles = helpers.clean_up_double_css_rules(self.table_styles)

        # vscode (insiders atm) overrides the css from flatbread
        # in order to prevent this, an !important is added to the prop values
        # this is can be turned on/off globally through CONFIG
        perf = (
            self.add_important_to_props_on_export
            if export else self.add_important_to_props_on_render)
        do = 'add' if perf else 'remove'
        self.table_styles = helpers.add_remove_important(self.table_styles, do)

        colstyles = add_column_styles(
            self.pita.df,
            **self.pita_styles,
            **kwargs,
        )
        super().set_table_styles(colstyles, overwrite=False)

        return super().render(
            flatbread_styles=style_container,
            table_title=self.pita.title,
            caption=self.pita.caption,
            **kwargs
        )
