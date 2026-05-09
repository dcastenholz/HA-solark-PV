"""Binary sensor map entries for SolArk entities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Self, Tuple, TypedDict, Unpack

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

    # ENTITY_DESCRIPTION_CLS = SolArkBinarySensorEntityDescription

    # # Dynamic maps let entry classes override an icon for specific values.
    # DynamicIcon: dict[bool, str] | None = None

    def __init__(self, key: str, name: str, **kwargs: Unpack[BinarySensorEntryOptional]) -> None:
        """Initialize the binary sensor entry."""
        super().__init__(key, name, **kwargs)

    # @classmethod
    # def _get_dynamic_entry(
    #     cls, lookup_map_key: bool
    # ) -> str | None:
    #     ''' Return the dictionary entry for the given key if DynamicIcon is configured. '''
    #     d = cls.DynamicIcon
    #     if not d:
    #         return None

    #     if lookup_map_key is None:
    #         raise ValueError(
    #             f"Value {lookup_map_key!r} is None. DynamicIcon keys: {list(d.keys())}"
    #         ) from None

    #     try:
    #         return d[lookup_map_key]
    #     except KeyError:
    #         raise ValueError(
    #             f"Value {lookup_map_key!r} not valid for DynamicIcon keys: {list(d.keys())}"
    #         ) from None

    # @classmethod
    # def dynamic_icon(cls, lookup_map_key: bool) -> str | None:
    #     """Return a dynamic icon for the value if one is configured."""
    #     entry = cls._get_dynamic_entry(lookup_map_key)
    #     return entry[0] if entry else None


class RegisterBoolEntry(BaseRegisterEntry[SolArkBinarySensorEntityDescription, bool], BinarySensorMixin):
    """Class for all modbus register backed boolean sensors."""

    ENTITY_DESCRIPTION_CLS = SolArkBinarySensorEntityDescription

    # def __init__(self, address: int, key: str, name: str, **kwargs) -> None:
    #     """Initialize a numeric register entry."""
    #     super().__init__(address, key, name, **kwargs)

    def _create_entity_description(self, entry_class: type[BaseBinarySensorEntry]) -> SolArkBinarySensorEntityDescription:
        """Create the Home Assistant entity description for this entry."""
        return SolArkBinarySensorEntityDescription.from_kwargs(
            key=self.key,
            name=self.name,
            entry_class=entry_class,
            opts=self.opts,
        )

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


# ----------------------------
# Time of Use Charge Enabled
# ----------------------------
class TimeOfUse_ChargeEnabledEntry(RegisterBoolEntry):
    """Register entry for time-of-use charge enabled state."""

    DEFAULTS = {
        # "state_class": None,
        "sensor_class": BinarySensorClass.ENABLED_DISABLED,
    }

    DynamicValueDict = {
        True: ("Enabled", "mdi:checkbox-marked-circle-outline"),
        False: ("Disabled", "mdi:checkbox-blank-circle-outline"),
    }
