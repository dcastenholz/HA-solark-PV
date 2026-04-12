from enum import Enum
from typing import Union

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)
from typing_extensions import Unpack

from .base_map_entry import BaseMapEntry, BaseMapEntryOptional
from .register_value_types import NumericValue
from .sensor_dynamic_icon import SensorDynamicIcon
from .sensor_entity_description import NativeUnit, SensorClass


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
class RegisterMapEntry(BaseMapEntry["RegisterMapEntry"]):
    """
    Modbus register-backed entry.

    Adds:
    - address
    - data type
    - register sizing logic
    """
    address: int
    data_type: DataType

    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
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

    # -----------------------------
    # Numeric helpers
    # -----------------------------
    def _get_numeric(self) -> NumericValue:
        if isinstance(self.register_value, (int, float)):
            return self.register_value
        raise TypeError(
            f"Non-numeric register_value for {self._entity_description.key}: "
            f"{self.register_value}"
        )

    def __add__(self, other: Union[RegisterMapEntry, NumericValue]) -> NumericValue:
        left = self._get_numeric()

        if isinstance(other, RegisterMapEntry):
            return left + other._get_numeric()

        if isinstance(other, (int, float)):
            return left + other

        return NotImplemented

    def __radd__(self, other: NumericValue) -> NumericValue:
        if isinstance(other, (int, float)):
            return other + self._get_numeric()
        return NotImplemented

    def __int__(self) -> int:
        return int(self._get_numeric())

    def __float__(self) -> float:
        return float(self._get_numeric())

    def split_bytes_uint16(self) -> tuple[int, int]:
        """Split a UINT16 into two 8-bit integers (high byte, low byte)."""
        value: int = int(self)
        if not 0 <= value <= 0xFFFF:
            raise ValueError("Value must be in range 0..65535 (UINT16)")

        high = (value >> 8) & 0xFF
        low = value & 0xFF
        return high, low

# ----------------------------
# String
# ----------------------------
class StringEntry(RegisterMapEntry):
    length: int

    def __init__(self, address: int, key: str, name: str, length: int, data_type: DataType = DataType.INT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
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
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:flash")
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Battery Voltage
# ----------------------------
class BatteryVoltageEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
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
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:solar-power")
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.V)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Frequency
# ----------------------------
class FrequencyEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
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
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("scale", 0.01)
        kwargs.setdefault("native_unit", NativeUnit.A)
        kwargs.setdefault("device_class", SensorDeviceClass.CURRENT)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Battery Current
# ----------------------------
class BatteryCurrentEntry(CurrentEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:battery-charging-outline")
        kwargs.setdefault("scale", 1.0)
        kwargs.setdefault("suggested_display_precision", 0)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Power
# ----------------------------
class PowerEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.INT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("device_class", SensorDeviceClass.POWER)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("native_unit", NativeUnit.WATT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Energy
# ----------------------------
class EnergyEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT32, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("scale", 0.1)
        kwargs.setdefault("native_unit", NativeUnit.KWH)
        kwargs.setdefault("device_class", SensorDeviceClass.ENERGY)
        kwargs.setdefault("state_class", SensorStateClass.TOTAL)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Temperature
# ----------------------------
class TemperatureEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
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
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("native_unit", NativeUnit.PERCENT)
        kwargs.setdefault("device_class", SensorDeviceClass.BATTERY)
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# State of Charge
# ----------------------------
class TimeOfUseEnabledEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:check-circle")
        kwargs.setdefault("state_class", SensorStateClass.MEASUREMENT)
        kwargs.setdefault("dynamic_icon", SensorDynamicIcon.CHECK_BOX)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# Time
# ----------------------------
class TimeOfUseTimeEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:clock-outline")
        kwargs.setdefault("sensor_class", SensorClass.TOU_TIME)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# RawValueEntry
# ----------------------------
class RawValueEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:code-braces")
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)

        super().__init__(address, key, name, data_type, **kwargs)


# ----------------------------
# SystemTimeEntry
# ----------------------------
class SystemTimeEntry(RegisterMapEntry):
    def __init__(self, address: int, key: str, name: str, data_type: DataType = DataType.UINT16, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        kwargs.setdefault("icon", "mdi:information-outline")
        kwargs.setdefault("entity_category", EntityCategory.DIAGNOSTIC)
        kwargs.setdefault("state_class", None)
        kwargs.setdefault("exclude_from_recorder", True)

        super().__init__(address, key, name, data_type, **kwargs)
