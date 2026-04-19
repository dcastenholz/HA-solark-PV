from enum import Enum
from typing import TYPE_CHECKING, Self

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)
from typing_extensions import Unpack

from .map_entry_lookup import MapEntryLookup
from .register_value_types import RegisterValue, SensorValue
from .sensor_dynamic_icon import SensorDynamicIcon
from .sensor_entity_description import NativeUnit, SensorClass
from .sensor_map_entry import SensorMapEntry, SensorMapEntryOptional

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensorEntity


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


# ----------------------------------
# Register Map Entry
# ----------------------------------
class RegisterMapEntry(SensorMapEntry):
    """
    Modbus register-backed entry.

    Adds:
    - address
    - data type
    - register sizing logic
    """
    address: int
    data_type: DataType

    _register_value: RegisterValue

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        self.address = address
        self.data_type = data_type

        super().__init__(key, name, **kwargs)

    @property
    def register_value(self) -> RegisterValue:
        return self._register_value

    @register_value.setter
    def register_value(self, value: RegisterValue) -> None:
        self.sensor_value = None
        self._register_value = value

    @property
    def sensor_value(self) -> SensorValue:
        if self._sensor_value is not None:
            return self._sensor_value
        return self.register_value

    @sensor_value.setter
    def sensor_value(self, value: SensorValue) -> None:
        self._sensor_value = value

    def _validate(self):
        # RegisterMapEntry must have non-negative address
        if self.address < 0:
            raise ValueError(f"RegisterMapEntry {self._entity_description.key}: address must be >= 0")

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

# ----------------------------
# Raw Value
# ----------------------------
class RawValueEntry(RegisterMapEntry):
    '''Values read from registers that are not normally displayed in UI screens.
    These are values that change over time and will produce history if enabled.'''

    RAW_PREFIX = "Raw Value -"

    @staticmethod
    def sensor_creating(sensor: "SolArkSensorEntity", runtime_data: "SolArkData") -> None:
        name = str(sensor.name)
        if name and not name.startswith(RawValueEntry.RAW_PREFIX):
            sensor.name = RawValueEntry.RAW_PREFIX + name

    DEFAULTS = {
        "icon": "mdi:code-braces",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": SensorStateClass.MEASUREMENT,
        "on_sensor_creating": sensor_creating,
    }


# ----------------------------
# Raw Value
# ----------------------------
class RawInfoEntry(RegisterMapEntry):
    '''Values read from registers that are not normally displayed in UI screens.
    These are mostly static values that do not typically change over time.'''

    RAW_PREFIX = "Raw Info -"

    @staticmethod
    def sensor_creating(sensor: "SolArkSensorEntity", runtime_data: "SolArkData") -> None:
        name = str(sensor.name)
        if name and not name.startswith(RawValueEntry.RAW_PREFIX):
            sensor.name = RawValueEntry.RAW_PREFIX + name

    DEFAULTS = {
        "state_class": None,
        "on_sensor_creating": sensor_creating,
    }


# ----------------------------
# Raw Value System Time
# ----------------------------
class RawValueSystemTimeEntry(RawValueEntry):
    '''Values read from registers that are not normally displayed in UI screens.
    These are values that are based on the inverter system time but are specifically
    excluded from history to avoid pointless database entries.'''

    DEFAULTS = {
        # "exclude_from_recorder": True,
    }


# ----------------------------
# String
# ----------------------------
class StringEntry(RegisterMapEntry):
    length: int

    def __init__(self, address: int, key: str, name: str, length: int, data_type: DataType = DataType.INT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        self.length = length

        super().__init__(address, key, name, data_type, **kwargs)

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
# Grid Voltage
# ----------------------------
class GridVoltageEntry(RegisterMapEntry):
    DEFAULTS = {
        "icon": "mdi:flash",
        "scale": 0.1,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Battery Voltage
# ----------------------------
class BatteryVoltageEntry(RegisterMapEntry):
    DEFAULTS = {
        "icon": "mdi:battery-plus-outline",
        "scale": 0.01,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
        "suggested_display_precision": 2,
    }


# ----------------------------
# PV Voltage
# ----------------------------
class PVVoltageEntry(RegisterMapEntry):
    DEFAULTS = {
        "icon": "mdi:solar-power",
        "scale": 0.1,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Frequency
# ----------------------------
class FrequencyEntry(RegisterMapEntry):
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
class CurrentEntry(RegisterMapEntry):
    DEFAULTS = {
        "scale": 0.01,
        "native_unit": NativeUnit.A,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Battery Current
# ----------------------------
class BatteryCurrentEntry(CurrentEntry):
    DEFAULTS = {
        "icon": "mdi:current-dc",
        "scale": 1.0,
        "suggested_display_precision": 0,
    }


# ----------------------------
# Power
# ----------------------------
class PowerEntry(RegisterMapEntry):
    DEFAULTS = {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": NativeUnit.WATT,
    }


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterMapEntry):
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
class TemperatureEntry(RegisterMapEntry):
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
class SOCEntry(RegisterMapEntry):
    DEFAULTS = {
        "native_unit": NativeUnit.PERCENT,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# State of Charge
# ----------------------------
class TimeOfUseEnabledEntry(RegisterMapEntry):
    DEFAULTS = {
        "icon": "mdi:check-circle",
        "state_class": SensorStateClass.MEASUREMENT,
        "dynamic_icon": SensorDynamicIcon.CHECK_BOX,
    }


# ----------------------------
# Time
# ----------------------------
class TimeOfUseTimeEntry(RegisterMapEntry):
    DEFAULTS = {
        "icon": "mdi:clock-outline",
        "sensor_class": SensorClass.TOU_TIME,
    }


# ----------------------------
# Grid Relay
# ----------------------------
class GridRelayEntry(MapEntryLookup, RegisterMapEntry):
    LOOKUP_MAP = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
    }

    @staticmethod
    def _data_updated(entry: "GridRelayEntry", runtime_data: "SolArkData") -> None:
        raw: int = int(entry)
        entry.sensor_value = entry.get_label_from_raw(raw)

    DEFAULTS = {
        "state_class": None,
        "on_data_updated": _data_updated,
    }
