from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .config_entry import SolArkConfigEntry
from .data import SolArkData
from .register_map_entry import SensorClass
from .sensor_entity_description import SolArkModbusSensorEntityDescription


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data: SolArkData = entry.runtime_data

    entities = []
    descriptions: list[SolArkModbusSensorEntityDescription] = runtime_data.register_map.get_descriptions() + runtime_data.calculated_sensor_map.get_descriptions()

    # Normal Modbus sensors
    for sensor_entity_description in descriptions:
        entity_cls: type[SolArkBaseSensor] = _get_sensor_class(sensor_entity_description.sensor_class)
        sensor = entity_cls(
            runtime_data,
            sensor_entity_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True



class SolArkBaseSensor(SensorEntity):
    """Single diagnostic sensor exposing config values as attributes."""

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkModbusSensorEntityDescription,
    ):
        super().__init__()
        self.runtime_data = runtime_data
        self._attr_device_info = runtime_data.device_info
        self.entity_description = description
        self._attr_name = f"{runtime_data.name} {description.name}"
        self._attr_unique_id = f"{runtime_data.name}_{description.key}"
        self._attr_exclude_from_recorder = description.exclude_from_recorder

class SolArkSensor(CoordinatorEntity, SolArkBaseSensor):
    """Sensor reading from Modbus via the coordinator."""

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkModbusSensorEntityDescription,
    ):
        SolArkBaseSensor.__init__(self, runtime_data, description)
        CoordinatorEntity.__init__(self, runtime_data.coordinator)

    @property
    def native_value(self) -> Any | None:
        data = self.coordinator.data
        return None if data is None else data.get(self.entity_description.key)


class SolArkTOU_TimeSensor(SolArkSensor):
    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data.get(self.entity_description.key) if self.coordinator.data else None
        if not isinstance(data, int):
            return None  # return None if no value yet
        # Convert HHMM integer to a 12-hour formatted string.
        try:
            value = int(data) # type: ignore
        except (TypeError, ValueError):
            return ""

        hours = value // 100
        minutes = value % 100
        if hours > 23 or minutes > 59:
            return "Invalid"

        suffix = "AM" if hours < 12 else "PM"
        hour_12 = hours % 12
        if hour_12 == 0:
            hour_12 = 12

        # TODO - Add option for 24 hour time display
        return f"{hour_12}:{minutes:02d} {suffix}"


class SolArkDateTimeSensor(SolArkSensor):
    @property
    def native_value(self) -> str | None:
        dt = self.coordinator.data.get(self.entity_description.key) if self.coordinator.data else None
        if dt is None:
            return None  # return None if no value yet
        # dt is a datetime object, safe to format now
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def exclude_from_recorder(self) -> bool:
        return True


class SolArkConfigInfoSensor(SolArkBaseSensor):
    """Sensor exposing static config values as attributes."""

    def __init__(
        self,
        runtime_data: SolArkData,
        entity_description: SolArkModbusSensorEntityDescription
    ):
        SolArkBaseSensor.__init__(self, runtime_data, entity_description)

    @property
    def native_value(self) -> Any | None:
        return self.runtime_data.name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:

        return self.runtime_data.config_flow_state.get_config_sensor_data(self.runtime_data.config_entry)

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def exclude_from_recorder(self) -> bool:
        return True

def _get_sensor_class(sensor_class: SensorClass) -> type[SolArkBaseSensor]:
    if sensor_class == SensorClass.NORMAL:
        return SolArkSensor
    if sensor_class == SensorClass.CONFIG:
        return SolArkConfigInfoSensor
    if sensor_class == SensorClass.DATETIME:
        return SolArkDateTimeSensor
    if sensor_class == SensorClass.TOU_TIME:
        return SolArkTOU_TimeSensor
    raise ValueError(f"Unknown SensorClass: {sensor_class}")
