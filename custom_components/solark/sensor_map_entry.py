import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, TypedDict, Unpack, cast

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from .base_map_entry import BaseEntry
from .config_sensor import ConfigSensor
from .coordinator_metrics import CoordinatorMetrics
from .map_entry_lookup import EntryLookup
from .register_value_types import SensorValue
from .sensor_entity_description import NativeUnit, SensorClass, SolArkSensorEntityDescription

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensorEntity

_LOGGER = logging.getLogger(__name__)


class SensorEntryOptional(TypedDict, total=False):
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


class SensorEntry(BaseEntry["SolArkSensorEntityDescription"]):
    state_class: SensorStateClass | None

    DEFAULTS = {
        "sensor_class": SensorClass.NORMAL,
    }

    def __init__(self, key: str, name: str, **kwargs: Unpack[SensorEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

    def _create_entity_description(self) -> SolArkSensorEntityDescription:
        return SolArkSensorEntityDescription.from_kwargs(
            key=self.key,
            name=self.name,
            opts=self.opts,
        )


class MetricsEntry(SensorEntry):
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
            on_data_updated=self._on_data_updated,
        )

    def _on_data_updated(self, entry: Any, runtime_data: "SolArkData") -> None:
        # get metric result and store it as sensor value
        entry.sensor_value = self.metric(runtime_data.coordinator_metrics)

# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorEntry):
    DEFAULTS = {
        "native_unit": NativeUnit.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Energy Total Increasing
# ----------------------------
class EnergyTotalIncreasingCalculatedEntry(SensorEntry):
    DEFAULTS = {
        "native_unit": NativeUnit.KWH,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    }


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorEntry):
    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    }


# ----------------------------
# Config
# ----------------------------
class ConfigEntry(SensorEntry):
    # @staticmethod
    # def data_updated(entry: "SensorEntry", runtime_data: "SolArkData") -> None:
    #     entry.sensor_value = runtime_data.name
    #     return

    @staticmethod
    def sensor_creating(sensor: "SolArkSensorEntity", runtime_data: "SolArkData") -> None:
        sensor._attr_native_value = runtime_data.name   # pylint: disable=protected-access
        sensor.extra_state_attributes = ConfigSensor.get_data(runtime_data.config_entry)
        return

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_class": SensorClass.STATIC_VALUE,
        # "on_data_updated": data_updated,
        "on_sensor_creating": sensor_creating,
        "should_poll": False,
        "exclude_from_recorder": True,
    }


# ----------------------------
# Generator Relay
# ----------------------------
class GeneratorRelayEntry(EntryLookup, SensorEntry):
    LOOKUP_MAP = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
        2: ("No Connection", "mdi:connection"),
        3: ("Closed when Generator is on", "mdi:generator-portable"),
    }

    @staticmethod
    def _data_updated(entry: "GeneratorRelayEntry", runtime_data: "SolArkData") -> None:
        entry.sensor_value = cast(int, runtime_data.register_map.GEN_RLY_RAW.register_value) & 0x0F  # mask low 4 bits
        entry.set_mapped_sensor_value(entry)
        # unmapped_sensor_value: int = cast(int, runtime_data.register_map.GEN_RLY_RAW.register_value) & 0x0F  # mask low 4 bits
        # entry.sensor_value = entry.get_label_from_raw(unmapped_sensor_value)

    DEFAULTS = {
        "state_class": None,
        "on_data_updated": _data_updated,
    }
