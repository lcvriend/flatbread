from typing import Any, Callable

import pandas as pd

from flatbread.render.constants import DEFAULT_DTYPES, DTYPE_TO_PRESETS, SMART_FORMATS


ColumnFormat = str | dict[str, Any]
ColumnFormats = dict[str, ColumnFormat] | list[ColumnFormat]
FormatSpec = ColumnFormats | Callable[[pd.DataFrame], ColumnFormats]


class TableSpecBuilder:
    """Converts pandas objects to data-viewer specifications"""
    def __init__(self, data: pd.DataFrame | pd.Series):
        self._data = data.to_frame() if isinstance(data, pd.Series) else data
        self._format_options: dict[str, str | dict[str, Any]] = {}

    def build_spec(self) -> dict:
        return {
            "values": self._prepare_values(),
            "columns": self._prepare_columns(),
            "index": self._prepare_index(),
            "columnNames": self._data.columns.names,
            "indexNames": self._data.index.names,
            "dtypes": self._prepare_dtypes(),
            "formatOptions": self._prepare_format_options()
        }

    def _prepare_values(self) -> list[list]:
        """Convert DataFrame values to nested list format"""
        return self._data.values.tolist()

    def _prepare_columns(self) -> list:
        """Prepare column labels"""
        return list(self._data.columns)

    def _prepare_index(self) -> list:
        """Prepare index labels"""
        return list(self._data.index)

    def _prepare_dtypes(self) -> list[str]:
        """Convert pandas dtypes to simplified type names"""
        return [DEFAULT_DTYPES.get(str(dtype), 'str') for dtype in self._data.dtypes]

    def _prepare_format_options(self) -> list[str | dict[str, Any] | None]:
        """Get format options for each column"""
        return [
            self._get_format_for_column(col)
            for col in self._data.columns
        ]

    def _get_format_for_column(self, column: Any) -> ColumnFormat | None:
        """Get format for a column, checking explicit formats then smart formats"""
        # First check explicit formats
        if format_spec := self._format_options.get(column):
            return format_spec
        # Then try smart detection
        return self._detect_smart_format(column)

    def _detect_smart_format(self, column: Any) -> ColumnFormat | None:
        """Detect format based on column name patterns"""
        if isinstance(column, tuple):
            # Check each part of tuple
            for part in column:
                if result := self._check_format_pattern(str(part)):
                    return result
        else:
            # Check single value
            if result := self._check_format_pattern(str(column)):
                return result
        return None

    def _check_format_pattern(self, value: str) -> ColumnFormat | None:
        """Check if value matches any format pattern"""
        value = value.lower()

        # Iterate through format types
        for format_type in SMART_FORMATS.values():
            # Check if value matches any of the labels for this format
            for label in format_type['labels']:
                if label in value:
                    return format_type['options']
        return None

    def set_format(self, column: str, format_spec: ColumnFormat) -> None:
        if isinstance(format_spec, str):
            pandas_dtype = str(self._data[column].dtype)
            simple_dtype = DEFAULT_DTYPES.get(pandas_dtype, 'str')
            valid_presets = DTYPE_TO_PRESETS.get(simple_dtype, set())
            if format_spec not in valid_presets:
                valid = ", ".join(sorted(valid_presets))
                raise ValueError(
                    f"Invalid preset '{format_spec}' for dtype {pandas_dtype} "
                    f"(mapped to {simple_dtype}). Valid presets are: {valid}"
                )
        self._format_options[column] = format_spec

    def set_formats(self, formats: FormatSpec]) -> None:
        """Set multiple column formats at once.

        Parameters
        ----------
        formats : dict, list or callable
            Either dict mapping column names to format specs,
            a list of length columns,
            or function that takes DataFrame and returns such dict
        """
        if callable(formats):
            formats = formats(self._data)

        if isinstance(formats, list):
            if len(formats) != len(self._data.columns):
                raise ValueError(f"Expected {len(self._data.columns)} formats, got {len (formats)}")
            formats = dict(zip(self._data.columns, formats))

        for column, format_spec in formats.items():
            self.set_format(column, format_spec)
