from dataclasses import dataclass, field
from typing import Any

@dataclass
class DisplayConfig:
    # Data handling
    locale: str | None = None
    na_rep: str = "-"
    margin_labels: list[str] = field(default_factory=list)

    # Layout control
    collapse_columns: bool = None
    max_rows: int = 30
    max_columns: int = 30
    trim_size: int = 5
    separator: str = "..."

    # Border controls
    hide_column_borders: bool = False
    hide_row_borders: bool = False
    hide_thead_border: bool = False
    hide_index_border: bool = False

    # Visual effects
    show_hover: bool = False

    @classmethod
    def from_defaults(
        cls,
        defaults: dict[str, Any],
        data_attrs: dict|None = None,
    ) -> "DisplayConfig":
        """Create config instance from defaults dict"""
        if not defaults:
            return cls()

        margin_labels = []
        if totals := defaults.get('totals', {}):
            margin_labels.append(totals.get('label', 'Totals'))
        if subtotals := defaults.get('subtotals', {}):
            margin_labels.append(subtotals.get('label', 'Subtotals'))
        if percentages := defaults.get('percentages', {}):
            margin_labels.append(percentages.get('label_pct', 'pct'))

        # Add ignored keys from attrs
        if data_attrs and (fb_attrs := data_attrs.get('flatbread')):
            if totals_attrs := fb_attrs.get('totals'):
                if ignore_keys := totals_attrs.get('ignore_keys'):
                    margin_labels.extend(ignore_keys)
            if percentages_attrs := fb_attrs.get('percentages'):
                if ignore_keys := percentages_attrs.get('ignore_keys'):
                    margin_labels.extend(ignore_keys)

        # Extract values from defaults, using dataclass defaults if not present
        return cls(
            locale = defaults.get("locale", cls.locale),
            na_rep = defaults.get("na_rep", cls.na_rep),
            margin_labels = list(set(margin_labels)),
            collapse_columns=defaults.get("collapse_columns", cls.collapse_columns),
            max_rows=defaults.get("max_rows", cls.max_rows),
            max_columns=defaults.get("max_columns", cls.max_columns),
            trim_size=defaults.get("trim_size", cls.trim_size),
            separator=defaults.get("separator", cls.separator),
            hide_column_borders=defaults.get("hide_column_borders", cls.hide_column_borders),
            hide_row_borders=defaults.get("hide_row_borders", cls.hide_row_borders),
            hide_thead_border=defaults.get("hide_thead_border", cls.hide_thead_border),
            hide_index_border=defaults.get("hide_index_border", cls.hide_index_border),
            show_hover=defaults.get("show_hover", cls.show_hover)
        )
