"""Sensor map entries for SolArk."""

import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Generic, Self

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from .._sensor.sensor_class import SensorClass
from .._sensor.sensor_entity_description import NativeUnit, SolArkSensorEntityDescription
from .._sensor.sensor_mixin import SensorMixin
from ..coordinator.coordinator_metrics import CoordinatorMetrics
from ..entry_map.base_entry import BaseEntry
from ..register_value_types import TSensorValue

if TYPE_CHECKING:
    from ..data import SolArkData


_LOGGER = logging.getLogger(__name__)


class BaseSensorEntry(Generic[TSensorValue], BaseEntry[SolArkSensorEntityDescription, TSensorValue], SensorMixin[TSensorValue], ABC):
    """
    BaseSensorEntry[TSensorValue]

        Type Parameters:
            TSensorValue: the type of the sensor display value.

    Abstract base class for all sensors.

        Provides:
            state class
    """

    state_class: SensorStateClass | None

    DEFAULTS = {
        "sensor_class": SensorClass.COORDINATOR,
    }


# TODO - Review all uses of this class for possible BaseSensorEntry inheritance instead
class SensorEntry_NoSet(Generic[TSensorValue], BaseSensorEntry[TSensorValue]):
    """Sensor entry that uses the default sensor value behavior."""

    pass


class MetricsEntry(BaseSensorEntry):
    """Sensor entry backed by coordinator metrics."""

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "sensor_class": SensorClass.METRICS,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "name_prefix": "Metric: ",
    }

    def __init__(
        self,
        key: str,
        name: str,
        # TODO - Can this be moved to set_sensor_value???
        metric: Callable[[CoordinatorMetrics], Any],
    ) -> None:
        """Initialize the metrics entry."""
        self.metric = metric

        super().__init__(
            key,
            name,
        )

    def calc_sensor_value(self: Self, runtime_data: "SolArkData") -> None:
        """Calculate the sensor value from coordinator metrics."""
        self._sensor_value = self.metric(runtime_data.coordinator_metrics)


# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorEntry_NoSet[float]):
    """Sensor entry for power values."""

    DEFAULTS = {
        "native_unit": NativeUnit.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Energy Total Increasing
# ----------------------------
class EnergyTotalIncreasingCalculatedEntry(SensorEntry_NoSet[float]):
    """Sensor entry for total increasing energy values."""

    DEFAULTS = {
        "native_unit": NativeUnit.KWH,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    }


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorEntry_NoSet[str]):
    """Sensor entry for diagnostic values."""

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    }


# ----------------------------
# Config
# ----------------------------
class ConfigEntry(SensorEntry_NoSet[str]):
    """Sensor entry for configuration values."""

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_class": SensorClass.CONFIG,
        "should_poll": False,
        "exclude_from_recorder": True,
    }


# ----------------------------
# Generator Relay
# ----------------------------
class GeneratorRelayEntry(BaseSensorEntry[int]):
    """Sensor entry for generator relay state."""

    # This is the most fundamental value that is read from the registers
    _register_value_low_4_bits: int

    DynamicValueAndIcon = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
        2: ("No Connection", "mdi:connection"),
        3: ("Closed when Generator is on", "mdi:generator-portable"),
    }

    def calc_sensor_value(self, runtime_data: "SolArkData") -> None:
        """Calculate generator relay state from the raw register value."""
        _register_value_low_4_bits = runtime_data.register_map.GEN_RLY_RAW.sensor_value
        self._sensor_value = (_register_value_low_4_bits & 0x0F) if _register_value_low_4_bits is not None else None  # mask low 4 bits

    DEFAULTS = {
        "state_class": None,
    }


# ----------------------------
# Battery Measurement Mode
# ----------------------------
class BatteryMeasurementModeEntry(BaseSensorEntry[int]):
    """Sensor entry for battery measurement mode."""

    DynamicValueAndIcon = {
        0: ("Voltage", "mdi:battery-unknown"),
        1: ("SOC", "mdi:battery-unknown"),
        2: ("No Battery", "mdi:battery-off-outline"),
    }

    def calc_sensor_value(self, runtime_data: "SolArkData") -> None:
        """Calculate battery measurement mode from the raw register value."""
        value = runtime_data.register_map.BATT_MEASURE_MODE_RAW.sensor_value
        self._sensor_value = (value & 0x0F) if value is not None else None  # mask low 4 bits

    DEFAULTS = {
        "state_class": None,
    }


# ----------------------------
# Time of Use Enabled
# ----------------------------
class TimeOfUse_EnabledEntry(BaseSensorEntry[bool]):
    """Sensor entry for overall or per-day time-of-use enabled state."""

    # DAYS_OF_WEEK = {
    #     1: "Monday",
    #     2: "Tuesday",
    #     3: "Wednesday",
    #     4: "Thursday",
    #     5: "Friday",
    #     6: "Saturday",
    #     7: "Sunday",
    # }

    DynamicValueAndIcon = {
        False: ("Disabled", "mdi:checkbox-blank-circle-outline"),
        True: ("Enabled", "mdi:checkbox-marked-circle-outline"),
    }

    def __init__(self, *, enabled_index: int, **kwargs):
        if enabled_index not in range(8):
            raise ValueError("enabled_index must be between 0 and 7")

        super().__init__(**kwargs)
        self.enabled_index = enabled_index

    # @property
    # def day_of_week(self) -> str | None:
    #     """Return the selected weekday, or None for overall enable."""
    #     return self.DAYS_OF_WEEK.get(self.enabled_index)

    def calc_sensor_value(self, runtime_data: "SolArkData") -> None:
        raw_value = runtime_data.register_map.TIMEOFUSE_ENABLED_RAW.sensor_value
        self._sensor_value = bool(int(raw_value) & (1 << self.enabled_index))

    DEFAULTS = {
        "state_class": None,
    }
