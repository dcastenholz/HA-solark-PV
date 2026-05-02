from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, Self, TypedDict

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)
from typing_extensions import Unpack

from .register_value_types import TSensorValue
from .sensor_entity_description import NativeUnit, SensorClass
from .sensor_map_entry import BaseSensorEntry

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensorEntity

_LOGGER = logging.getLogger(__name__)


# ----------------------------------
# Data Type Enum
# ----------------------------------
# TODO - Unused strings??? convert to auto()
class DataType(Enum):
    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    INT64 = "int64"
    UINT64 = "uint64"


class RegisterEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool

    device_class: SensorDeviceClass
    sensor_class: SensorClass

    state_class: Optional[SensorStateClass]
    native_unit: NativeUnit

    set_sensor_value: Callable[[Any, "SolArkData"], None]
    scale: float
    offset: int


# ----------------------------------
# Register Entry
# ----------------------------------
class RegisterEntry(Generic[TSensorValue], BaseSensorEntry[TSensorValue], ABC):
    """
    RegisterEntry[TSensorValue]

        Type Parameters:
            TSensorValue: the type of the sensor display value.

    Abstract base class for all modbus register-backed sensors.

        Adds:
            the register address for the start of the range to read
            the length of the register range to read
            storage of decoded register read value
            validation
    """

    address: int

    def __init__(self, address: int, key: str, name: str, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

        self.address = address

    @property
    @abstractmethod
    def register_length(self) -> int:
        pass

    def _validate(self):
        # RegisterEntry must have non-negative address
        if self.address < 0:
            raise ValueError(f"RegisterEntry {self._entity_description.key}: address must be >= 0")


class RegisterNumericEntry(Generic[TSensorValue], RegisterEntry[TSensorValue], ABC):
    """
    RegisterNumericEntry[TRegisterValue, TSensorValue]

        Type Parameters:
            TRegisterValue: the type of the decoded value from the register.
            TSensorValue: the type of the sensor display value.

    Abstract base class for all modbus integer register backed numeric sensors.

        Adds:
            data type
            the length of the register range to read for all numeric entries
    """
    data_type: DataType

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        super().__init__(address, key, name, **kwargs)

        self.data_type = data_type

    @property
    def register_length(self) -> int:
        """Calculate the register count based on the data type, including string length if applicable."""
        if self.data_type in (DataType.INT16, DataType.UINT16):
            return 1
        if self.data_type in (DataType.INT32, DataType.UINT32):
            return 2
        if self.data_type in (DataType.INT64, DataType.UINT64):
            return 4
        raise ValueError(f"Unknown DataType {self.data_type} for {self._entity_description.key}")


class RegisterIntEntry(RegisterNumericEntry[int]):
    """
    Class for all modbus integer register backed integer sensors.

        Adds:
            logic for setting base value and sensor value
    """

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        super().__init__(address, key, name, data_type, **kwargs)


class RegisterFloatEntry(RegisterNumericEntry[float]):
    """
    Class for all modbus float register backed float sensors.

        Adds:
            logic for setting base value and sensor value
            offset value for the register
            scale value for the register
    """
    offset: int
    scale: float

    DEFAULTS = {
        "offset": 0,
        "scale": 1.0,
    }

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        super().__init__(address, key, name, data_type, **kwargs)

        # -----------------------------
        # Store fields using kwargs merged with DEFAULTS
        # -----------------------------
        self.offset = self.opts["offset"]
        self.scale = self.opts["scale"]

    @property
    def sensor_value(self) -> float | None:
        return self._sensor_value

    @sensor_value.setter
    def sensor_value(self: Self, value: int) -> None:
        self._sensor_value = (value - self.offset) * self.scale


# ----------------------------
# Grid Relay
# ----------------------------
class GridRelayEntry(RegisterIntEntry):
    DynamicValueDict = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
    }

    DEFAULTS = {
        "state_class": None,
    }


# ----------------------------
# String
# ----------------------------
class StringEntry(RegisterEntry[str]):
    """
    Class for all modbus string register backed string sensors.

        Adds:
            logic for setting base value and sensor value
            the length of the register range to read for string entries
    """
    length: int

    def __init__(self, address: int, key: str, name: str, length: int, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        self.length = length

        super().__init__(address, key, name, **kwargs)

    def _validate(self):
        # StringEntry must have string_register_length defined
        if self.length is None:
            raise ValueError(f"StringEntry {self._entity_description.key} must have length")

    @property
    def register_length(self) -> int:
        if not self.length:
            raise ValueError(f"StringEntry missing length for {self._entity_description.key}")
        if self.length < 1:
            raise ValueError(f"StringEntry with length < 1 for {self._entity_description.key}")
        return self.length


# ----------------------------
# Serial Number Entry
# ----------------------------
class SerialNumberEntry(StringEntry):
    # TODO - Make sure this is called!!!
    def _post_process(self: Self, runtime_data: "SolArkData") -> None:
        '''Save the serial number to the device info serial number property'''

        # TODO - This must be moved to a location where it will only be run if the register is read
        # just prior to it running.  _post_process is a sledgehammer
        from .device_info import SolArkDeviceInfo
        a = self.sensor_value
        SolArkDeviceInfo.handle_serial_number_change(runtime_data, str(self.sensor_value))


# ----------------------------
# Raw Value
# ----------------------------
class RawValueEntry(RegisterIntEntry):
    '''Values read from registers that are NOT normally displayed in UI screens.
    These are values that change over time and will produce history if enabled.'''

    DEFAULTS = {
        "icon": "mdi:code-braces",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": SensorStateClass.MEASUREMENT,
        "name_prefix": "Raw Value: ",
    }


# ----------------------------
# Raw Value
# ----------------------------
class RawInfoEntry(RegisterIntEntry):
    '''Values read from registers that are not normally displayed in UI screens.
    These are mostly static values that do not typically change over time.'''

    DEFAULTS = {
        "icon": "mdi:code-braces",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": None,
        "name_prefix": "Raw Info: ",
    }


# ----------------------------
# Raw Value System Time
# ----------------------------
class RawValueSystemTimeEntry(RegisterIntEntry):
    '''Values read from registers that are not normally displayed in UI screens.
    These are values that are based on the inverter system time but are specifically
    excluded from history to avoid pointless database entries.'''

    DEFAULTS = {
        # "exclude_from_recorder": True,
    }


# ----------------------------
# Grid Voltage
# ----------------------------
class GridVoltageEntry(RegisterFloatEntry):
    DEFAULTS = {
        "icon": "mdi:flash",
        "scale": 0.1,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Battery Voltage
# ----------------------------
class BatteryVoltageEntry(RegisterFloatEntry):
    DEFAULTS = {
        "icon": "mdi:battery-plus-outline",
        "scale": 0.01,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# PV Voltage
# ----------------------------
class PVVoltageEntry(RegisterFloatEntry):
    DEFAULTS = {
        "icon": "mdi:solar-power",
        "scale": 0.1,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Frequency
# ----------------------------
class FrequencyEntry(RegisterFloatEntry):
    DEFAULTS = {
        "icon": "mdi:sine-wave",
        "scale": 0.01,
        "native_unit": NativeUnit.HZ,
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Current
# ----------------------------
class CurrentEntry(RegisterFloatEntry):
    DEFAULTS = {
        "scale": 0.01,
        "native_unit": NativeUnit.A,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Battery Current
# ----------------------------
class BatteryCurrentEntry(RegisterIntEntry):
    DEFAULTS = {
        "icon": "mdi:current-dc",
        "native_unit": NativeUnit.A,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Power
# ----------------------------
class PowerEntry(RegisterIntEntry):
    DEFAULTS = {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": NativeUnit.WATT,
    }


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterFloatEntry):
    DEFAULTS = {
        "scale": 0.1,
        "native_unit": NativeUnit.KWH,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    }


# ----------------------------
# Energy Total Increasing
# ----------------------------
class EnergyTotalIncreasingEntry(EnergyEntry):
    DEFAULTS = {
        "state_class": SensorStateClass.TOTAL_INCREASING,
    }


# ----------------------------
# Temperature
# ----------------------------
class TemperatureEntry(RegisterFloatEntry):
    DEFAULTS = {
        "scale": 0.1,
        "offset": 1000,
        "native_unit": NativeUnit.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# State of Charge
# ----------------------------
class SOCEntry(RegisterIntEntry):
    DEFAULTS = {
        "native_unit": NativeUnit.PERCENT,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Time of Use Enabled
# ----------------------------
class TimeOfUse_EnabledEntry(RegisterIntEntry):
    DynamicValueDict = {
        0: ("Disabled", "mdi:checkbox-blank-circle-outline"),
        255: ("Enabled", "mdi:checkbox-marked-circle-outline"),
    }

    DEFAULTS = {
        "icon": "mdi:check-circle",
        "state_class": None,
    }


# ----------------------------
# Time of Use Charge Enabled
# ----------------------------
class TimeOfUse_ChargeEnabledEntry(RegisterIntEntry):
    DynamicValueDict = {
        0: ("Disabled", "mdi:checkbox-blank-circle-outline"),
        1: ("Enabled", "mdi:checkbox-marked-circle-outline"),
    }

    DEFAULTS = {
        "icon": "mdi:check-circle",
        "state_class": None,
    }


# ----------------------------
# Time of Use Time
# ----------------------------
class TimeOfUse_TimeEntry(RegisterIntEntry):
    DEFAULTS = {
        "icon": "mdi:clock-outline",
        "sensor_class": SensorClass.TOU_TIME,
    }
