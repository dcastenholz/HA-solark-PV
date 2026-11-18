"""Runtime data container for SolArk."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription

from .config.config_data import ConfigData
from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator.coordinator_data import CoordinatorData
from .coordinator.coordinator_metrics import CoordinatorMetrics
from .coordinator.coordinator_metrics_storage import MetricsStorage
from .entry_map.base_map import BaseMap
from .maps.solark_metrics_map import SolArkMetricsMap
from .maps.solark_register_map import SolArkRegisterMap
from .modbus.modbus_client import SolArkModbusClient
from .modbus.modbus_config import ModbusConfig

if TYPE_CHECKING:
    from .coordinator import SolArkCoordinator
    from .maps.solark_sensor_map import SolArkSensorMap

TFilter = TypeVar("TFilter", bound=EntityDescription)


@dataclass
class SolArkData:
    """Runtime data container for a SolArk config entry."""

    hass: HomeAssistant
    config_entry: ConfigEntry
    config_data: ConfigData
    modbus_config: ModbusConfig
    modbus_client: SolArkModbusClient
    device_info: DeviceInfo
    coordinator_metrics: CoordinatorMetrics
    metrics_storage: MetricsStorage

    register_map: SolArkRegisterMap
    calculated_sensor_map: SolArkSensorMap
    metrics_map: SolArkMetricsMap

    entry_maps: List[BaseMap]

    previous_data_updated: CoordinatorData
    last_data_updated: CoordinatorData

    _coordinator: Optional["SolArkCoordinator"] = None

    serial_number: str = ""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize runtime data for a config entry."""
        from .maps.solark_sensor_map import SolArkSensorMap

        self.hass = hass
        self.config_entry = entry
        self.config_entry.runtime_data = self

        # ---- config / maps ----
        self.config_data = ConfigData.from_storage_data(self.config_entry)

        self.register_map = SolArkRegisterMap(self)
        self.calculated_sensor_map = SolArkSensorMap(self)
        self.metrics_map = SolArkMetricsMap(self)

        self.entry_maps = [
            self.register_map,
            self.calculated_sensor_map,
            self.metrics_map,
        ]

        # ---- modbus ----
        self.modbus_config = ModbusConfig(self.config_data)
        self.modbus_client = SolArkModbusClient(self.modbus_config, self.register_map)

        # ---- metrics (must exist before storage restore) ----
        self.coordinator_metrics = CoordinatorMetrics()
        self.metrics_storage = MetricsStorage(self)

        # ---- device ----
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.name)},
            name=self.name,
            manufacturer=ATTR_MANUFACTURER,
        )

        # ---- data cache ----
        now = datetime.now()
        self.previous_data_updated = CoordinatorData({}, now)
        self.last_data_updated = CoordinatorData({}, now)

    # ----------------------------------
    # properties
    # ----------------------------------
    @property
    def name(self) -> str:
        """Return the configured instance name."""
        return self.config_entry.data[CONF_NAME]

    @property
    def coordinator(self) -> "SolArkCoordinator":
        """Return the initialized data update coordinator."""
        if self._coordinator is None:
            raise RuntimeError("Coordinator not initialized")
        return self._coordinator

    @coordinator.setter
    def coordinator(self, value: "SolArkCoordinator") -> None:
        """Set the data update coordinator."""
        self._coordinator = value

    # ----------------------------------
    # entity helpers
    # ----------------------------------
    def descriptions_of_type(self, entry_type: type[TFilter]) -> list[TFilter]:
        """Return entity descriptions of the requested type from all maps."""
        result: list[TFilter] = []
        for entry_map in self.entry_maps:
            result.extend(entry_map.descriptions_of_type(entry_type))
        return result

    # ----------------------------------
    # metrics persistence (FIXED)
    # ----------------------------------
    async def load_metrics(self) -> None:
        """Load metrics into runtime object."""
        await self.metrics_storage.async_restore_into_runtime()

    async def store_metrics(self) -> None:
        """Persist metrics safely."""
        await self.metrics_storage.async_persist_runtime()

    # ----------------------------------
    # lifecycle
    # ----------------------------------
    async def on_load_entry(self) -> None:
        """Startup."""
        # Load saved coordinator metrics
        await self.load_metrics()

    async def on_unload_entry(self) -> None:
        """Clean shutdown."""
        if self._coordinator:
            await self._coordinator.async_stop()
            self._coordinator = None

    # ----------------------------------
    # data cache
    # ----------------------------------
    def cache_updated_data(self) -> None:
        """Cache the latest successful register and calculated sensor data."""
        self.previous_data_updated = self.last_data_updated

        data = self.register_map.data | self.calculated_sensor_map.data

        self.last_data_updated = CoordinatorData(
            data=data,
            timestamp=datetime.now(),
        )
