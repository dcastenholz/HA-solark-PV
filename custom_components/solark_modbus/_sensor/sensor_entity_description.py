"""Sensor entity descriptions for SolArk."""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)

from .._sensor.sensor_class import SensorClass
from ..entry_map.base_entry import BaseEntry


# ----------------------------------
# Native Unit of Measurement Enum
# ----------------------------------
class NativeUnit(Enum):
    """Native units used by SolArk sensors."""

    KWH = UnitOfEnergy.KILO_WATT_HOUR
    WATT = UnitOfPower.WATT
    V = UnitOfElectricPotential.VOLT
    A = UnitOfElectricCurrent.AMPERE
    AH = "Ah"
    CELSIUS = UnitOfTemperature.CELSIUS
    PERCENT = PERCENTAGE
    HZ = UnitOfFrequency.HERTZ


# ----------------------------------
# Sensor Entity Description
# ----------------------------------
@dataclass(kw_only=True, frozen=True)
class SolArkSensorEntityDescription(SensorEntityDescription):
    """SolArk-specific sensor description."""
    sensor_class: SensorClass = SensorClass.COORDINATOR
    # TODO - Is this needed at all???
    # description: str | None = None
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
    ) -> "SolArkSensorEntityDescription":
        """Create a sensor entity description from entry options."""

        passthrough = {
            # SolArkSensorEntityDescription
            "sensor_class",
            "description",
            "exclude_from_recorder",
            "should_poll",
            "name_prefix",

            # SensorEntityDescription
            "device_class",
            "state_class",

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

        # -----------------------------
        # Derive suggested display precision from scale
        # -----------------------------
        scale = opts.get("scale")

        # Inject an appriopriate display precision based on the scale.
        # TODO - Convert scale to be a power of 10.  This will become trivial.
        if isinstance(scale, (int, float)) and scale not in (0, 1):
            try:
                precision = max(0, int(round(-math.log10(scale))))
                base_kwargs["suggested_display_precision"] = precision
            except (ValueError, OverflowError):
                pass  # ignore invalid scale

        # -----------------------------
        # Unit handling
        # -----------------------------
        unit = opts.get("native_unit")
        if unit is not None:
            base_kwargs["native_unit_of_measurement"] = unit.value

        return cls(**base_kwargs)
