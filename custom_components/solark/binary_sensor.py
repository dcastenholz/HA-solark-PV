
from typing import Any

from .base_map_entry import BaseEntry
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .binary_sensor_class import BinarySensorClass
from .binary_sensor_entity_description import SolArkBinarySensorEntityDescription
from .data import SolArkData


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    runtime_data: SolArkData = entry.runtime_data

    entities = []

    # Only binary sensors
    for entity_description in runtime_data.descriptions_of_type(SolArkBinarySensorEntityDescription):
        entity_cls: type[SolArkBinarySensor] = _get_sensor_class(entity_description.sensor_class)
        entities.append(entity_cls(runtime_data, entity_description))

    async_add_entities(entities)
    return True


class SolArkBinarySensor(BinarySensorEntity):
    """Base binary sensor entity.
    All binary sensor classes used in a BinarySensorMap must inherit from this."""

    def __init__(self, runtime_data: SolArkData, description: SolArkBinarySensorEntityDescription):
        self.runtime_data = runtime_data
        self.entity_description: SolArkBinarySensorEntityDescription = description

        # Setting the entity_description on a BinarySensorEntity handles most properties,
        # but some need to be set specifically or modified
        self._attr_name = f"{runtime_data.name} {description.name_prefix}{description.name}"
        self._attr_unique_id = f"{runtime_data.name}_{description.key}"
        self._attr_device_info = runtime_data.device_info
        self._attr_exclude_from_recorder = description.exclude_from_recorder
        self._attr_should_poll = description.should_poll

        self._attr_device_class = description.device_class

    @property
    def entry_class(self) -> type[BaseEntry]:
        return self.entity_description.entry_class

    @property
    def icon(self) -> str | None:
        '''Gets the icon to display.

        Uses 'or' so empty string in dynamic dictionary will not be returned.'''
        return self.entry_class.dynamic_icon(self.data_value) or self.entity_description.icon

    @property
    def data_value(self):
        return self.data.get(self.entity_description.key)

    @property
    def data(self):
        return self.runtime_data.coordinator.data

    @property
    def is_on(self) -> bool | None:

        if self.data is None:
            return None

        value = self.data_value

        if value is None:
            return None

        # fallback: assume raw boolean/int
        return bool(value)


BINARYSENSOR_CLASS_MAP = {
    BinarySensorClass.BINARY: SolArkBinarySensor,
}

def _get_sensor_class(sensor_class: BinarySensorClass) -> type[SolArkBinarySensor]:
    try:
        return BINARYSENSOR_CLASS_MAP[sensor_class]
    except KeyError as err:
        raise ValueError(
            f"Unhandled BinarySensorClass: {sensor_class}. "
            f"BINARYSENSOR_CLASS_MAP is incomplete."
        ) from err
