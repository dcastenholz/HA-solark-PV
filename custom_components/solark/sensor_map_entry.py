import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, TypedDict, Unpack, cast

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from .base_map_entry import BaseMapEntry
from .config_sensor import ConfigSensor
from .map_entry_lookup import MapEntryLookup
from .register_value_types import SensorValue
from .sensor_entity_description import NativeUnit, SensorClass, SolArkSensorEntityDescription

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkStaticValueSensor

_LOGGER = logging.getLogger(__name__)


class SensorMapEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool
    dynamic_icon: Callable[["SensorValue"], str | None]

    on_sensor_creating: Callable[["SolArkStaticValueSensor", "SolArkData"], None]
    device_class: SensorDeviceClass
    sensor_class: SensorClass

    suggested_display_precision: int
    state_class: Optional[SensorStateClass]
    native_unit: NativeUnit

    on_data_updated: Callable[[Any, "SolArkData"], None]
    scale: float
    offset: int


class SensorMapEntry(BaseMapEntry["SensorMapEntry", "SolArkSensorEntityDescription"]):
    scale: float
    offset: int
    state_class: SensorStateClass | None

    DEFAULTS = {
        "exclude_from_recorder": False,

        "sensor_class": SensorClass.NORMAL,

        "scale": 1.0,
        "offset": 0,
    }

    def __init__(self, key: str, name: str, **kwargs: Unpack[SensorMapEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

        # -----------------------------
        # Normalize into guaranteed dict
        # -----------------------------
        opts = self.opts

        # -----------------------------
        # entity description build
        # -----------------------------
        self._entity_description = SolArkSensorEntityDescription.from_kwargs(
            key=key,
            name=name,
            opts=opts
        )

        # -----------------------------
        # store fields
        # -----------------------------
        self.data_updated = opts.get("on_data_updated")
        self.scale = opts["scale"]
        self.offset = opts["offset"]


# ----------------------------
# Power
# ----------------------------
class PowerEntry(SensorMapEntry):
    DEFAULTS = {
        "native_unit": NativeUnit.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    }


# ----------------------------
# Energy Total Increasing
# ----------------------------
class EnergyTotalIncreasingEntry(SensorMapEntry):
    DEFAULTS = {
        "scale": 0.1,
        "native_unit": NativeUnit.KWH,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    }


# ----------------------------
# Diagnostic
# ----------------------------
class DiagnosticEntry(SensorMapEntry):
    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    }


# ----------------------------
# Config
# ----------------------------
class ConfigEntry(SensorMapEntry):
    # @staticmethod
    # def data_updated(entry: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    #     entry.sensor_value = runtime_data.name
    #     return

    @staticmethod
    def sensor_creating(sensor: "SolArkStaticValueSensor", runtime_data: "SolArkData") -> None:
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
class GeneratorRelayEntry(MapEntryLookup, SensorMapEntry):
    LOOKUP_MAP = {
        0: ("Open", "mdi:electric-switch"),
        1: ("Closed", "mdi:electric-switch-closed"),
        2: ("No Connection", "mdi:connection"),
        3: ("Closed when Generator is on", "mdi:generator-portable"),
    }

    @staticmethod
    def data_updated(entry: "GeneratorRelayEntry", runtime_data: "SolArkData") -> None:
        raw: int = cast(int, runtime_data.register_map.GEN_RLY_RAW.register_value) & 0x0F  # mask low 4 bits
        entry.sensor_value = entry.get_label_from_raw(raw)

    DEFAULTS = {
        "state_class": None,
        "on_data_updated": data_updated,
    }
