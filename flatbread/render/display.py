from typing import Any

from jinja2 import Environment, PackageLoader

from flatbread import DEFAULTS
from flatbread.render.config import DisplayConfig
from flatbread.render.template import TemplateManager
from flatbread.render.tablespec import TableSpecBuilder


class PitaDisplayMixin:
    """Mixin for displaying pandas objects using data-viewer"""
    _env = Environment(loader=PackageLoader('flatbread', 'render'))
    _template_name = 'template.jinja.html'

    @property
    def _config(self) -> DisplayConfig:
        if not hasattr(self, '_display_config'):
            self._display_config = DisplayConfig.from_defaults(
                DEFAULTS,
                self._obj.attrs if hasattr(self._obj, 'attrs') else None
            )
        return self._display_config

    @property
    def _table_spec_builder(self) -> TableSpecBuilder:
        """Lazy initialization of spec builder"""
        if not hasattr(self, '_spec_builder'):
            self._spec_builder = TableSpecBuilder(self._obj)
        return self._spec_builder

    @property
    def _template_manager(self) -> TemplateManager:
        """Lazy initialization of template manager"""
        if not hasattr(self, '_template_mgr'):
            self._template_mgr = TemplateManager()
        return self._template_mgr

    def configure_display(self, **kwargs) -> "PitaDisplayMixin":
        """Configure display options"""
        self._config.update(**kwargs)
        return self

    def set_locale(self, locale: str) -> "PitaDisplayMixin":
        """Set the locale for number/date formatting"""
        self._config.locale = locale
        return self

    def set_na_rep(self, na_rep: str) -> "PitaDisplayMixin":
        """Set null value representation"""
        self._config.na_rep = na_rep
        return self

    def set_max_rows(self, max_rows: int) -> "PitaDisplayMixin":
        """Set maximum rows before truncating"""
        self._config.max_rows = max_rows
        return self

    def set_max_columns(self, max_columns: int) -> "PitaDisplayMixin":
        """Set maximum columns before truncating"""
        self._config.max_columns = max_columns
        return self

    def set_trim_size(self, n: int) -> "PitaDisplayMixin":
        """Set number of items to show when truncated"""
        self._config.trim_size = n
        return self

    def set_separator(self, sep: str) -> "PitaDisplayMixin":
        """Set truncation indicator"""
        self._config.separator = sep
        return self

    def hide_borders(self, hide: bool = True) -> "PitaDisplayMixin":
        """Hide all borders"""
        self._config.hide_column_borders = hide
        self._config.hide_row_borders = hide
        self._config.hide_thead_border = hide
        self._config.hide_index_border = hide
        return self

    def show_column_borders(self, show: bool = True) -> "PitaDisplayMixin":
        """Show/hide vertical column borders"""
        self._config.hide_column_borders = not show
        return self

    def show_row_borders(self, show: bool = True) -> "PitaDisplayMixin":
        """Show/hide horizontal row borders"""
        self._config.hide_row_borders = not show
        return self

    def show_header_border(self, show: bool = True) -> "PitaDisplayMixin":
        """Show/hide header bottom border"""
        self._config.hide_thead_border = not show
        return self

    def show_index_border(self, show: bool = True) -> "PitaDisplayMixin":
        """Show/hide index right border"""
        self._config.hide_index_border = not show
        return self

    def show_hover(self, show: bool = True) -> "PitaDisplayMixin":
        """Enable row hover effect"""
        self._config.show_hover = show
        return self

    def collapse_columns(self, collapse: bool = True) -> "PitaDisplayMixin":
        """Collapse column headers"""
        self._config.collapse_columns = collapse
        return self

    def set_section_levels(self, levels: int) -> "PitaDisplayMixin":
        """Set index levels to show as sections"""
        self._config.section_levels = levels
        return self

    def set_margin_labels(self, *labels: str) -> "PitaDisplayMixin":
        """Set labels to be treated as margins"""
        self._config.margin_labels = list(labels)
        return self

    def format(
        self,
        column: str,
        format_spec: str | dict[str, Any],
    ) -> "PitaDisplayMixin":
        """Set format options for a column

        Parameters
        ----------
        column : str
            Column to format
        format_spec : str | dict
            Either a preset name (e.g. 'currency') or format options dict

        Returns
        -------
        PitaDisplayMixin
            Self for method chaining
        """
        self._table_spec_builder.set_format(column, format_spec)
        return self

    def _repr_html_(self) -> str:
        """Generate HTML representation for Jupyter display"""
        spec = self._table_spec_builder.build_spec()
        return self._template_manager.render(spec, self._config)

    def get_table_spec(self) -> dict:
        """
        Get the raw table specification as a dictionary.

        Returns
        -------
        dict
            Dictionary containing the complete table specification including:
            - values: 2D array of cell values
            - columns: Column labels
            - index: Row labels
            - columnNames: Names for column levels
            - indexNames: Names for index levels
            - dtypes: Data types per column
            - formatOptions: Format configuration per column
        """
        return self._table_spec_builder.build_spec()

    def get_table_spec_json(self) -> str:
        """
        Get the table specification as a JSON string.

        Returns
        -------
        str
            JSON string containing the complete table specification.
            The JSON is serialized using the same custom serialization logic
            used for display, handling pandas-specific types like Timestamps
            and Intervals.
        """
        spec = self.get_table_spec()
        return self._template_manager._serialize_to_json(spec)
