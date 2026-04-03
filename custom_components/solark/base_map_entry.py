import logging
from typing import TYPE_CHECKING, Callable, Generic, Optional, Self, TypeVar

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

from .register_value_types import RegisterValue
from .sensor_entity_description import (
    SensorClass,
    SolArkModbusSensorEntityDescription,
    UnitOfMeasure,
)

if TYPE_CHECKING:
    from .data import SolArkData

_LOGGER = logging.getLogger(__name__)


TEntry = TypeVar("TEntry", bound="BaseMapEntry")

class BaseMapEntry(Generic[TEntry]):
    """
    Base class for all SolArk map entries.

    Provides:
    - Entity metadata wrapper
    - Scaling and offset support
    - Post-processing hook
    - Numeric conversion helpers
    """

    register_value: RegisterValue = None

    def __init__(
        self,
        key: str,
        name: str | None = None,
        unit_of_measurement: UnitOfMeasure | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
        entity_registry_enabled_default: bool = False,
        entity_category: EntityCategory | None = None,
        description: str | None = None,
        sensor_class: SensorClass = SensorClass.NORMAL,
        exclude_from_recorder: bool = False,
        post_process_method: Optional[
            Callable[["SolArkData", Self], None]
        ] = None,
        scale: float = 1.0,
        offset: int = 0,
    ) -> None:
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
        )

        self.scale = scale
        self.offset = offset
        self.post_process_method = post_process_method

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
    def post_process(self, runtime_data: "SolArkData") -> None:
        """
        Execute post-processing callback if defined.
        """
        if not self.post_process_method:
            return

        try:
            self.post_process_method(runtime_data, self)
        except Exception:  # pylint: disable=broad-exception-caught
            _LOGGER.exception(
                "Error post-processing entry %s",
                self._entity_description.key,
            )
