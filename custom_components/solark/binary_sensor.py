from typing import cast

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, EntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .binary_sensor_class import BinarySensorClass
from .binary_sensor_entity_description import SolArkBinarySensorEntityDescription

# This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
from .config_entry import SolArkConfigEntry
from .data import SolArkData


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data: SolArkData = entry.runtime_data

    entities = []
    descriptions: list[EntityDescription] = runtime_data.register_map.get_descriptions() + runtime_data.calculated_sensor_map.get_descriptions()

    # Only binary sensors
    for entity_description in descriptions:
        if isinstance(entity_description, SolArkBinarySensorEntityDescription):
            binary_sensor_entity_description: SolArkBinarySensorEntityDescription = cast(SolArkBinarySensorEntityDescription, entity_description)
            entity_cls: type[SolArkBinarySensor] = _get_sensor_class(binary_sensor_entity_description.sensor_class)

            if entity_cls:
                sensor = entity_cls(
                    runtime_data,
                    entity_description,
                )
                entities.append(sensor)

    async_add_entities(entities)
    return True


class SolArkBinarySensor(BinarySensorEntity):
    """Standard SolArk binary sensor."""
    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkBinarySensorEntityDescription,
    ):
        self.runtime_data = runtime_data
        self.entity_description: SolArkBinarySensorEntityDescription = description

        self._attr_device_info = runtime_data.device_info
        self._attr_name = f"{runtime_data.name} {description.name}"
        self._attr_unique_id = f"{runtime_data.name}_{description.key}"
        self._attr_exclude_from_recorder = description.exclude_from_recorder

        if description.should_poll:
            self.should_poll = description.should_poll

        if description.post_process_sensor:
            description.post_process_sensor(self, self.runtime_data)

        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def data(self):
        return self.runtime_data.coordinator.data

    @property
    def is_on(self) -> bool | None:

        if self.data is None:
            return None

        value = self.data.get(self.entity_description.key)

        if value is None:
            return None

        # allow flexible mapping patterns
        mapper = getattr(self.entity_description, "value_map", None)
        if mapper:
            return bool(mapper(value))

        # fallback: assume raw boolean/int
        return bool(value)

    # @property
    # def device_class(self) -> BinarySensorDeviceClass | None:
    #     return BinarySensorDeviceClass.PROBLEM



BINARYSENSOR_CLASS_MAP = {
    BinarySensorClass.BINARY: SolArkBinarySensor,
}

@staticmethod
def _get_sensor_class(sensor_class: BinarySensorClass) -> type[SolArkBinarySensor] | None:
    return BINARYSENSOR_CLASS_MAP.get(sensor_class)