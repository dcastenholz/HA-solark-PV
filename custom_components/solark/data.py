from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription

from .base_map import BaseMap
from .config_data import ConfigData
from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator_data import CoordinatorData
from .coordinator_metrics import CoordinatorMetrics
from .modbus_client import SolArkModbusClient
from .modbus_config import ModbusConfig
from .solark_register_map import SolArkRegisterMap

if TYPE_CHECKING:
    # This line can be removed if manifest.json has "homeassistant": "2024.6.0" or greater
    from .config_entry import SolArkConfigEntry
    from .coordinator import SolArkCoordinator
    from .solark_sensor_map import SolArkSensorMap

TFilter = TypeVar("TFilter", bound=EntityDescription)

@dataclass
class SolArkData:
    hass: HomeAssistant
    config_entry: "SolArkConfigEntry"
    config_data: ConfigData
    modbus_config: ModbusConfig
    modbus_client: SolArkModbusClient
    device_info: DeviceInfo
    coordinator_metrics: CoordinatorMetrics

    register_map: SolArkRegisterMap
    calculated_sensor_map: SolArkSensorMap

    entry_maps: List[BaseMap]

    # This MUST be initialized so the
    previous_data_updated: CoordinatorData = field(default_factory=lambda: CoordinatorData({}, datetime.now()))
    last_data_updated: CoordinatorData = field(default_factory=lambda: CoordinatorData({}, datetime.now()))

    _coordinator: Optional["SolArkCoordinator"] = None

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ):
        # Local import prevents circular import
        from .config_entry import SolArkConfigEntry  # pylint: disable=C0415
        from .solark_sensor_map import SolArkSensorMap

        self.hass = hass
        # Set the config entry first to enable the read-only properties
        self.config_entry = SolArkConfigEntry(hass, entry)
        self.config_entry.runtime_data = self

        self.config_data = ConfigData.from_storage_data(self.config_entry)
        self.modbus_config = ModbusConfig(self.config_data)
        self.register_map = SolArkRegisterMap(self)
        self.calculated_sensor_map = SolArkSensorMap(self)
        self.modbus_client = SolArkModbusClient(self.modbus_config, self.register_map)
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.name)},
            name=self.config_entry.name,
            manufacturer=ATTR_MANUFACTURER,
        )

        self.entry_maps = [self.register_map, self.calculated_sensor_map]

        self.coordinator_metrics = CoordinatorMetrics()

    @property
    def name(self) -> str:
        return self.config_entry.name

    @property
    def scan_interval(self) -> int:
        return self.config_entry.scan_interval

    @property
    def coordinator(self) -> "SolArkCoordinator":
        if self._coordinator is None:
            raise RuntimeError("Coordinator not initialized")
        return self._coordinator

    @coordinator.setter
    def coordinator(self, value: "SolArkCoordinator") -> None:
        self._coordinator = value

    # @property
    # def descriptions(self) -> list[EntityDescription]:
    #     descriptions: list[EntityDescription] = []

    #     for entry_map in self.entry_maps:
    #         descriptions += entry_map.descriptions

    #     return descriptions

    def descriptions_of_type(self, entry_type: type[TFilter]) -> list[TFilter]:
        descriptions: list[TFilter] = []

        for entry_map in self.entry_maps:
            descriptions += entry_map.descriptions_of_type(entry_type)

        return descriptions

    async def close(self) -> None:
        """Cleanly shut down all allocated resources."""
        # Stop the coordinator if it exists
        if self._coordinator:
            await self._coordinator.async_stop()  # if async, you can run with asyncio.create_task or call in async context
            self._coordinator = None

    @property
    def current_data(self) -> dict[str, Any]:
        return {**self.register_map.as_dict(), **self.calculated_sensor_map.as_dict()}

    # ----------------------------------
    # Update data lifecycle events
    # ----------------------------------
    def on_startup(self):
        self.coordinator_metrics.on_startup()
        return

    def on_data_reading(self):
        self.coordinator_metrics.on_data_reading()
        return

    def on_data_read(self):
        self.coordinator_metrics.on_data_read()
        return

    def on_data_read_failed(self):
        self.coordinator_metrics.on_data_read_failed()
        return

    def on_data_updated(self):
        self.previous_data_updated = self.last_data_updated
        self.last_data_updated = CoordinatorData(data=self.current_data, timestamp=datetime.now())
        self.coordinator_metrics.on_data_updated()
        return

    def on_shutdown(self):
        self.coordinator_metrics.on_shutdown()
        return
