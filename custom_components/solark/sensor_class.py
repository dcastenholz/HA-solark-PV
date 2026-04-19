from enum import Enum, auto


class SensorClass(Enum):
    STATIC_VALUE = auto()
    NORMAL = auto()
    DATETIME = auto()
    TOU_TIME = auto()
    METRICS = auto()
