import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Generic, TypedDict, TypeVar

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory
from typing_extensions import Unpack

from .register_value_types import RegisterValue
from .sensor_class import SensorClass
from .sensor_entity_description import (
    SolArkModbusSensorEntityDescription,
    UnitOfMeasure,
)

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkBaseSensor

_LOGGER = logging.getLogger(__name__)


TEntry = TypeVar("TEntry", bound="BaseMapEntry")

class BaseMapEntryRequired(TypedDict):
    key: str
    name: str


class BaseMapEntryOptional(TypedDict, total=False):
    unit_of_measurement: UnitOfMeasure
    device_class: SensorDeviceClass
    state_class: SensorStateClass
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    sensor_class: SensorClass
    exclude_from_recorder: bool
    should_poll: bool
    extra_state_attributes: dict[str, Any]
    post_process: Callable[["BaseMapEntry[Any]", "SolArkData"], None]
    post_process_sensor: Callable[["SolArkBaseSensor", "SolArkData"], None]
    scale: float
    offset: int

class BaseMapEntryKwargs(BaseMapEntryRequired,BaseMapEntryOptional):
    pass

class BaseMapEntry(Generic[TEntry], ABC):
    """
    Base class for all SolArk map entries.

    Provides:
    - Entity metadata wrapper
    - Scaling and offset support
    - Post-processing hook
    - Numeric conversion helpers
    """
    register_value: RegisterValue = None

    state_class: SensorStateClass | None
    post_process: Callable[["BaseMapEntry[Any]", "SolArkData"], None] | None
    post_process_sensor: Callable[["SolArkBaseSensor", "SolArkData"], None] | None
    scale: float
    offset: int

    def __init__(self, **kwargs: Unpack[BaseMapEntryKwargs]) -> None:
        # -----------------------------
        # unpack once (HERE)
        # -----------------------------
        key = kwargs["key"]
        name = kwargs["name"]

        # if not key:
        #     raise ValueError(f"{self.__class__.__name__} must define 'key'")

        # if not name:
        #     raise ValueError(f"{self.__class__.__name__} must define 'name'")

        unit_of_measurement = kwargs.get("unit_of_measurement")
        device_class = kwargs.get("device_class")
        state_class = kwargs.get("state_class")
        icon = kwargs.get("icon")
        entity_registry_enabled_default = kwargs.get("entity_registry_enabled_default", False)
        entity_category = kwargs.get("entity_category")
        description = kwargs.get("description")
        sensor_class = kwargs.get("sensor_class", SensorClass.NORMAL)
        exclude_from_recorder = kwargs.get("exclude_from_recorder", False)
        should_poll = kwargs.get("should_poll")
        extra_state_attributes = kwargs.get("extra_state_attributes") or {}
        post_process = kwargs.get("post_process")
        post_process_sensor = kwargs.get("post_process_sensor")
        scale = kwargs.get("scale", 1.0)
        offset = kwargs.get("offset", 0)

        # -----------------------------
        # entity description build
        # -----------------------------
        self._entity_description = SolArkModbusSensorEntityDescription(
            key=key,
            name=name,
            native_unit_of_measurement=(
                unit_of_measurement.value if unit_of_measurement else None
            ),
            unit_of_measurement_enum=unit_of_measurement,
            device_class=device_class,
            state_class=state_class,
            icon=icon,
            entity_registry_enabled_default=entity_registry_enabled_default,
            entity_category=entity_category,
            description=description,
            sensor_class=sensor_class,
            exclude_from_recorder=exclude_from_recorder,
            should_poll=should_poll,
            extra_state_attributes=extra_state_attributes,
            post_process_sensor=post_process_sensor,
        )

        # -----------------------------
        # store fields
        # -----------------------------
        self.post_process = post_process
        self.post_process_sensor = post_process_sensor
        self.scale = scale
        self.offset = offset

        self.processed_value: int | None = None

        self._validate()

    # -----------------------------
    # Validation hook
    # -----------------------------
    def _validate(self) -> None:
        """
        Base validation for all entries.

        Subclasses may extend this.
        """
        return

    # -----------------------------
    # Entity access
    # -----------------------------
    @property
    def entity_description(self) -> SolArkModbusSensorEntityDescription:
        return self._entity_description

    # -----------------------------
    # Post processing
    # -----------------------------
    def do_post_process(self, runtime_data: "SolArkData") -> None:
        """ Execute post-processing method. """
        if self.post_process:
            try:
                self.post_process(self, runtime_data)
            except Exception:  # pylint: disable=broad-exception-caught
                _LOGGER.exception(
                    "Error post-processing entry %s",
                    self._entity_description.key,
                )
