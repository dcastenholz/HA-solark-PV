import datetime
import logging
from enum import Enum
from typing import Any, Callable, Optional, Union

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)

from .sensor_entity_description import SensorClass, SolArkModbusSensorEntityDescription, UnitOfMeasure


# ----------------------------------
# Data Type Enum
# ----------------------------------
class DataType(Enum):
    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    INT64 = "int64"
    UINT64 = "uint64"
    #STRING = "string"

RegisterValue = Union[int, float, str, datetime.datetime, None]
NumericValue = Union[int, float]
DIAGNOSTIC = EntityCategory.DIAGNOSTIC

_LOGGER = logging.getLogger(__name__)

# ----------------------------------
# Register Map Entry
# ----------------------------------
class RegisterMapEntry:
    _entity_description: SolArkModbusSensorEntityDescription

    data_type: DataType = DataType.INT16
    address: int = -1
    register_value: RegisterValue = (
        None  # This will hold the decoded value after reading registers, or the calculated value if source_is_register_read is False
    )
    processed_value: int | None = None
    scale: float = 1.0
    offset: int = 0

    def __init__(
        self,
        key: str,
        address: int,
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
        scale: float = 1.0,
        offset: int = 0,
        data_type: DataType = DataType.INT16

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

        self.address = address
        self.data_type = data_type
        self.scale = scale
        self.offset = offset
    def __post_init__(self):
        self.__validate__()

    def __validate__(self):
        # Address must be non-negative
        if self.address < 0:
            raise ValueError(f"RegisterMapEntry {self._entity_description.key} must have a non-negative address if source_is_register_read is True")


    def __add__(self, other: Union["RegisterMapEntry", NumericValue]) -> NumericValue:
        """Add this entry to another entry or numeric value."""
        self_val: NumericValue
        if isinstance(self.register_value, (int, float)):
            self_val = self.register_value
        else:
            raise TypeError(f"Cannot use non-numeric register_value {self.register_value}")

        if isinstance(other, RegisterMapEntry):
            if isinstance(other.register_value, (int, float)):
                return self_val + other.register_value
            else:
                raise TypeError(f"Cannot add non-numeric register_value {other.register_value}")
        elif isinstance(other, (int, float)):
            return self_val + other
        else:
            raise TypeError(f"Cannot add RegisterMapEntry with {type(other)}")

    def __radd__(self, other: NumericValue) -> NumericValue:
        """Support int/float + RegisterMapEntry"""
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

    @property
    def register_length(self) -> int:
        """Calculate the register count based on the data type, including string length if applicable."""
        if self.data_type in (DataType.INT16, DataType.UINT16):
            return 1
        if self.data_type in (DataType.INT32, DataType.UINT32):
            return 2
        if self.data_type in (DataType.INT64, DataType.UINT64):
            return 4
        # if self.data_type == DataType.STRING:
        #     if not self.string_register_length:
        #         raise ValueError(f"STRING type missing string_register_length for {self.key}")
        #     if self.string_register_length < 1:
        #         raise ValueError(f"STRING with string_register_length < 1 for {self.key}")
        #     return self.string_register_length
        raise ValueError(f"Unknown DataType {self.data_type} for {self._entity_description.key}")

    def from_register_map_entry(self) -> SolArkModbusSensorEntityDescription:
        return self._entity_description


# ----------------------------
# String
# ----------------------------
class StringEntry(RegisterMapEntry):
    length: int

    def __init__(self, length: int, **kwargs):
        self.length = length

        super().__init__(
            **kwargs,
        )

        self.__validate__()

    def __validate__(self):
            # STRING type must have string_register_length defined
            if self.length is None:
                raise ValueError(f"STRING type RegisterMapEntry {self._entity_description.key} must have length")

    @property
    def register_length(self) -> int:
            if not self.length:
                raise ValueError(f"STRING type missing length for {self._entity_description.key}")
            if self.length < 1:
                raise ValueError(f"STRING with length < 1 for {self._entity_description.key}")
            return self.length

# ----------------------------
# Grid Voltage
# ----------------------------
class GridVoltageEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("icon", "mdi:flash")
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# Battery Voltage
# ----------------------------
class BatteryVoltageEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("icon", "mdi:battery")
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# PV Voltage
# ----------------------------
class PVVoltageEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("icon", "mdi:solar-power")
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# Frequency
# ----------------------------
class FrequencyEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.HZ)
        kwargs.setdefault("device_class", SensorDeviceClass.FREQUENCY)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("icon", "mdi:sine-wave")

        super().__init__(**kwargs)

# ----------------------------
# Current
# ----------------------------
class CurrentEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.INT16)
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.A)
        kwargs.setdefault("device_class", SensorDeviceClass.CURRENT)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# Power
# ----------------------------
class PowerEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("device_class", SensorDeviceClass.POWER)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.WATT)

        super().__init__(**kwargs)


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT32)
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.KWH)
        kwargs.setdefault("device_class", SensorDeviceClass.ENERGY)
        kwargs.setdefault("state_class", SensorStateClass.TOTAL)

        super().__init__(**kwargs)


# ----------------------------
# Temperature
# ----------------------------
class TemperatureEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("offset", 1000)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.CELSIUS)
        kwargs.setdefault("device_class", SensorDeviceClass.TEMPERATURE)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# State of Charge
# ----------------------------
class SOCEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("unit_of_measurement", UnitOfMeasure.PERCENT)
        kwargs.setdefault("device_class", SensorDeviceClass.BATTERY)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# State of Charge
# ----------------------------
class TimeOfUseEnabledEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("icon", "mdi:check-circle")
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(**kwargs)

# ----------------------------
# Time
# ----------------------------
class TimeOfUseTimeEntry(RegisterMapEntry):
    post_process_method: Optional[Callable[[Any, "RegisterMapEntry"], None]] = None

    def __init__(self, **kwargs):
        kwargs.setdefault("sensor_class", SensorClass.TOU_TIME)
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("icon", "mdi:clock-outline")

        super().__init__(**kwargs)

# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)

        super().__init__(**kwargs)

# ----------------------------
# SystemTimeEntry
# ----------------------------
class SystemTimeEntry(RegisterMapEntry):
    def __init__(self, **kwargs):
        kwargs.setdefault("data_type", DataType.UINT16)
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)
        kwargs.setdefault("icon", "mdi:information-outline")
        kwargs.setdefault("state_class", None)
        kwargs.setdefault("exclude_from_recorder", True)

        super().__init__(**kwargs)
