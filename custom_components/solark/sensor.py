from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
from .config_entry import SolArkConfigEntry
from .const import FORMAT_TOU_SENSORS_24HOUR
from .data import SolArkData
from .device_info import SolArkDeviceInfo
from .register_value_types import SensorValue
from .sensor_class import SensorClass
from .sensor_entity_description import SolArkSensorEntityDescription


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    entry = SolArkConfigEntry(hass, entry)

    runtime_data: SolArkData = entry.runtime_data

    entities = []

    # Normal sensors
    for entity_description in runtime_data.descriptions_of_type(SolArkSensorEntityDescription):
        entity_cls: type[SolArkSensorEntity] = _get_sensor_class(entity_description.sensor_class)
        entities.append(entity_cls(runtime_data, entity_description))

    async_add_entities(entities)
    return True


class SolArkSensorEntity(SensorEntity):
    """Base sensor entity: metadata + shared setup only.
    All sensor classes used in a SensorMap must inherit from this."""

    def __init__(self, runtime_data: SolArkData, description: SolArkSensorEntityDescription):
        if description.on_sensor_creating:
            description.on_sensor_creating(self, runtime_data)

        self.runtime_data = runtime_data
        self.entity_description: SolArkSensorEntityDescription = description

        # Setting the entity_description on a SensorEntity handles most properties,
        # but some need to be set specifically or modified
        self._attr_name = f"{runtime_data.name} {description.name}"
        self._attr_unique_id = f"{runtime_data.name}_{description.key}"
        self._attr_device_info = runtime_data.device_info
        self._attr_exclude_from_recorder = description.exclude_from_recorder
        self._attr_should_poll = description.should_poll

    @property
    def icon(self) -> str | None:
        if (strategy := self.entity_description.dynamic_icon) is not None:
            if (icon := strategy(self.native_value)) is not None:
                return icon

        return self.entity_description.icon

    @property
    def native_value(self) -> Any | None:
        """Default: no data source."""
        return None

class SolArkCoordinatorEntity(CoordinatorEntity):
    """Adds coordinator data access only."""

    @property
    def data(self):
        return self.coordinator.data

class SolArkStaticValueSensor(SolArkSensorEntity):
    """Sensors that do not depend on coordinator."""

    # Instances of this class must set a static native_value
    _attr_native_value: SensorValue = None

    @property
    def native_value(self) -> SensorValue:
        if self._attr_native_value is None:
            raise RuntimeError(f"The sensor '{self._attr_name}' is a {type(self).__name__}, so '_attr_native_value' must be set.")
        return self._attr_native_value


class SolArkCoordinatorSensor(SolArkCoordinatorEntity, SolArkSensorEntity):
    """Sensors backed by coordinator data."""

    def __init__(
        self,
        runtime_data: SolArkData,
        description: SolArkSensorEntityDescription,
    ):
        SolArkSensorEntity.__init__(self, runtime_data, description)
        SolArkCoordinatorEntity.__init__(self, runtime_data.coordinator)

    @property
    def native_value(self):
        data = self.data
        if data is None:
            return None
        return data.get(self.entity_description.key)

class SolArkSerialNumberSensor(SolArkCoordinatorSensor):
    """Sensor for reading and processing the Serial Number."""

    old_serial_number: str | None = None

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        serial_number = self.native_value

        if serial_number and serial_number != self.old_serial_number:
            # Update device info
            SolArkDeviceInfo.set_serial_number(self.runtime_data)

            # Store the serial number for comparison later.
            # If it changes, the new one will be written.
            self.old_serial_number = serial_number

        # Write updated state to HA
        self.async_write_ha_state()


# TODO - Add Firmware class???


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
    SensorClass.NORMAL: SolArkCoordinatorSensor,
    SensorClass.DATETIME: SolArkDateTimeSensor,
    SensorClass.TOU_TIME: SolArkTOU_TimeSensor,
    SensorClass.SN: SolArkSerialNumberSensor,
}

def _get_sensor_class(sensor_class: SensorClass) -> type[SolArkSensorEntity]:
    try:
        return SENSOR_CLASS_MAP[sensor_class]
    except KeyError as err:
        raise ValueError(
            f"Unhandled SensorClass: {sensor_class}. "
            f"SENSOR_CLASS_MAP is incomplete."
        ) from err
