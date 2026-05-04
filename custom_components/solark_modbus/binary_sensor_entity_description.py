"""Binary sensor entity descriptions for SolArk."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription

from .base_entry import BaseEntry
from .binary_sensor_class import BinarySensorClass


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
    entry_class: type[BaseEntry]
    name_prefix: str = ""

    @classmethod
    def from_kwargs(
        cls,
        key: str,
        name: str,
        entry_class: type[BaseEntry],
        opts: dict[str, Any],
    ) -> "SolArkBinarySensorEntityDescription":
        """Create a binary sensor entity description from entry options."""

        passthrough = {
            # SolArkBinarySensorEntityDescription
            "sensor_class",
            "description",
            "exclude_from_recorder",
            "should_poll",
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
            "entry_class": entry_class,
            **{k: v for k, v in opts.items()
            if k in passthrough and v is not None},
        }

        unit = opts.get("native_unit")
        if unit is not None:
            base_kwargs["native_unit_of_measurement"] = unit.value

        return cls(**base_kwargs)
