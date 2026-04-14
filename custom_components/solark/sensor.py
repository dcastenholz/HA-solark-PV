from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import EntityDescription, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
from .config_entry import SolArkConfigEntry
from .const import FORMAT_TOU_SENSORS_24HOUR
from .data import SolArkData
from .sensor_class import SensorClass
from .sensor_entity_description import SolArkSensorEntityDescription


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data: SolArkData = entry.runtime_data

    entities = []
    descriptions: list[EntityDescription] = runtime_data.register_map.get_descriptions() + runtime_data.calculated_sensor_map.get_descriptions()

    # Normal sensors
    for entity_description in descriptions:
        if isinstance(entity_description, SolArkSensorEntityDescription):
            sensor_entity_description: SolArkSensorEntityDescription = cast(SolArkSensorEntityDescription, entity_description)
            entity_cls: type[SolArkSensor] = _get_sensor_class(sensor_entity_description.sensor_class)

            if entity_cls:
                sensor = entity_cls(
                    runtime_data,
                    entity_description,
                )
                entities.append(sensor)

    async_add_entities(entities)
    return True


class SolArkSensor(SensorEntity):
    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkSensorEntityDescription,
    ):
        self.runtime_data = runtime_data
        self.entity_description: SolArkSensorEntityDescription = description

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
        return None if self.data is None else self.data.get(self.entity_description.key)

    @property
    def icon(self) -> str | None:
        if (strategy := self.entity_description.dynamic_icon) is not None:
            if (icon := strategy(self.native_value)) is not None:
                return icon

        return self.entity_description.icon

    @property
    def data(self):
        return self.runtime_data.coordinator.data


class SolArkCoordinatorSensor(CoordinatorEntity, SolArkSensor):
    """Sensor reading from Modbus via the coordinator."""

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkSensorEntityDescription,
    ):
        SolArkSensor.__init__(self, runtime_data, description)
        CoordinatorEntity.__init__(self, runtime_data.coordinator)


class SolArkTOU_TimeSensor(SolArkCoordinatorSensor):
    @property
    def native_value(self) -> str | None:
        raw_value = self.data.get(self.entity_description.key) if self.data else None
        if not isinstance(raw_value, int):
            return None  # return None if no value yet

        # Convert HHMM integer to a 12-hour formatted string.
        try:
            value = int(raw_value) # type: ignore
        except (TypeError, ValueError):
            return ""

        hours = value // 100
        minutes = value % 100
        if hours > 23 or minutes > 59:
            return f"Invalid: {value}"

        suffix = ""

        if not FORMAT_TOU_SENSORS_24HOUR:
            suffix += " "
            suffix += "AM" if hours < 12 else "PM"
            hours = hours % 12
            if hours == 0:
                hours = 12

        return f"{hours}:{minutes:02d}{suffix}"


class SolArkDateTimeSensor(SolArkCoordinatorSensor):
    @property
    def native_value(self) -> str | None:
        dt = self.data.get(self.entity_description.key) if self.data else None
        if dt is None:
            return None  # return None if no value yet
        # dt is a datetime object, safe to format now
        return dt.strftime("%Y-%m-%d %H:%M:%S")


SENSOR_CLASS_MAP = {
    SensorClass.NORMAL: SolArkCoordinatorSensor,
    SensorClass.BASE: SolArkSensor,
    SensorClass.DATETIME: SolArkDateTimeSensor,
    SensorClass.TOU_TIME: SolArkTOU_TimeSensor,
}

@staticmethod
def _get_sensor_class(sensor_class: SensorClass) -> type[SolArkSensor] | None:
    return SENSOR_CLASS_MAP.get(sensor_class)
