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

    def render(self, spec: str, config: DisplayConfig) -> str:
        template = self._env.get_template("template.jinja.html")
        html = template.render(
            data=spec,
            config=config,
            id=f"id-{uuid.uuid4()}"
        )
        return html
