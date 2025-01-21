from dataclasses import dataclass, field
from typing import Any

@dataclass
class DisplayConfig:
    # Data handling
    locale: str | None = None
    na_rep: str = "-"
    margin_labels: list[str] = field(default_factory=lambda: ["Totals", "Subtotals"])

    # Layout control
    section_levels: int = 0
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
    def from_defaults(cls, defaults: dict[str, Any]) -> "DisplayConfig":
        """Create config instance from defaults dict"""
        if not defaults:  # If no defaults provided, use dataclass defaults
            return cls()

        # Extract values from defaults, using dataclass defaults if not present
        return cls(
            locale=defaults.get("locale", cls.locale),
            na_rep=defaults.get("na_rep", cls.na_rep),
            margin_labels=defaults.get("margin_labels", cls.margin_labels),
            section_levels=defaults.get("section_levels", cls.section_levels),
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
