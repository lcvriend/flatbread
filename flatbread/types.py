from typing import Union, Hashable, Iterable


AxisAlias = Union[str, int]
IndexName = Hashable
LevelAlias = Union[str, int, None]
LevelsAlias = Union[LevelAlias, Iterable[LevelAlias]]
