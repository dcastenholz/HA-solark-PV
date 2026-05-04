"""Sensor class types for SolArk."""

from enum import Enum, auto


# TODO - Can we just set the class in the map entry???
class SensorClass(Enum):
    """Sensor implementation classes."""

    STATIC_VALUE = auto()
    COORDINATOR = auto()
    DATETIME = auto()
    TOU_TIME = auto()
    METRICS = auto()
    CONFIG = auto()
