import logging
from typing import TYPE_CHECKING, Any, Callable, TypedDict, Unpack

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

from .base_map_entry import BaseMapEntry
from .binary_sensor_class import BinarySensorClass
from .binary_sensor_entity_description import SolArkBinarySensorEntityDescription
from .register_value_types import SensorValue

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensor

_LOGGER = logging.getLogger(__name__)


class BinarySensorMapEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool
    extra_state_attributes: dict[str, Any]
    dynamic_icon: Callable[["SensorValue"], str | None]

    post_process_sensor: Callable[["SolArkSensor", "SolArkData"], None]
    device_class: BinarySensorDeviceClass
    sensor_class: BinarySensorClass

    post_process: Callable[[Any, "SolArkData"], None]


class BinarySensorMapEntry(BaseMapEntry["BinarySensorMapEntry", SolArkBinarySensorEntityDescription]):
    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorMapEntryOptional]) -> None:
        # -----------------------------
        # Set defaults in kwargs once
        # -----------------------------
        kwargs.setdefault("entity_registry_enabled_default", False)
        kwargs.setdefault("exclude_from_recorder", False)

        kwargs.setdefault("sensor_class", BinarySensorClass.BINARY)

        # -----------------------------
        # Normalize into guaranteed dict
        # -----------------------------
        opts: dict[str, Any] = dict(kwargs)

        # -----------------------------
        # entity description build
        # -----------------------------
        self._entity_description = SolArkBinarySensorEntityDescription(
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
        )

        # -----------------------------
        # store fields
        # -----------------------------
        self.post_process = opts.get("post_process")

        self._validate()


# ----------------------------
# Binary
# ----------------------------
class BinaryEntry(BinarySensorMapEntry):
    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorMapEntryOptional]) -> None:
        kwargs.setdefault("device_class", BinarySensorDeviceClass.PROBLEM)
        kwargs.setdefault("sensor_class", BinarySensorClass.BINARY)

        super().__init__(key, name, **kwargs)
