from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)

from .sensor_class import SensorClass

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkBaseSensor

class BatteryChargeHelper(StrEnum):
    AH = "Ah"


# ----------------------------------
# Native Unit of Measurement Enum
# ----------------------------------
class UnitOfMeasure(Enum):
    KWH = UnitOfEnergy.KILO_WATT_HOUR
    WATT = UnitOfPower.WATT
    V = UnitOfElectricPotential.VOLT
    A = UnitOfElectricCurrent.AMPERE
    AH = BatteryChargeHelper.AH
    CELSIUS = UnitOfTemperature.CELSIUS
    PERCENT = PERCENTAGE
    HZ = UnitOfFrequency.HERTZ
    NONE = None  # for sensors without a unit


# ----------------------------------
# Sensor Entity Description
# ----------------------------------
@dataclass(kw_only=True, frozen=True)
class SolArkModbusSensorEntityDescription(SensorEntityDescription):
    """A class that describes SolArk sensor entities."""

    key: str
    name: str | None = None
    native_unit_of_measurement: str | None = None
    unit_of_measurement_enum: UnitOfMeasure | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    icon: str | None = None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None
    description: str | None = None
    sensor_class: SensorClass = SensorClass.NORMAL
    exclude_from_recorder: bool = False
    should_poll: bool | None = None
    extra_state_attributes: dict[str, Any] = field(default_factory=dict)
    post_process_sensor: Callable[["SolArkBaseSensor", "SolArkData"], None] | None

    # TODO - Add suggested_display_precision: int | None = None

    def __post_init__(self):
        if self.unit_of_measurement_enum:
            object.__setattr__(
                self,
                "native_unit_of_measurement",
                self.unit_of_measurement_enum.value,
            )
