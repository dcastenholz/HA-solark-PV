import datetime
import logging
from typing import Any, Callable, Optional, Union

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)

from .sensor_entity_description import SensorClass, SolArkModbusSensorEntityDescription, UnitOfMeasure

RegisterValue = Union[int, float, str, datetime.datetime, None]
NumericValue = Union[int, float]

_LOGGER = logging.getLogger(__name__)

# ----------------------------------
# Register Map Entry
# ----------------------------------

class SensorMapEntry():
    _entity_description: SolArkModbusSensorEntityDescription

    scale: float
    offset: int
    post_process_method: Optional[Callable[[Any, "SensorMapEntry"], None]]

    # This will hold the decoded value after reading registers
    register_value: RegisterValue = None
    processed_value: int | None = None

    def __init__(
        self,
        key: str,
        name: str | None = None,
        unit_of_measurement: UnitOfMeasure | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
        entity_registry_enabled_default: bool = False,
        entity_category: EntityCategory | None = None,
        description: str | None = None,
        sensor_class: SensorClass = SensorClass.NORMAL,
        exclude_from_recorder: bool = False,
        post_process_method: Optional[Callable[[Any, "SensorMapEntry"], None]] = None,
        scale: float = 1.0,
        offset: int = 0,

    ) -> None:

        self._entity_description = SolArkModbusSensorEntityDescription(
            key=key,
            name=name,
            native_unit_of_measurement=(unit_of_measurement.value if unit_of_measurement else None),
            unit_of_measurement_enum=unit_of_measurement,
            device_class=device_class,
            state_class=state_class,
            icon=icon,
            entity_registry_enabled_default=entity_registry_enabled_default,
            entity_category=entity_category,
            description=description,
            sensor_class=sensor_class,
            exclude_from_recorder=exclude_from_recorder,
        )

        self.scale = scale
        self.offset = offset
        self.post_process_method = post_process_method

        self._validate()

    def _validate(self):
        if type(self) is SensorMapEntry:
            # Must have a post_process_method. Not required for subclasses
            if self.post_process_method is None:
                raise ValueError(f"SensorMapEntry {self._entity_description.key} must have post_process_method")

    def __add__(self, other: Union["SensorMapEntry", NumericValue]) -> NumericValue:
        """Add this entry to another entry or numeric value."""
        self_val: NumericValue
        if isinstance(self.register_value, (int, float)):
            self_val = self.register_value
        else:
            raise TypeError(f"Cannot use non-numeric register_value {self.register_value}")

        if isinstance(other, SensorMapEntry):
            if isinstance(other.register_value, (int, float)):
                return self_val + other.register_value
            else:
                raise TypeError(f"Cannot add non-numeric register_value {other.register_value}")
        elif isinstance(other, (int, float)):
            return self_val + other
        else:
            raise TypeError(f"Cannot add RegisterMapEntry with {type(other)}")

    def __radd__(self, other: NumericValue) -> NumericValue:
        """Support int/float + SensorMapEntry"""
        if isinstance(other, (int, float)):
            if isinstance(self.register_value, (int, float)):
                return other + self.register_value
            else:
                raise TypeError(f"Cannot use non-numeric register_value {self.register_value}")
        return NotImplemented

    def __int__(self) -> int:
        if isinstance(self.register_value, (int, float)):
            return int(self.register_value)
        raise TypeError(f"Cannot convert non-numeric register_value {self.register_value} to int")

    def __float__(self) -> float:
        if isinstance(self.register_value, (int, float)):
            return float(self.register_value)
        raise TypeError(f"Cannot convert non-numeric register_value {self.register_value} to float")

    @property
    def entity_description(self) -> SolArkModbusSensorEntityDescription:
        return self._entity_description

    def post_process(self, register_map: Any) -> None:
        if self.post_process_method is not None:
            try:
                self.post_process_method(register_map, self)
            except Exception as ex:                             # pylint: disable=W0718
                _LOGGER.exception("Error post-processing register %s: %s", self._entity_description.key, ex)


# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        super().__init__(
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfMeasure.WATT,
            **kwargs,
        )


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        super().__init__(
            scale=0.1,
            unit_of_measurement=UnitOfMeasure.KWH,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            **kwargs,
        )


# ----------------------------
# ConfigEntry
# ----------------------------
class ConfigEntry(SensorMapEntry):
    def __init__(self, **kwargs):
        super().__init__(
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:information-outline",
            sensor_class=SensorClass.CONFIG,
            **kwargs,
        )
