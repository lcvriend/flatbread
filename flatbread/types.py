from typing import Literal, TypeAlias

Axis: TypeAlias = int | Literal["index", "columns", "both"] | None
Level: TypeAlias = int | str
