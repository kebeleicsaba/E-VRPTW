from enum import Enum, auto

class HeuristicMode(Enum):
    CONSTRUCT_ONLY = auto()
    CONSTRUCT_LOCAL = auto()
    CONSTRUCT_ALNS = auto()