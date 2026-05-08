"""Binary sensor class types for SolArk."""

from enum import Enum, auto


class BinarySensorClass(Enum):
    """Binary sensor implementation classes."""

    BINARY = auto()
    SUCCESS_FAILURE = auto()
    ENABLED_DISABLED = auto()
