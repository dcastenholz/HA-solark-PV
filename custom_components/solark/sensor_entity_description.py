from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.sensor import SensorEntityDescription
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
    from .sensor import SolArkSensorEntity


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
    sensor_class: SensorClass = SensorClass.NORMAL
    description: str | None = None
    exclude_from_recorder: bool = False
    # should_poll is ignored for coordinator sensors.
    should_poll: bool = True
    dynamic_icon: Callable[["SensorValue"], str] | None = None
    on_sensor_creating: Callable[["SolArkSensorEntity", "SolArkData"], None] | None = None
    name_prefix: str = ""

    @classmethod
    def from_kwargs(
        cls,
        key: str,
        name: str,
        opts: dict[str, Any],
    ) -> "SolArkSensorEntityDescription":

        passthrough = {
            # SolArkSensorEntityDescription
            "sensor_class",
            "description",
            "exclude_from_recorder",
            "should_poll",
            "dynamic_icon",
            "on_sensor_creating",
            "name_prefix",

            # SensorEntityDescription
            "device_class",
            "state_class",
            "suggested_display_precision",

            # EntityDescription
            "icon",
            "entity_registry_enabled_default",
            "entity_category",
        }

        base_kwargs = {
            "key": key,
            "name": name,
            **{k: v for k, v in opts.items()
            if k in passthrough and v is not None},
        }

        unit = opts.get("native_unit")
        if unit is not None:
            base_kwargs["native_unit_of_measurement"] = unit.value

        return cls(**base_kwargs)
