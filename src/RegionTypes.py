
from typing import List, TypedDict

class Cell(TypedDict):
    cellX: int
    cellY: int

# Holds information for a region
class RegionInfo(TypedDict):
    description: str
    color: str
    cells: List[Cell]
