import json
from collections import namedtuple
from pathlib import Path


here = Path(__file__).resolve().parent

with open(here / 'config.json', 'r', encoding='utf8') as f:
    config = json.load(f)

if not config['settings']['store_output_in_cwd']:
    path = here.parent
else:
    path = Path()

items = {k:path / v for k,v in config['paths'].items()}
Paths = namedtuple('Paths', items.keys())
PATHS = Paths(**items)
