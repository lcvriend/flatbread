import json
import urllib
from decimal import Decimal
from pathlib import Path

import pandas as pd


DEFAULT_DTYPES: dict[str, str] = {
    'object':         'str',
    'string':         'str',
    'bool':           'bool',
    'boolean':        'bool',
    'category':       'category',
    'datetime64[ns]': 'datetime',
    'float64':        'float',
    'Float64':        'float',
    'int8':           'int',
    'int16':          'int',
    'int32':          'int',
    'int64':          'int',
    'Int8':           'int',
    'Int16':          'int',
    'Int32':          'int',
    'Int64':          'int',
}


@pd.api.extensions.register_dataframe_accessor("to_table_spec")
class DataFrameToTableSpec:
    """
    A pandas DataFrame accessor that converts a DataFrame to a table specification.

    This accessor provides methods to convert a DataFrame to a dictionary-based
    table specification, which can be saved as JSON or converted to a URL.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    >>> spec = df.to_table_spec()
    >>> json_spec = df.to_table_spec.as_json()
    >>> df.to_table_spec('output.json')
    """
    def __init__(self, pandas_obj) -> None:
        self._obj = pandas_obj
        self._dtypes = DEFAULT_DTYPES.copy()

    def __call__(
        self, path: Path|str|None,
        format_options: list[dict[str,str]|None]|None = None,
    ) -> dict|str|None:
        """
        Convert the DataFrame to a table specification and optionally save it to a file.

        Parameters
        ----------
        path : Path or str, optional
            The file path where the table specification should be saved as JSON.
            If None, the specification is returned as a dictionary.
        format_options: list of dicts or None, optional
            Formatting options for the columns.

        Returns
        -------
        dict or str or None
            If path is None, returns the table specification as a dictionary.
            If path is provided, saves the specification to the file and returns None.
        """
        spec = self._get_spec(format_options)
        if path is None:
            return spec
        json_contents = self._serialize_spec_to_json(spec)
        Path(path).write_text(json_contents, encoding='utf8')

    def as_json(self) -> str:
        """
        Convert the DataFrame to a table specification and return it as a JSON string.

        Returns
        -------
        str
            The table specification as a JSON string.
        """
        spec = self._get_spec()
        json_contents = self._serialize_spec_to_json(spec)
        return json_contents

    def as_data_url(self) -> str:
        """
        Convert the DataFrame to a table specification and return it as a data URL.

        Returns
        -------
        str
            The table specification as a data URL.
        """
        json_contents = self.as_json()
        data = urllib.parse.quote(json_contents, encoding='utf-8')
        return f"data:application/json,{data}"

    def _get_spec(
        self,
        format_options: list[dict[str,str]|None]|None = None,
    ) -> dict:
        """
        Generate the table specification from the DataFrame.

        Returns
        -------
        dict
            The table specification as a dictionary.
        """
        spec = self._obj.to_dict(orient='split')
        spec['values'] = spec.pop('data')
        spec['indexNames'] = self._obj.index.names
        spec['columnNames'] = self._obj.columns.names
        spec['dtypes'] = self._obj.dtypes.pipe(self.get_dtypes_as_list)
        if format_options is not None:
            spec['formatOptions'] = format_options
        return spec

    def _serialize_spec_to_json(self, spec) -> str:
        """
        Serialize the table specification to a JSON string.

        Parameters
        ----------
        spec : dict
            The table specification dictionary.

        Returns
        -------
        str
            The serialized JSON string.
        """
        return json.dumps(spec, separators=(',', ':'), default=self.serialize)

    @staticmethod
    def serialize(item):
        """
        Serialize special types (Timestamp, Decimal) for JSON conversion.

        Parameters
        ----------
        item : Any
            The item to be serialized.

        Returns
        -------
        str or float
            The serialized representation of the item.
        """
        if isinstance(item, pd.Timestamp):
            timestamp = item.isoformat()
            if timestamp.endswith('T00:00:00'):
                return timestamp[:-9]
            return timestamp
        if isinstance(item, Decimal):
            return float(item)

    def get_dtypes_as_list(self, s: pd.Series) -> list[str]:
        """
        Convert a Series of dtypes to a list of simplified type names.

        Parameters
        ----------
        s : pd.Series
            A Series containing DataFrame column dtypes.

        Returns
        -------
        list of str
            A list of simplified type names.
        """
        get_dtype = lambda item: self._dtypes.get(str(item), 'str')
        return s.map(get_dtype).to_list()
