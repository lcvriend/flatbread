import pandas as pd
from jinja2 import Environment, PackageLoader
import flatbread.render.pandas_to_table_spec
from IPython.display import display, HTML
import uuid

class PitaDisplayMixin:
    _env = Environment(loader=PackageLoader('flatbread', 'render'))
    _template_name = 'template.jinja.html'

    def _repr_html_(self):
        template = self._env.get_template(self._template_name)
        data = self._get_table_spec()
        return  template.render(data=data, id=f"id-{uuid.uuid4()}")

    def _get_table_spec(self):
        isSeries = isinstance(self._obj, pd.Series)
        data = self._obj.to_frame() if isSeries else self._obj
        return data.to_table_spec.as_json()
