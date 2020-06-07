from flatbread.utils.types import AxisAlias

AXES_ALIAS = {
    0: 0,
    1: 1,
    2: 2,
    'index': 0,
    'rows': 0,
    'columns': 1,
    'both': 2,
    'all': 2,
}


def get_axis_number(axis: AxisAlias) -> int:
    assert (axis in AXES_ALIAS), f"Axis should be one of {AXES_ALIAS.keys()}"
    return AXES_ALIAS[axis]
