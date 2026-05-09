"""Register map entries for modbus register-backed sensors."""

from __future__ import annotations

import logging
from abc import ABC
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

from .._sensor.sensor_class import SensorClass
from .._sensor.sensor_entity_description import NativeUnit, SolArkSensorEntityDescription
from .._sensor.sensor_mixin import SensorMixin
from ..entry_map.base_entry import BaseRegisterEntry
from ..register_value_types import TSensorValue

if TYPE_CHECKING:
    from ..data import SolArkData

_LOGGER = logging.getLogger(__name__)


# ----------------------------------
# Data Type Enum
# ----------------------------------
# TODO - Unused strings??? convert to auto()
class DataType(Enum):
    """Supported Modbus register data types."""

    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    INT64 = "int64"
    UINT64 = "uint64"


class RegisterEntryOptional(TypedDict, total=False):
    """Optional keyword arguments for register-backed entries."""

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

    # TODO - Is this unused???
    set_sensor_value: Callable[[Any, "SolArkData"], None]
    scale: float
    offset: int


# ----------------------------------
# Register Entry
# ----------------------------------
class BaseRegisterSensorEntry(Generic[TSensorValue], BaseRegisterEntry[SolArkSensorEntityDescription, TSensorValue], SensorMixin[TSensorValue], ABC):
    """
    BaseRegisterSensorEntry[TSensorValue]

        Type Parameters:
            TSensorValue: the type of the sensor display value.

    Abstract base class for all modbus register-backed sensors.
    """

    # ENTITY_DESCRIPTION_CLS = SolArkSensorEntityDescription

    # address: int

    # def __init__(self, address: int, key: str, name: str, **kwargs: Unpack[RegisterEntryOptional]) -> None:
    #     """Initialize a register-backed entry."""
    #     super().__init__(address, key, name, **kwargs)

    # def _create_entity_description(self, entry_class: type[BaseRegisterEntry]) -> SolArkSensorEntityDescription:
    #     return SolArkSensorEntityDescription.from_kwargs(
    #         key=self.key,
    #         name=self.name,
    #         entry_class=entry_class,
    #         opts=self.opts,
    #     )


class RegisterNumericEntry(Generic[TSensorValue], BaseRegisterSensorEntry[TSensorValue], ABC):
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
        """Initialize a numeric register entry."""
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
        """Initialize an integer register entry."""
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
        """Initialize a floating-point register entry."""
        super().__init__(address, key, name, data_type, **kwargs)

        # -----------------------------
        # Store fields using kwargs merged with DEFAULTS
        # -----------------------------
        self.offset = self.opts["offset"]
        self.scale = self.opts["scale"]

    @property
    def sensor_value(self) -> float | None:
        """Return the scaled and offset sensor value."""
        return self._sensor_value

    @sensor_value.setter
    def sensor_value(self: Self, value: int) -> None:
        """Set the scaled and offset sensor value from a raw register value."""
        self._sensor_value = (value - self.offset) * self.scale


# ----------------------------
# Grid Relay
# ----------------------------
class GridRelayEntry(RegisterIntEntry):
    """Register entry for grid relay state."""

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
class StringEntry(BaseRegisterSensorEntry[str]):
    """
    Class for all modbus string register backed string sensors.

        Adds:
            logic for setting base value and sensor value
            the length of the register range to read for string entries
    """
    # TODO - Should we just combine with SerialNumber???  Depends on potential reuse.
    length: int

    def __init__(self, address: int, key: str, name: str, length: int, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        """Initialize a string register entry."""
        self.length = length

        super().__init__(address, key, name, **kwargs)

    def _validate(self):
        # StringEntry must have string_register_length defined
        if self.length is None:
            raise ValueError(f"StringEntry {self._entity_description.key} must have length")

    @property
    def register_length(self) -> int:
        """Return the configured string register length."""
        if not self.length:
            raise ValueError(f"StringEntry missing length for {self._entity_description.key}")
        if self.length < 1:
            raise ValueError(f"StringEntry with length < 1 for {self._entity_description.key}")
        return self.length


# ----------------------------
# Serial Number Entry
# ----------------------------
class SerialNumberEntry(StringEntry):
    """String register entry for the inverter serial number."""

    # TODO - Make sure this is called!!!
    def _post_process(self: Self, runtime_data: "SolArkData") -> None:
        '''Save the serial number to the device info serial number property'''

        # TODO - This must be moved to a location where it will only be run if the register is read
        # just prior to it running.  _post_process is a sledgehammer
        from ..helpers.device_info import SolArkDeviceInfo
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
# TODO - Get rid of this class???
class RawValueSystemTimeEntry(RawInfoEntry):
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
    """Register entry for grid voltage values."""

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
    """Register entry for battery voltage values."""

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
    """Register entry for photovoltaic voltage values."""

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
    """Register entry for frequency values."""

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
    """Register entry for current values."""

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
    """Register entry for battery current values."""

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
    """Register entry for power values."""

    DEFAULTS = {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": NativeUnit.WATT,
    }


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterFloatEntry):
    """Register entry for energy values."""

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
    """Register entry for total increasing energy values."""

    DEFAULTS = {
        "state_class": SensorStateClass.TOTAL_INCREASING,
    }


# ----------------------------
# Temperature
# ----------------------------
class TemperatureEntry(RegisterFloatEntry):
    """Register entry for temperature values."""

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
    """Register entry for state of charge values."""

    DEFAULTS = {
        "native_unit": NativeUnit.PERCENT,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Time of Use Enabled
# ----------------------------
class TimeOfUse_EnabledEntry(RegisterIntEntry):
    """Register entry for time-of-use enabled state."""

    DynamicValueDict = {
        0: ("Disabled", "mdi:checkbox-blank-circle-outline"),
        255: ("Enabled", "mdi:checkbox-marked-circle-outline"),
    }

    DEFAULTS = {
        "icon": "mdi:check-circle",
        "state_class": None,
    }


# ----------------------------
# Time of Use Time
# ----------------------------
class TimeOfUse_TimeEntry(RegisterIntEntry):
    """Register entry for time-of-use time values."""

    DEFAULTS = {
        "icon": "mdi:clock-outline",
        "sensor_class": SensorClass.TOU_TIME,
    }
