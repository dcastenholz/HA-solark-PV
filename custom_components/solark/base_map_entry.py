import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, TypedDict, TypeVar

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory
from typing_extensions import Unpack

from .register_value_types import RegisterValue
from .sensor_class import SensorClass
from .sensor_entity_description import (
    NativeUnit,
    SolArkModbusSensorEntityDescription,
)

if TYPE_CHECKING:
    from .data import SolArkData
    from .sensor import SolArkBaseSensor

_LOGGER = logging.getLogger(__name__)


TEntry = TypeVar("TEntry", bound="BaseMapEntry")

class BaseMapEntryOptional(TypedDict, total=False):
    native_unit: NativeUnit
    device_class: SensorDeviceClass
    state_class: Optional[SensorStateClass]
    icon: str
    entity_registry_enabled_default: bool
    entity_category: EntityCategory
    description: str
    suggested_display_precision: int
    sensor_class: SensorClass
    exclude_from_recorder: bool
    should_poll: bool
    extra_state_attributes: dict[str, Any]
    post_process: Callable[["BaseMapEntry[Any]", "SolArkData"], None]
    post_process_sensor: Callable[["SolArkBaseSensor", "SolArkData"], None]
    dynamic_icon: Callable[[RegisterValue], str | None]

    scale: float
    offset: int

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
    scale: float
    offset: int

    def __init__(self, key: str, name: str, **kwargs: Unpack[BaseMapEntryOptional]) -> None:
        # -----------------------------
        # Normalize kwargs once
        # -----------------------------
        opts = {
            "entity_registry_enabled_default": False,
            "sensor_class": SensorClass.NORMAL,
            "exclude_from_recorder": False,
            "scale": 1.0,
            "offset": 0,
            **kwargs,
        }

        # -----------------------------
        # entity description build
        # -----------------------------
        self._entity_description = SolArkModbusSensorEntityDescription(
            key=key,
            name=name,
            native_unit=opts.get("native_unit"),
            device_class=opts.get("device_class"),
            state_class=opts.get("state_class"),
            icon=opts.get("icon"),
            entity_registry_enabled_default=opts["entity_registry_enabled_default"],
            entity_category=opts.get("entity_category"),
            description=opts.get("description"),
            suggested_display_precision=opts.get("suggested_display_precision"),
            sensor_class=opts["sensor_class"],
            exclude_from_recorder=opts["exclude_from_recorder"],
            should_poll=opts.get("should_poll"),
            extra_state_attributes=opts.get("extra_state_attributes") or {},
            post_process_sensor=opts.get("post_process_sensor"),
            dynamic_icon=opts.get("dynamic_icon"),
        )

        # -----------------------------
        # store fields
        # -----------------------------
        self.post_process = opts.get("post_process")
        self.scale = opts["scale"]
        self.offset = opts["offset"]

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
