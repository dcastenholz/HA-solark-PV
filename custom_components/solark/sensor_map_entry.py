import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)

from .base_map_entry import BaseMapEntry
from .register_map_entry import RegisterMapEntry
from .sensor_entity_description import SensorClass, UnitOfMeasure

_LOGGER = logging.getLogger(__name__)

class SensorMapEntry(BaseMapEntry[RegisterMapEntry]):
    """
    Pure sensor-level entry.

    No register addressing; only semantic sensor behavior.
    """

    def _validate(self) -> None:
        super()._validate()

        # Must have a post_process_method.
        if self.post_process_method is None:
            raise ValueError(
                f"SensorMapEntry {self._entity_description.key} "
                "must define post_process_method"
            )


# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("device_class", SensorDeviceClass.POWER)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.WATT)

        super().__init__(**kwargs)


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.KWH)
        kwargs.setdefault("device_class", SensorDeviceClass.ENERGY)
        kwargs.setdefault("state_class", SensorStateClass.TOTAL)

        super().__init__(**kwargs)


# ----------------------------
# ConfigEntry
# ----------------------------
class ConfigEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)
        kwargs.setdefault("sensor_class", SensorClass.CONFIG)

        super().__init__(**kwargs)


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)

        super().__init__(**kwargs)