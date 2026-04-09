from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .config_entry import SolArkConfigEntry
from .data import SolArkData
from .sensor_class import SensorClass
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

    # description: SolArkModbusSensorEntityDescription

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkModbusSensorEntityDescription,
    ):
        super().__init__()
        # self.description = description
        self.runtime_data = runtime_data
        self.entity_description = description

        self._attr_device_info = runtime_data.device_info
        self._attr_name = f"{runtime_data.name} {description.name}"
        self._attr_unique_id = f"{runtime_data.name}_{description.key}"
        self._attr_exclude_from_recorder = description.exclude_from_recorder

        if description.should_poll:
            self.should_poll = description.should_poll

        if description.post_process_sensor:
            description.post_process_sensor(self, self.runtime_data)

    @property
    def native_value(self) -> Any | None:
        data = self.runtime_data.coordinator.data
        return None if data is None else data.get(self.entity_description.key)

class SolArkSensor(CoordinatorEntity, SolArkBaseSensor):
    """Sensor reading from Modbus via the coordinator."""

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkModbusSensorEntityDescription,
    ):
        SolArkBaseSensor.__init__(self, runtime_data, description)
        CoordinatorEntity.__init__(self, runtime_data.coordinator)


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
            return f"Invalid: {value}"

        suffix = ""

        # TODO - Add option for 24 hour time display
        FORMAT_24HOUR: bool = False

        if not FORMAT_24HOUR:
            suffix += " "
            suffix += "AM" if hours < 12 else "PM"
            hours = hours % 12
            if hours == 0:
                hours = 12

        return f"{hours}:{minutes:02d}{suffix}"


class SolArkDateTimeSensor(SolArkSensor):
    @property
    def native_value(self) -> str | None:
        dt = self.coordinator.data.get(self.entity_description.key) if self.coordinator.data else None
        if dt is None:
            return None  # return None if no value yet
        # dt is a datetime object, safe to format now
        return dt.strftime("%Y-%m-%d %H:%M:%S")


SENSOR_CLASS_MAP = {
    SensorClass.NORMAL: SolArkSensor,
    SensorClass.BASE: SolArkBaseSensor,
    SensorClass.DATETIME: SolArkDateTimeSensor,
    SensorClass.TOU_TIME: SolArkTOU_TimeSensor,
}

@staticmethod
def _get_sensor_class(sensor_class: SensorClass) -> type[SolArkBaseSensor]:
    return SENSOR_CLASS_MAP[sensor_class]