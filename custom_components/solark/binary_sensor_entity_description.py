from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.binary_sensor import BinarySensorEntityDescription

from .binary_sensor_class import BinarySensorClass
from .register_value_types import SensorValue

if TYPE_CHECKING:
    from .binary_sensor import SolArkBinarySensor
    from .data import SolArkData

# ----------------------------------
# Sensor Entity Description
# ----------------------------------
@dataclass(kw_only=True, frozen=True)
class SolArkBinarySensorEntityDescription(BinarySensorEntityDescription):
    """SolArk-specific sensor description."""
    sensor_class: BinarySensorClass = BinarySensorClass.BINARY
    # TODO - Is this needed at all???
    description: str | None = None
    # TODO - Is this needed at all???
    exclude_from_recorder: bool = False
    # should_poll is ignored for coordinator sensors.
    should_poll: bool = True
    dynamic_icon: Callable[["SensorValue"], str] | None = None
    on_sensor_creating: Callable[["SolArkBinarySensor", "SolArkData"], None] | None = None
    name_prefix: str = ""

    @classmethod
    def from_kwargs(
        cls,
        key: str,
        name: str,
        opts: dict[str, Any],
    ) -> "SolArkBinarySensorEntityDescription":

        passthrough = {
            # SolArkBinarySensorEntityDescription
            "sensor_class",
            "description",
            "exclude_from_recorder",
            "should_poll",
            "dynamic_icon",
            "on_sensor_creating",
            "name_prefix",

            # BinarySensorEntityDescription
            "device_class",

            # EntityDescription
            "icon",
            "entity_registry_enabled_default",
            "entity_category",
        }

        base_kwargs = {
            "key": key,
            "name": name,
            **{k: v for k, v in opts.items()
            if k in passthrough and v is not None},
        }

        unit = opts.get("native_unit")
        if unit is not None:
            base_kwargs["native_unit_of_measurement"] = unit.value

        return cls(**base_kwargs)
