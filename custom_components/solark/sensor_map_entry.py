import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, TypedDict, Unpack, cast
from unittest.mock import DEFAULT

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from .base_map_entry import BaseMapEntry
from .map_entry_lookup import MapEntryLookup
from .register_value_types import SensorValue
from .sensor_entity_description import NativeUnit, SensorClass, SolArkSensorEntityDescription

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensor

_LOGGER = logging.getLogger(__name__)


class SensorMapEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool
    extra_state_attributes: dict[str, Any]
    dynamic_icon: Callable[["SensorValue"], str | None]

    post_process_sensor: Callable[["SolArkSensor", "SolArkData"], None]
    device_class: SensorDeviceClass
    sensor_class: SensorClass

    suggested_display_precision: int
    state_class: Optional[SensorStateClass]
    native_unit: NativeUnit

    post_process: Callable[[Any, "SolArkData"], None]
    scale: float
    offset: int


class SensorMapEntry(BaseMapEntry["SensorMapEntry", "SolArkSensorEntityDescription"]):
    scale: float
    offset: int
    state_class: SensorStateClass | None

    DEFAULTS = {
        "entity_registry_enabled_default": False,
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
        # opts: dict[str, Any] = dict(kwargs)
        opts = self.opts

        # -----------------------------
        # entity description build
        # -----------------------------
        self._entity_description = SolArkSensorEntityDescription(
            key=key,
            name=name,

            icon=opts.get("icon"),
            entity_registry_enabled_default=opts["entity_registry_enabled_default"],
            entity_category=opts.get("entity_category"),
            description=opts.get("description"),
            exclude_from_recorder=opts["exclude_from_recorder"],
            should_poll=opts.get("should_poll"),
            extra_state_attributes=opts.get("extra_state_attributes") or {},
            dynamic_icon=opts.get("dynamic_icon"),

            post_process_sensor=opts.get("post_process_sensor"),
            device_class=opts.get("device_class"),
            sensor_class=opts["sensor_class"],

            suggested_display_precision=opts.get("suggested_display_precision"),
            state_class=opts.get("state_class"),
            native_unit=opts.get("native_unit"),
        )

        # -----------------------------
        # store fields
        # -----------------------------
        self.post_process = opts.get("post_process")
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
    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_class": SensorClass.BASE,
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
    def post_process_method(entry: "GeneratorRelayEntry", runtime_data: "SolArkData") -> None:
        raw: int = cast(int, runtime_data.register_map.GEN_RLY_RAW.register_value) & 0x0F  # mask low 4 bits
        entry.sensor_value = entry.get_label_from_raw(raw)

    DEFAULTS = {
        "state_class": None,
        "post_process": post_process_method,
    }
