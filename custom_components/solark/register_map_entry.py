from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Optional, TypedDict

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)
from typing_extensions import Unpack

from .map_entry_lookup import EntryLookup
from .register_value_types import RegisterValue, SensorValue
from .sensor_dynamic_icon import SensorDynamicIcon
from .sensor_entity_description import NativeUnit, SensorClass
from .sensor_map_entry import SensorEntry

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensorEntity


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
    dynamic_icon: Callable[["SensorValue"], str | None]

    on_sensor_creating: Callable[["SolArkSensorEntity", "SolArkData"], None]
    device_class: SensorDeviceClass
    sensor_class: SensorClass

    suggested_display_precision: int
    state_class: Optional[SensorStateClass]
    native_unit: NativeUnit

    on_data_updated: Callable[[Any, "SolArkData"], None]
    scale: float
    offset: int


# ----------------------------------
# Register Map Entry
# ----------------------------------
class RegisterEntry(SensorEntry):
    """
    Modbus register-backed entry.

    Adds:
    - address
    - data type
    - register sizing logic
    """
    address: int
    data_type: DataType
    scale: float
    offset: int

    _register_value: RegisterValue

    DEFAULTS = {
        "scale": 1.0,
        "offset": 0,
    }

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[RegisterEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

        self.address = address
        self.data_type = data_type

        # -----------------------------
        # Store fields using kwargs merged with DEFAULTS
        # -----------------------------
        self.scale = self.opts["scale"]
        self.offset = self.opts["offset"]

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
        # RegisterEntry must have non-negative address
        if self.address < 0:
            raise ValueError(f"RegisterEntry {self._entity_description.key}: address must be >= 0")

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
# String
# ----------------------------
class StringEntry(RegisterEntry):
    length: int

    def __init__(self, address: int, key: str, name: str, length: int, data_type: DataType = DataType.INT16, **kwargs: Unpack[RegisterEntryOptional]) -> None:
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
# Serial Number Entry
# ----------------------------
class SerialNumberEntry(StringEntry):
    @staticmethod
    def _data_updated(entry: SerialNumberEntry, runtime_data: "SolArkData") -> None:
        '''Save the serial number to the device info serial number property'''

        from .device_info import SolArkDeviceInfo
        SolArkDeviceInfo.handle_serial_number_change(runtime_data, str(entry.sensor_value))

    DEFAULTS = {
        "on_data_updated": _data_updated,
    }


# ----------------------------
# Raw Value
# ----------------------------
class RawValueEntry(RegisterEntry):
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
class RawInfoEntry(RegisterEntry):
    '''Values read from registers that are not normally displayed in UI screens.
    These are mostly static values that do not typically change over time.'''

    DEFAULTS = {
        "icon": "mdi:code-braces",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": None,
        # "on_sensor_creating": sensor_creating,
        "name_prefix": "Raw Info: ",
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
# Grid Voltage
# ----------------------------
class GridVoltageEntry(RegisterEntry):
    DEFAULTS = {
        "icon": "mdi:flash",
        "scale": 0.1,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Battery Voltage
# ----------------------------
class BatteryVoltageEntry(RegisterEntry):
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
class PVVoltageEntry(RegisterEntry):
    DEFAULTS = {
        "icon": "mdi:solar-power",
        "scale": 0.1,
        "native_unit": NativeUnit.V,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Frequency
# ----------------------------
class FrequencyEntry(RegisterEntry):
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
class CurrentEntry(RegisterEntry):
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
class PowerEntry(RegisterEntry):
    DEFAULTS = {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": NativeUnit.WATT,
    }


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterEntry):
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
class TemperatureEntry(RegisterEntry):
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
class SOCEntry(RegisterEntry):
    DEFAULTS = {
        "native_unit": NativeUnit.PERCENT,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# State of Charge
# ----------------------------
class TimeOfUseEnabledEntry(RegisterEntry):
    DEFAULTS = {
        "icon": "mdi:check-circle",
        "state_class": SensorStateClass.MEASUREMENT,
        "dynamic_icon": SensorDynamicIcon.CHECK_BOX,
    }


# ----------------------------
# Time
# ----------------------------
class TimeOfUseTimeEntry(RegisterEntry):
    DEFAULTS = {
        "icon": "mdi:clock-outline",
        "sensor_class": SensorClass.TOU_TIME,
    }


# ----------------------------
# Grid Relay
# ----------------------------
class GridRelayEntry(EntryLookup, RegisterEntry):
    LOOKUP_MAP = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
    }

    @staticmethod
    def _data_updated(entry: "GridRelayEntry", runtime_data: "SolArkData") -> None:
        entry.set_mapped_sensor_value(entry)
        # raw: int = int(entry)
        # entry.sensor_value = entry.get_label_from_raw(raw)

    DEFAULTS = {
        "state_class": None,
        "on_data_updated": _data_updated,
    }
