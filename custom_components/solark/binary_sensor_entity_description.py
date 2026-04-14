from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntityDescription
from homeassistant.components.sensor import EntityCategory

from .binary_sensor_class import BinarySensorClass
from .register_value_types import SensorValue

if TYPE_CHECKING:
    from .binary_sensor import SolArkBinarySensor
    from .data import SolArkData

# ----------------------------------
# Sensor Entity Description
# ----------------------------------
@dataclass(kw_only=True, frozen=True)
class SolArkBinarySensorEntityDescription(BinarySensorEntityDescription):
    """SolArk-specific sensor description."""
    key: str
    name: str = ""

    icon: str | None = None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None
    description: str | None = None
    exclude_from_recorder: bool = False
    should_poll: bool | None = None
    extra_state_attributes: dict[str, Any] = field(default_factory=dict)
    dynamic_icon: Callable[["SensorValue"], str] | None = None

    post_process_sensor: Callable[["SolArkBinarySensor", "SolArkData"], None] | None = None
    device_class: BinarySensorDeviceClass | None = None
    sensor_class: BinarySensorClass = BinarySensorClass.BINARY
