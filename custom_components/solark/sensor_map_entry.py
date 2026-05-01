import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, Self, TypedDict, Unpack

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from .base_map_entry import BaseEntry
from .config_sensor import ConfigSensor
from .coordinator_metrics import CoordinatorMetrics
from .register_value_types import TBaseValue, TLookupMapKey, TSensorValue
from .sensor_entity_description import NativeUnit, SensorClass, SolArkSensorEntityDescription

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensorEntity

_LOGGER = logging.getLogger(__name__)


class BaseSensorEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool

    on_sensor_creating: Callable[["SolArkSensorEntity", "SolArkData"], None]
    device_class: SensorDeviceClass
    sensor_class: SensorClass

    # TODO - Eliminate suggested_display_precision. Should always be calculated from scale
    suggested_display_precision: int
    state_class: Optional[SensorStateClass]
    native_unit: NativeUnit

    set_sensor_value_method: Callable[[Any, "SolArkData"], None]


class BaseSensorEntry(Generic[TBaseValue, TSensorValue, TLookupMapKey],
                  BaseEntry["SolArkSensorEntityDescription", TBaseValue, TSensorValue, TLookupMapKey], ABC):
    """
    BaseSensorEntry[TBaseValue, TSensorValue]

    Type Parameters:
        TBaseValue: the type of the base value.
        TSensorValue: the type of the sensor display value.
        TLookupMapKey: the type of the dynamic lookup key value.

    Abstract base class for all sensor entries.

        Adds:
            state class
    """

    state_class: SensorStateClass | None

    DEFAULTS = {
        "sensor_class": SensorClass.COORDINATOR,
    }

    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseSensorEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

    def _create_entity_description(self, entry_class: type[BaseEntry]) -> SolArkSensorEntityDescription:
        return SolArkSensorEntityDescription.from_kwargs(
            key=self.key,
            name=self.name,
            entry_class=entry_class,
            opts=self.opts,
        )


# TODO - Review all uses of this class for possible BaseSensorEntry inheritance instead
class SensorEntry_NoSet(Generic[TSensorValue], BaseSensorEntry[TSensorValue, TSensorValue, TSensorValue]):

    def calc_sensor_value(self, runtime_data: "SolArkData") -> None:
        self._sensor_value = self.base_value


class MetricsEntry(BaseSensorEntry):
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
        metric: Callable[[CoordinatorMetrics], Any],
    ) -> None:
        self.metric = metric

        super().__init__(
            key,
            name,
        )

    def calc_sensor_value(self: Self, runtime_data: "SolArkData") -> None:
        # get metric result and store it as sensor value
        self._sensor_value = self.metric(runtime_data.coordinator_metrics)

# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorEntry_NoSet[float]):
    DEFAULTS = {
        "native_unit": NativeUnit.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Energy Total Increasing
# ----------------------------
class EnergyTotalIncreasingCalculatedEntry(SensorEntry_NoSet[float]):
    DEFAULTS = {
        "native_unit": NativeUnit.KWH,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    }


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorEntry_NoSet[str]):
    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    }


# ----------------------------
# Config
# ----------------------------
class ConfigEntry(SensorEntry_NoSet[str]):
    @staticmethod
    def sensor_creating(sensor: "SolArkSensorEntity", runtime_data: "SolArkData") -> None:
        sensor._attr_native_value = runtime_data.name   # pylint: disable=protected-access
        sensor.extra_state_attributes = ConfigSensor.get_data(runtime_data.config_entry)
        return

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_class": SensorClass.STATIC_VALUE,
        "on_sensor_creating": sensor_creating,
        "should_poll": False,
        "exclude_from_recorder": True,
    }


# ----------------------------
# Generator Relay
# ----------------------------
class GeneratorRelayEntry(BaseSensorEntry[int, int, int]):
    # This is the most fundamental value that is read from the registers
    _register_value_low_4_bits: int

    DynamicValueDict = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
        2: ("No Connection", "mdi:connection"),
        3: ("Closed when Generator is on", "mdi:generator-portable"),
    }

    def calc_sensor_value(self, runtime_data: "SolArkData") -> None:
        value = runtime_data.register_map.GEN_RLY_RAW.register_value
        self._sensor_value = (value & 0x0F) if value is not None else None  # mask low 4 bits

    DEFAULTS = {
        "state_class": None,
    }
