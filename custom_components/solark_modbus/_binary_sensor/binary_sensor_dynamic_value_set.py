from enum import Enum
from typing import Any


class BinarySensorDynamicValueSet(Enum):
    """Value pairs for binary sensor state."""
    ENABLED_DISABLED = "enabled_disabled"
    SUCCESS_FAILURE = "success_failure"


class BinarySensorDynamicInfo:
    """Information about binary sensor dynamic values."""
    def __init__(self, binary_sensor_dynamic_value_set: BinarySensorDynamicValueSet, true_icon: Any, false_icon: Any):
        self.binary_sensor_dynamic_value_set = binary_sensor_dynamic_value_set
        self.true_icon = true_icon
        self.false_icon = false_icon
