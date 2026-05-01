from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .base_map_entry import BaseEntry
from .const import FORMAT_TOU_SENSORS_24HOUR
from .data import SolArkData
from .register_value_types import SensorValue
from .sensor_class import SensorClass
from .sensor_entity_description import SolArkSensorEntityDescription


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    runtime_data: SolArkData = entry.runtime_data

    entities = []

    # Normal sensors
    for entity_description in runtime_data.descriptions_of_type(SolArkSensorEntityDescription):
        entity_cls: type[SolArkSensorEntity] = _get_sensor_class(entity_description.sensor_class)
        entities.append(entity_cls(runtime_data, entity_description))

    async_add_entities(entities)
    return True


class SolArkSensorEntity(SensorEntity, ABC):
    """Base sensor entity: metadata + shared setup only.
    All sensor classes used in a SensorMap must inherit from this."""

    def __init__(self, runtime_data: SolArkData, description: SolArkSensorEntityDescription):
        self.runtime_data = runtime_data
        self.entity_description: SolArkSensorEntityDescription = description

        # Setting the entity_description on a SensorEntity handles most properties,
        # but some need to be set specifically or modified
        self._attr_name = f"{runtime_data.name} {description.name_prefix}{description.name}"
        self._attr_unique_id = f"{runtime_data.name}_{description.key}"
        self._attr_device_info = runtime_data.device_info
        self._attr_exclude_from_recorder = description.exclude_from_recorder
        self._attr_should_poll = description.should_poll

        if description.on_sensor_creating:
            description.on_sensor_creating(self, runtime_data)

    @property
    def entry_class(self) -> type[BaseEntry]:
        return self.entity_description.entry_class

    @property
    def icon(self) -> str | None:
        '''Gets the icon to display.

        Uses 'or' so empty string in dynamic dictionary will not be returned.'''
        return self.entry_class.dynamic_icon(self.data_value) or self.entity_description.icon

    @property
    def native_value(self) -> Any | None:
        value = self.entry_class.dynamic_native_value(self.data_value)
        if value is not None:
            return value

        return self.data_value

    @property
    @abstractmethod
    def data_value(self):
        pass


class SolArkCoordinatorEntity(CoordinatorEntity, ABC):
    """Adds coordinator data access only."""

    @property
    def data(self):
        return self.coordinator.data

    @property
    def data_value(self):
        data = self.data
        if data is None:
            return None
        return data.get(self.entity_description.key)


class SolArkCoordinatorSensor(SolArkCoordinatorEntity, SolArkSensorEntity):
    """Sensors backed by coordinator data."""

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkSensorEntityDescription,
    ):
        SolArkSensorEntity.__init__(self, runtime_data, description)
        SolArkCoordinatorEntity.__init__(self, runtime_data.coordinator)


class SolArkStaticValueSensor(SolArkSensorEntity):
    """Sensors that do not depend on coordinator."""

    # Instances of this class must set a static native_value
    _attr_native_value: SensorValue = None
    @property
    def data_value(self):
        return None

    @property
    def native_value(self) -> SensorValue:
        if self._attr_native_value is None:
            raise RuntimeError(f"The sensor '{self._attr_name}' is a {type(self).__name__}, so '_attr_native_value' must be set.")
        return self._attr_native_value


class SolArkMetricsSensor(SolArkCoordinatorSensor):
    '''Sensor to handle coordinator metrics'''


class SolArkTOU_TimeSensor(SolArkCoordinatorSensor):
    @property
    def native_value(self) -> str | None:
        raw_value = self.data.get(self.entity_description.key) if self.data else None
        if not isinstance(raw_value, int):
            return None  # return None if no value yet

        # Convert HHMM integer to a 24-hour formatted string.
        hours = raw_value // 100
        minutes = raw_value % 100
        suffix = ""
        if hours > 23 or minutes > 59:
            return f"Invalid: {raw_value}"


        if not FORMAT_TOU_SENSORS_24HOUR:
            # Convert HHMM integer to a 12-hour formatted string.
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
    SensorClass.STATIC_VALUE: SolArkStaticValueSensor,
    SensorClass.COORDINATOR: SolArkCoordinatorSensor,
    SensorClass.METRICS: SolArkMetricsSensor,
    SensorClass.TOU_TIME: SolArkTOU_TimeSensor,
    SensorClass.DATETIME: SolArkDateTimeSensor,
}

def _get_sensor_class(sensor_class: SensorClass) -> type[SolArkSensorEntity]:
    try:
        return SENSOR_CLASS_MAP[sensor_class]
    except KeyError as err:
        raise ValueError(
            f"Unhandled SensorClass: {sensor_class}. "
            f"SENSOR_CLASS_MAP is incomplete."
        ) from err
