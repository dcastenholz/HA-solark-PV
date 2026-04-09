from enum import Enum, auto


class SensorClass(Enum):
    BASE = auto()
    NORMAL = auto()
    DATETIME = auto()
    TOU_TIME = auto()
