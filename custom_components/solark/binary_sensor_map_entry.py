import logging
from typing import TYPE_CHECKING, Any, Callable, TypedDict, Unpack

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


class BinarySensorEntry(BaseEntry[SolArkBinarySensorEntityDescription]):
    DEFAULTS = {
        "sensor_class": BinarySensorClass.BINARY,
    }

    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorEntryOptional]) -> None:
        super().__init__(key, name, **kwargs)

    def _create_entity_description(self) -> SolArkBinarySensorEntityDescription:
        return SolArkBinarySensorEntityDescription.from_kwargs(
            key=self.key,
            name=self.name,
            opts=self.opts,
        )

# ----------------------------
# Binary
# ----------------------------
class BinaryProblemEntry(BinarySensorEntry):
    DEFAULTS = {
        "device_class": BinarySensorDeviceClass.PROBLEM,
    }

class BinaryMetricsEntry(BinarySensorEntry):
    DEFAULTS = {
        "icon": "mdi:information-outline",
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

