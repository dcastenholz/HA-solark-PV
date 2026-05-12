"""Binary sensor map entries for SolArk entities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Self, TypedDict, Unpack

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

from .._binary_sensor.binary_sensor_class import BinarySensorClass
from .._binary_sensor.binary_sensor_dynamic_value_set import BinarySensorDynamicValueSet
from .._binary_sensor.binary_sensor_entity_description import SolArkBinarySensorEntityDescription
from .._binary_sensor.binary_sensor_mixin import BinarySensorMixin
from ..coordinator.coordinator_metrics import CoordinatorMetrics
from .base_entry import BaseEntry, BaseRegisterEntry

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
    binary_sensor_state_values: BinarySensorDynamicValueSet

    # TODO - Is this unused???
    set_sensor_value: Callable[[Any, "SolArkData"], None]


class BaseBinarySensorEntry(BaseEntry[SolArkBinarySensorEntityDescription, bool], BinarySensorMixin):
    """Base class for all binary sensor map entries."""

    DEFAULTS = {
        "sensor_class": BinarySensorClass.BINARY,
    }

    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorEntryOptional]) -> None:
        """Initialize the binary sensor entry."""
        super().__init__(key, name, **kwargs)


class RegisterBoolEntry(BaseRegisterEntry[SolArkBinarySensorEntityDescription, bool], BinarySensorMixin):
    """Class for all modbus register backed boolean sensors."""

    @property
    def register_length(self) -> int:
        """The register count."""
        return 1


# ----------------------------
# Binary
# ----------------------------
class BinaryProblemEntry(BaseBinarySensorEntry):
    """Binary sensor entry that reports a problem state."""

    DEFAULTS = {
        "device_class": BinarySensorDeviceClass.PROBLEM,
    }

class MetricsSuccessFailureEntry(BaseBinarySensorEntry):
    """Binary sensor entry backed by coordinator metric success values."""

    DEFAULTS = {
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "name_prefix": "Metric: ",
        "sensor_class": BinarySensorClass.SUCCESS_FAILURE,
    }

    DynamicIcon: dict[bool, str] = {
        True: "mdi:check-circle",
        False: "mdi:alert-circle",
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


# ----------------------------
# Time of Use Charge Enabled
# ----------------------------
class TimeOfUse_ChargeEnabledEntry(RegisterBoolEntry):
    """Register entry for time-of-use charge enabled state."""

    DynamicIcon = {
        True: "mdi:checkbox-marked-circle-outline",
        False: "mdi:checkbox-blank-circle-outline",
    }

    DEFAULTS = {
        # "state_class": None,
        "sensor_class": BinarySensorClass.ENABLED_DISABLED,
    }
