from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .config_flow_state import ConfigFlowState
from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator_data import CoordinatorData
from .coordinator_metrics import CoordinatorMetrics
from .modbus_client import SolArkModbusClient
from .modbus_config import ModbusConfig
from .solark_register_map import SolArkRegisterMap

if TYPE_CHECKING:
    from .config_entry import SolArkConfigEntry
    from .coordinator import SolArkCoordinator
    from .solark_sensor_map import SolArkSensorMap

@dataclass
class SolArkData:
    hass: HomeAssistant
    config_entry: "SolArkConfigEntry"
    config_flow_state: ConfigFlowState
    modbus_config: ModbusConfig
    modbus_client: SolArkModbusClient
    device_info: DeviceInfo
    register_map: SolArkRegisterMap
    calculated_sensor_map: SolArkSensorMap
    coordinator_metrics: CoordinatorMetrics
    last_successful_read_data: CoordinatorData | None

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

        self.config_flow_state = ConfigFlowState.from_config_entry(self.config_entry)
        self.modbus_config = ModbusConfig(self.config_flow_state)
        self.register_map = SolArkRegisterMap(self)
        self.calculated_sensor_map = SolArkSensorMap(self)
        self.modbus_client = SolArkModbusClient(self.modbus_config, self.register_map)
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.name)},
            name=self.config_entry.name,
            manufacturer=ATTR_MANUFACTURER,
        )
        self.coordinator_metrics = CoordinatorMetrics()

        self.last_successful_read_data = None

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

    async def close(self) -> None:
        """Cleanly shut down all allocated resources."""
        # Stop the coordinator if it exists
        if self._coordinator:
            await self._coordinator.async_stop()  # if async, you can run with asyncio.create_task or call in async context
            self._coordinator = None

    @property
    def current_data(self) -> dict[str, Any]:
        return {**self.register_map.as_dict(), **self.calculated_sensor_map.as_dict()}

    def on_startup(self):
        self.coordinator_metrics.on_startup()
        return

    def on_start(self):
        self.coordinator_metrics.on_start()
        return

    def on_success(self):
        self.last_successful_read_data = CoordinatorData(data=self.current_data, timestamp=datetime.now())
        # Increment update counter
        self.coordinator_metrics.on_success()
        return

    def on_failure(self):
        self.coordinator_metrics.on_failure()
        return
