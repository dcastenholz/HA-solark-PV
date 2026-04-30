import logging
from typing import TYPE_CHECKING, Any, Callable, Self, TypedDict, Unpack, cast

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

from .base_map_entry import BaseEntry
from .binary_sensor_class import BinarySensorClass
from .binary_sensor_entity_description import SolArkBinarySensorEntityDescription
from .coordinator_metrics import CoordinatorMetrics
from .register_value_types import SensorValue

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkSensorEntity

_LOGGER = logging.getLogger(__name__)


class BinarySensorEntryOptional(TypedDict, total=False):
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool
    dynamic_icon: Callable[["SensorValue"], str | None]

    on_sensor_creating: Callable[["SolArkSensorEntity", "SolArkData"], None]
    device_class: BinarySensorDeviceClass
    sensor_class: BinarySensorClass

    on_data_updated: Callable[[Any, "SolArkData"], None]


class BinarySensorEntry(BaseEntry[SolArkBinarySensorEntityDescription, bool, bool, bool]):
    """
    Abstract base class for all binarysensor entries.
    """

    DEFAULTS = {
        "sensor_class": BinarySensorClass.BINARY,
    }

    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

    def set_sensor_value(self, runtime_data: "SolArkData") -> None:
        # TODO - Get rid of cast
        # self._sensor_value = cast(bool, self._base_value)
        self._sensor_value = self._base_value

    def _create_entity_description(self) -> SolArkBinarySensorEntityDescription:
        return SolArkBinarySensorEntityDescription.from_kwargs(
            key=self.key,
            name=self.name,
            opts=self.opts,
        )

    def dynamic_lookup_key(self, runtime_data: "SolArkData") -> bool | None:
        return self.sensor_value


# ----------------------------
# Binary
# ----------------------------
class BinaryProblemEntry(BinarySensorEntry):
    DEFAULTS = {
        "device_class": BinarySensorDeviceClass.PROBLEM,
    }

class MetricsSuccessEntry(BinarySensorEntry):
    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "name_prefix": "Metric: ",
    }

    LOOKUP_MAP = {
        True: ("Success", "mdi:electric-switch"),
        False: ("Failure", "mdi:electric-switch-closed"),
    }

    def dynamic_lookup_key(self, runtime_data: "SolArkData"):
        return self.sensor_value

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

    def _post_process(self: Self, runtime_data: "SolArkData") -> None:
        # get metric result and store it as sensor value
        self._sensor_value = self.metric(runtime_data.coordinator_metrics)

