import logging
from abc import ABC
from typing import Unpack

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)

from .base_map_entry import BaseMapEntry, BaseMapEntryKwargs
from .register_map_entry import RegisterMapEntry
from .sensor_entity_description import SensorClass, UnitOfMeasure

_LOGGER = logging.getLogger(__name__)

class SensorMapEntry(BaseMapEntry[RegisterMapEntry], ABC):
    """
    Pure sensor-level entry.

    No register addressing; only semantic sensor behavior.
    """
    def __init__(self, **kwargs: Unpack[BaseMapEntryKwargs]) -> None:
        super().__init__(**kwargs)


# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorMapEntry):
    def __init__(self, **kwargs: Unpack[BaseMapEntryKwargs]) -> None:
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.WATT)
        kwargs.setdefault("device_class", SensorDeviceClass.POWER)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(SensorMapEntry):
    def __init__(self, **kwargs: Unpack[BaseMapEntryKwargs]) -> None:
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.KWH)
        kwargs.setdefault("device_class", SensorDeviceClass.ENERGY)
        kwargs.setdefault("state_class", SensorStateClass.TOTAL)

        super().__init__(**kwargs)


# ----------------------------
# ConfigEntry
# ----------------------------
class ConfigEntry(SensorMapEntry):
    def __init__(self, **kwargs: Unpack[BaseMapEntryKwargs]) -> None:
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)
        kwargs.setdefault("sensor_class", SensorClass.BASE)

        super().__init__(**kwargs)


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorMapEntry):
    def __init__(self, **kwargs: Unpack[BaseMapEntryKwargs]) -> None:
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)

        super().__init__(**kwargs)
