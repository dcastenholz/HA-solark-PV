from enum import Enum

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
)

from .sensor_entity_description import SensorClass, UnitOfMeasure
from .sensor_map_entry import SensorMapEntry


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
    address: int
    data_type: DataType

    def __init__(
        self,
        key: str,
        address: int,
        **kwargs,
    ) -> None:
        data_type = kwargs.pop("data_type", DataType.INT16)

        self.address = address
        self.data_type = data_type

        super().__init__(key=key, **kwargs)
        self._validate()

    def _validate(self):
        super()._validate()
        # Address must be non-negative
        if self.address < 0:
            raise ValueError(f"RegisterMapEntry {self._entity_description.key} must have a non-negative address")

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

    def __init__(self, length: int, **kwargs):
        self.length = length

        super().__init__(**kwargs,)
        self._validate()

    def _validate(self):
        super()._validate()
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
