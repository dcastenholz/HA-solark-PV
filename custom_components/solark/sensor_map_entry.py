import logging
from typing import Unpack

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)

from .base_map_entry import BaseMapEntry, BaseMapEntryOptional
from .register_map_entry import RegisterMapEntry
from .sensor_entity_description import NativeUnit, SensorClass

_LOGGER = logging.getLogger(__name__)

class SensorMapEntry(BaseMapEntry[RegisterMapEntry]):
    pass

# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorMapEntry):
    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("native_unit", NativeUnit.WATT)
        kwargs.setdefault("device_class", SensorDeviceClass.POWER)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(key, name, **kwargs)


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(SensorMapEntry):
    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.KWH)
        kwargs.setdefault("device_class", SensorDeviceClass.ENERGY)
        kwargs.setdefault("state_class", SensorStateClass.TOTAL)

        super().__init__(key, name, **kwargs)


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorMapEntry):
    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:information-outline")
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)

        super().__init__(key, name, **kwargs)


# ----------------------------
# ConfigEntry
# ----------------------------
class ConfigEntry(SensorMapEntry):
    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:information-outline")
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)
        kwargs.setdefault("sensor_class", SensorClass.BASE)

        super().__init__(key, name, **kwargs)
