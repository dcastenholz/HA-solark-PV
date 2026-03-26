import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any, Callable, Optional, Union

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
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

from .sensor_entity_description import SensorClass, SolArkModbusSensorEntityDescription


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
    AH = BatteryChargeHelper.AH
    CELSIUS = UnitOfTemperature.CELSIUS
    PERCENT = PERCENTAGE
    HZ = UnitOfFrequency.HERTZ
    NONE = None  # for sensors without a unit

# ----------------------------------
# Device Class Enum
# ----------------------------------
class DeviceClass(Enum):
    ENERGY = SensorDeviceClass.ENERGY
    POWER = SensorDeviceClass.POWER
    VOLTAGE = SensorDeviceClass.VOLTAGE
    CURRENT = SensorDeviceClass.CURRENT
    TEMPERATURE = SensorDeviceClass.TEMPERATURE
    BATTERY = SensorDeviceClass.BATTERY
    FREQUENCY = SensorDeviceClass.FREQUENCY
    TIMESTAMP = SensorDeviceClass.TIMESTAMP
    NONE = None  # for sensors without a device class

# ----------------------------------
# State Class Enum
# ----------------------------------
class StateClass(Enum):
    TOTAL = SensorStateClass.TOTAL
    TOTAL_INCREASING = SensorStateClass.TOTAL_INCREASING
    MEASUREMENT = SensorStateClass.MEASUREMENT
    NONE = None  # for sensors without a state class

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
@dataclass()
class RegisterMapEntry:
    key: str
    name: str
    data_type: DataType = DataType.INT16
    source_is_register_read: bool = True  # True if value comes directly from register read, False if calculated from other values
    address: int = -1
    register_value: RegisterValue = (
        None  # This will hold the decoded value after reading registers, or the calculated value if source_is_register_read is False
    )
    processed_value: int | None = None
    icon: str = ""
    scale: float = 1.0
    offset: int = 0
    native_unit_of_measurement: NativeUnit = NativeUnit.NONE
    device_class: DeviceClass = DeviceClass.NONE
    state_class: StateClass = StateClass.NONE
    entity_registry_enabled_default: bool = False
    entity_category: EntityCategory | None = None
    post_process_method: Optional[Callable[[Any, "RegisterMapEntry"], None]] = None
    description: str | None = None
    sensor_class: SensorClass = SensorClass.NORMAL
    exclude_from_recorder: bool = False

    def __post_init__(self):
        self.__validate__()

    def __validate__(self):
        if self.source_is_register_read:
            # If reading directly from register, address must be non-negative
            if self.address < 0:
                raise ValueError(f"RegisterMapEntry {self.key} must have a non-negative address if source_is_register_read is True")
        else:
            # If not read from register, must have a post_process_method
            if self.post_process_method is None:
                raise ValueError(f"RegisterMapEntry {self.key} must have post_process_method if source_is_register_read is False")

            # If not read from register, address must be -1
            if self.address != -1:
                raise ValueError(f"RegisterMapEntry {self.key} should not have an address since it's not read directly from a register")


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

    def post_process(self, register_map: Any) -> None:
        if self.post_process_method is not None:
            try:
                self.post_process_method(register_map, self)
            except Exception as ex:                             # pylint: disable=W0718
                _LOGGER.exception("Error post-processing register %s: %s", self.key, ex)

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
        raise ValueError(f"Unknown DataType {self.data_type} for {self.key}")

    def from_register_map_entry(self) -> SolArkModbusSensorEntityDescription:
        return SolArkModbusSensorEntityDescription(
            name=self.name,
            key=self.key,
            native_unit_of_measurement=self.native_unit_of_measurement.value,
            device_class=self.device_class.value,
            state_class=self.state_class.value,
            icon=self.icon or None,
            entity_registry_enabled_default=self.entity_registry_enabled_default,
            entity_category=self.entity_category,
            description=self.description,
            sensor_class=self.sensor_class,
            exclude_from_recorder=self.exclude_from_recorder
        )


# ----------------------------
# String
# ----------------------------
@dataclass
class StringEntry(RegisterMapEntry):
    #data_type: DataType = field(default=DataType.STRING)
    length: int = 1

    def __post_init__(self):
        self.__validate__()
        super().__post_init__()

    def __validate__(self):
        if self.source_is_register_read:
            # If reading directly from register, STRING type must have string_register_length defined
            if self.length is None:
                raise ValueError(f"STRING type RegisterMapEntry {self.key} must have length")

    @property
    def register_length(self) -> int:
            if not self.length:
                raise ValueError(f"STRING type missing length for {self.key}")
            if self.length < 1:
                raise ValueError(f"STRING with length < 1 for {self.key}")
            return self.length

# ----------------------------
# Grid Voltage
# ----------------------------
@dataclass
class GridVoltageEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    icon: str = field(default="mdi:flash")
    scale: float = field(default=0.1)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.V)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# Battery Voltage
# ----------------------------
@dataclass
class BatteryVoltageEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    icon: str = field(default="mdi:battery")
    scale: float = field(default=0.01)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.V)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# PV Voltage
# ----------------------------
@dataclass
class PVVoltageEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    icon: str = field(default="mdi:solar-power")
    scale: float = field(default=0.1)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.V)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# Frequency
# ----------------------------
@dataclass
class FrequencyEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    scale: float = field(default=0.01)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.HZ)
    device_class: DeviceClass = field(default=DeviceClass.FREQUENCY)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)
    icon: str = field(default="mdi:sine-wave")


# ----------------------------
# Current
# ----------------------------
@dataclass
class CurrentEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.INT16)
    scale: float = field(default=0.01)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.A)
    device_class: DeviceClass = field(default=DeviceClass.CURRENT)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# Power
# ----------------------------
@dataclass
class PowerEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.INT16)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.WATT)
    device_class: DeviceClass = field(default=DeviceClass.POWER)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# Energy
# ----------------------------
@dataclass
class EnergyEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT32)
    scale: float = field(default=0.1)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.KWH)
    device_class: DeviceClass = field(default=DeviceClass.ENERGY)
    state_class: StateClass = field(default=StateClass.TOTAL)


# ----------------------------
# Temperature
# ----------------------------
@dataclass
class TemperatureEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    scale: float = field(default=0.1)
    offset: int = field(default=1000)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.CELSIUS)
    device_class: DeviceClass = field(default=DeviceClass.TEMPERATURE)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# State of Charge
# ----------------------------
@dataclass
class SOCEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    native_unit_of_measurement: NativeUnit = field(default=NativeUnit.PERCENT)
    device_class: DeviceClass = field(default=DeviceClass.BATTERY)
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# State of Charge
# ----------------------------
@dataclass
class TimeOfUseEnabledEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    icon: str = field(default="mdi:check-circle")
    state_class: StateClass = field(default=StateClass.MEASUREMENT)


# ----------------------------
# Time
# ----------------------------
@dataclass
class TimeEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    icon: str = field(default="mdi:clock-outline")

    def __post_init__(self):
        # Assign the post-process formatting if not already set
        if not self.post_process_method:
            self.post_process_method = self.format_hhmm_time

        super().__post_init__()

    @staticmethod
    def format_hhmm_time(register_map, entry: RegisterMapEntry): # pylint: disable=W0613
        """Convert HHMM integer to a 12-hour formatted string."""
        try:
            value = int(entry.register_value) # type: ignore
        except (TypeError, ValueError):
            entry.register_value = None
            return

        if value in (0, 65535):
            # Optionally treat 0 or 65535 as undefined
            entry.register_value = None
            return

        hours = value // 100
        minutes = value % 100
        if hours > 23 or minutes > 59:
            entry.register_value = "Invalid"
            return

        suffix = "AM" if hours < 12 else "PM"
        hour_12 = hours % 12
        if hour_12 == 0:
            hour_12 = 12

        entry.register_value = f"{hour_12}:{minutes:02d} {suffix}"


# ----------------------------
# Diagnostic
# ----------------------------
@dataclass
class DiagnosticEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    entity_category: EntityCategory = field(default=DIAGNOSTIC)


# ----------------------------
# ConfigEntry
# ----------------------------
@dataclass
class ConfigEntry(StringEntry):
    data_type: DataType = field(default=DataType.UINT16)
    entity_category: EntityCategory = field(default=EntityCategory.DIAGNOSTIC)
    source_is_register_read: bool = field(default=False)
    #data_type: DataType = field(default=DataType.STRING)
    icon: str = field(default="mdi:information-outline")
    state_class: StateClass = field(default=StateClass.NONE)
    sensor_class: SensorClass = field(default=SensorClass.CONFIG)


# ----------------------------
# SystemTimeEntry
# ----------------------------
@dataclass
class SystemTimeEntry(RegisterMapEntry):
    data_type: DataType = field(default=DataType.UINT16)
    entity_category: EntityCategory = field(default=EntityCategory.DIAGNOSTIC)
    icon: str = field(default="mdi:information-outline")
    state_class: StateClass = field(default=StateClass.NONE)
    exclude_from_recorder: bool = field(default=True)
