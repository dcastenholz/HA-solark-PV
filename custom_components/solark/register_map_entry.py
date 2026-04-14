from enum import Enum
from typing import TYPE_CHECKING

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

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        # This pattern of reading kwargs and then poping the value to get rid of it
        # helps the type checker at design time.
        #address = kwargs["address"]
        self.address = address
        #kwargs.pop("address")

        # When there is a non-None default value, pop with the appropriate default
        # helps the type checking at design time.
        #self.data_type = kwargs.pop("data_type", DataType.INT16)
        self.data_type = data_type

        super().__init__(key, name, **kwargs)

    def _validate(self):
        super()._validate()
        # Address must be non-negative
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
# String
# ----------------------------
class StringEntry(RegisterMapEntry):
    length: int

    def __init__(self, address: int, key: str, name: str, length: int, data_type: DataType = DataType.INT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        # This pattern of reading kwargs and then poping the value to get rid of it
        # helps the type checker at design time.
        #length = kwargs["length"]
        self.length = length
        #kwargs.pop("length")

        super().__init__(address, key, name, data_type, **kwargs)
        self._validate()

    def _validate(self):
        super()._validate()
        # STRING type must have string_register_length defined
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
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:flash")
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Battery Voltage
# ----------------------------
class BatteryVoltageEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:battery-plus-outline")
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("native_unit", NativeUnit.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("suggested_display_precision", 2)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# PV Voltage
# ----------------------------
class PVVoltageEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:solar-power")
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Frequency
# ----------------------------
class FrequencyEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:sine-wave")
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("native_unit", NativeUnit.HZ)
        kwargs.setdefault("device_class", SensorDeviceClass.FREQUENCY)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Current
# ----------------------------
class CurrentEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("native_unit", NativeUnit.A)
        kwargs.setdefault("device_class", SensorDeviceClass.CURRENT)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Battery Current
# ----------------------------
class BatteryCurrentEntry(CurrentEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:current-dc")
        kwargs.setdefault("scale", 1.0)
        kwargs.setdefault("suggested_display_precision", 0)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Power
# ----------------------------
class PowerEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("device_class", SensorDeviceClass.POWER)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("native_unit", NativeUnit.WATT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT32, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.KWH)
        kwargs.setdefault("device_class", SensorDeviceClass.ENERGY)
        kwargs.setdefault("state_class", SensorStateClass.TOTAL)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Energy Total Increasing
# ----------------------------
class EnergyTotalIncreasingEntry(EnergyEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT32, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("state_class", SensorStateClass.TOTAL_INCREASING)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Temperature
# ----------------------------
class TemperatureEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("offset", 1000)
        kwargs.setdefault("native_unit", NativeUnit.CELSIUS)
        kwargs.setdefault("device_class", SensorDeviceClass.TEMPERATURE)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# State of Charge
# ----------------------------
class SOCEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("native_unit", NativeUnit.PERCENT)
        kwargs.setdefault("device_class", SensorDeviceClass.BATTERY)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# State of Charge
# ----------------------------
class TimeOfUseEnabledEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:check-circle")
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("dynamic_icon", SensorDynamicIcon.CHECK_BOX)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Time
# ----------------------------
class TimeOfUseTimeEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:clock-outline")
        kwargs.setdefault("sensor_class", SensorClass.TOU_TIME)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# RawValueEntry
# ----------------------------
class RawValueEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:code-braces")
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# SystemTimeEntry
# ----------------------------
class SystemTimeEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:information-outline")
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)
        kwargs.setdefault("state_class", None)
        kwargs.setdefault("exclude_from_recorder", True)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# GridRelayEntry
# ----------------------------
class GridRelayEntry(MapEntryLookup, RegisterMapEntry):
    LOOKUP_MAP = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
    }

    def __init__(self, address: int, key: str, name: str, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        kwargs.setdefault("state_class", None)
        kwargs.setdefault("post_process", self.post_process_method)

        super().__init__(address, key, name, **kwargs)

    @staticmethod
    def post_process_method(entry: GridRelayEntry, runtime_data: "SolArkData") -> None:
        raw: int = int(entry)
        entry.sensor_value = entry.get_label_from_raw(raw)
