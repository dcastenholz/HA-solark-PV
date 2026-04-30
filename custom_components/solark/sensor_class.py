from enum import Enum, auto


class SensorClass(Enum):
    STATIC_VALUE = auto()
    COORDINATOR = auto()
    DATETIME = auto()
    TOU_TIME = auto()
    METRICS = auto()
