import decimal
import json
import uuid

import pandas as pd
from jinja2 import Environment, PackageLoader

from flatbread.render.config import DisplayConfig


# MARK: Template
class TemplateManager:
    """Manages rendering templates"""
    def __init__(self):
        self._env = Environment(loader=PackageLoader("flatbread", "render"))

    def render(self, spec: dict, config: DisplayConfig) -> str:
        template = self._env.get_template("template.jinja.html")
        return template.render(
            data=self._serialize_to_json(spec),
            config=config,  # Pass entire config
            id=f"id-{uuid.uuid4()}"
        )

    def _serialize_to_json(self, data: dict) -> str:
        """Safely serialize data to JSON for JS consumption"""
        return json.dumps(data, separators=(',', ':'), default=self._json_serialize)

    @staticmethod
    def _json_serialize(obj):
        """Handle special types for JSON serialization"""
        if isinstance(obj, pd.Timestamp):
            timestamp = obj.isoformat()
            if timestamp.endswith('T00:00:00'):
                return timestamp[:-9]
            return timestamp
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (pd.Index, pd.arrays.IntervalArray)):
            return list(obj)
        if pd.isna(obj):
            return None
        if isinstance(obj, pd._libs.interval.Interval):
            return str(obj)
        if hasattr(obj, 'dtype'):
            return obj.item()
        return str(obj)
