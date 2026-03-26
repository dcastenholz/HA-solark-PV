from dataclasses import dataclass
from enum import Enum, auto

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory


class SensorClass(Enum):
    NORMAL = auto()
    CONFIG = auto()
    DATETIME = auto()


# ----------------------------------
# Sensor Entity Description
# ----------------------------------
@dataclass(kw_only=True, frozen=True)
class SolArkModbusSensorEntityDescription(SensorEntityDescription):
    """A class that describes SolArk sensor entities."""

    key: str
    name: str | None = None
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    icon: str | None = None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None
    description: str | None = None
    sensor_class: SensorClass = SensorClass.NORMAL
    exclude_from_recorder: bool = False
