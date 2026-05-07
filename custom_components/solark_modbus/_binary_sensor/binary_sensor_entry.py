"""Binary sensor map entries for SolArk entities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Self, Tuple, TypedDict, Unpack

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

from ..coordinator.coordinator_metrics import CoordinatorMetrics
from ..entry_map.base_entry import BaseEntry
from .binary_sensor_class import BinarySensorClass
from .binary_sensor_entity_description import SolArkBinarySensorEntityDescription

if TYPE_CHECKING:
    from ..data import SolArkData


_LOGGER = logging.getLogger(__name__)


class BinarySensorEntryOptional(TypedDict, total=False):
    """Optional keyword arguments for binary sensor map entries."""

    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    exclude_from_recorder: bool
    should_poll: bool

    device_class: BinarySensorDeviceClass
    sensor_class: BinarySensorClass

    # TODO - Is this unused???
    set_sensor_value: Callable[[Any, "SolArkData"], None]


class BinarySensorEntry(BaseEntry[SolArkBinarySensorEntityDescription, bool]):
    """Base class for all binary sensor map entries."""

    DEFAULTS = {
        "sensor_class": BinarySensorClass.BINARY,
    }

    # Dynamic maps let entry classes override an icon for specific values.
    DynamicValueDict: dict[bool, Tuple[Any, str]] | None = None

    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorEntryOptional]) -> None:
        """Initialize the binary sensor entry."""
        super().__init__(key, name, **kwargs)

    def _create_entity_description(self, entry_class: type[BaseEntry]) -> SolArkBinarySensorEntityDescription:
        """Create the Home Assistant entity description for this entry."""
        return SolArkBinarySensorEntityDescription.from_kwargs(
            key=self.key,
            name=self.name,
            entry_class=entry_class,
            opts=self.opts,
        )


# ----------------------------
# Binary
# ----------------------------
class BinaryProblemEntry(BinarySensorEntry):
    """Binary sensor entry that reports a problem state."""

    DEFAULTS = {
        "device_class": BinarySensorDeviceClass.PROBLEM,
    }

class MetricsSuccessEntry(BinarySensorEntry):
    """Binary sensor entry backed by coordinator metric success values."""

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "name_prefix": "Metric: ",
    }

    DynamicValueDict: dict[bool, Tuple[Any, str]] = {
        True: (None, "mdi:check-circle"),
        False: (None, "mdi:alert-circle"),
    }

    def __init__(
        self,
        key: str,
        name: str,
        metric: Callable[[CoordinatorMetrics], Any],
    ) -> None:
        """Initialize the metrics success entry."""
        self.metric = metric

        super().__init__(
            key,
            name,
        )

    def calc_sensor_value(self: Self, runtime_data: "SolArkData") -> None:
        """Calculate the sensor value from coordinator metrics."""
        self._sensor_value = self.metric(runtime_data.coordinator_metrics)
