import uuid
import pandas as pd
from jinja2 import Environment, PackageLoader

from flatbread import DEFAULTS
import flatbread.render.pandas_to_table_spec


class PitaDisplayMixin:
    _env = Environment(loader=PackageLoader('flatbread', 'render'))
    _template_name = 'template.jinja.html'
    _as_frame = None

    def _repr_html_(self):
        template = self._env.get_template(self._template_name)
        data = self._get_table_spec()
        return template.render(
            data = data,
            defaults = DEFAULTS,
            id = f"id-{uuid.uuid4()}",
        )

    @property
    def as_frame(self):
        if self._as_frame is None:
            is_series = isinstance(self._obj, pd.Series)
            self._as_frame = self._obj.to_frame() if is_series else self._obj
        return self._as_frame

    def _get_table_spec(self):
        return self.as_frame.to_table_spec.as_json()

    def set_format_options(self, options):
        """
        Set custom format options for the display.

        Parameters
        ----------
        options : dict, callable
            A dictionary where keys are column names and values are format option dictionaries or a callable that takes a DataFrame and returns a dictionary.

        Returns
        -------
        self
            Returns the object itself for method chaining.

        Examples
        --------
        >>> df.pita.set_format_options({
        ...     'price': {'style': 'currency', 'currency': 'USD'},
        ...     'percentage': {'style': 'percent', 'maximumFractionDigits': 2}
        ... })
        """
        if callable(options):
            options = options(self.as_frame)
        self.as_frame.to_table_spec.set_format_options(options)
        return self
