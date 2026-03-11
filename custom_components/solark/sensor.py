from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .hub import SolArkHubManager
from .register_map import SensorClass
from .sensor_entity_description import SolArkModbusSensorEntityDescription


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    hub_manager: SolArkHubManager = SolArkHubManager.get_manager(hass, entry)

    entities = []

    # Normal Modbus sensors
    for sensor_entity_description in hub_manager.hub.register_map.get_descriptions():
        entity_cls: type[SolArkBaseSensor] = get_sensor_class(sensor_entity_description.sensor_class)
        sensor = entity_cls(
            hub_manager,
            sensor_entity_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True



class SolArkBaseSensor(SensorEntity):
    """Single diagnostic sensor exposing config values as attributes."""

    def __init__(
        self,
        hub_manager: SolArkHubManager,
        description: SolArkModbusSensorEntityDescription,
    ):
        self.hub_manager = hub_manager
        self._attr_device_info = hub_manager.device_info
        self.entity_description  = description
        self._attr_name = f"{hub_manager.name} {description.name}"
        self._attr_unique_id = f"{hub_manager.name}_{description.key}"


class SolArkSensor(CoordinatorEntity, SolArkBaseSensor):
    """Sensor reading from Modbus via the coordinator."""

    def __init__(
        self,
        hub_manager: SolArkHubManager,
        description: SolArkModbusSensorEntityDescription,
    ):
        SolArkBaseSensor.__init__(self, hub_manager, description)
        CoordinatorEntity.__init__(self, coordinator=hub_manager.hub)

    @property
    def native_value(self):
        data = self.coordinator.data
        return None if data is None else data.get(self.entity_description.key)


class SolArkConfigInfoSensor(SolArkBaseSensor):
    """Sensor exposing static config values as attributes."""

    def __init__(
        self,
        hub_manager: SolArkHubManager,
        entity_description: SolArkModbusSensorEntityDescription
    ):
        SolArkBaseSensor.__init__(self, hub_manager, entity_description)

    @property
    def native_value(self):
        return "loaded"

    @property
    def extra_state_attributes(self):
        return {
            "name": self.hub_manager.entry.data.get("name"),
            "host": self.hub_manager.entry.data.get("host"),
            "scan_interval": self.hub_manager.entry.data.get("scan_interval"),
        }

def get_sensor_class(sensor_class: SensorClass) -> type[SolArkBaseSensor]:
    if sensor_class == SensorClass.NORMAL:
        return SolArkSensor
    if sensor_class == SensorClass.CONFIG:
        return SolArkConfigInfoSensor