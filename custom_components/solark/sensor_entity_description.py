from dataclasses import InitVar, dataclass, field
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.sensor import EntityCategory, SensorDeviceClass, SensorEntityDescription, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)

from .register_value_types import SensorValue
from .sensor_class import SensorClass

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensor


class BatteryChargeHelper(StrEnum):
    AH = "Ah"


# ----------------------------------
# Native Unit of Measurement Enum
# ----------------------------------
class NativeUnit(Enum):
    KWH = UnitOfEnergy.KILO_WATT_HOUR
    WATT = UnitOfPower.WATT
    V = UnitOfElectricPotential.VOLT
    A = UnitOfElectricCurrent.AMPERE
    AH = "Ah"
    CELSIUS = UnitOfTemperature.CELSIUS
    PERCENT = PERCENTAGE
    HZ = UnitOfFrequency.HERTZ


# ----------------------------------
# Sensor Entity Description
# ----------------------------------
@dataclass(kw_only=True, frozen=True)
class SolArkSensorEntityDescription(SensorEntityDescription):
    """SolArk-specific sensor description."""
    key: str
    name: str = ""

    icon: str | None = None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None
    description: str | None = None
    exclude_from_recorder: bool = False
    # TODO - Determine if this is ever needed with coordinator
    should_poll: bool | None = None
    extra_state_attributes: dict[str, Any] = field(default_factory=dict)
    dynamic_icon: Callable[["SensorValue"], str] | None = None

    post_process_sensor: Callable[["SolArkSensor", "SolArkData"], None] | None = None
    device_class: SensorDeviceClass | None = None
    sensor_class: SensorClass = SensorClass.NORMAL

    suggested_display_precision: int | None = None
    state_class: SensorStateClass | None = None
    native_unit: InitVar[NativeUnit | None] = None

    def __post_init__(self, native_unit: NativeUnit | None):
        if native_unit is not None:
            object.__setattr__(
                self,
                "native_unit_of_measurement",
                native_unit.value,
            )
