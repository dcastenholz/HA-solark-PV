from enum import Enum

from .register_value_types import RegisterValue


class SensorDynamicIcon(Enum):
    CHECK_BOX = lambda v: (
        "mdi:checkbox-blank-circle-outline" if v == 0
         else "mdi:checkbox-marked-circle-outline" if v == 255
         else None
    )

    RELAY = lambda v: (
        "mdi:electric-switch" if v == "Open"
         else "mdi:electric-switch-closed" if v == "Closed"
         else None
    )

    GENERATOR_RELAY = lambda v: (
        "mdi:electric-switch" if v == 0
        else "mdi:electric-switch-closed" if v == 1
        else "mdi:connection" if v == 2
        else "mdi:generator-portable" if v == 3
        else None
    )

    def __call__(self, value: RegisterValue | None) -> str | None:
        if value is None:
            return None
        return self.value(value)