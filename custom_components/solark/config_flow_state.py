from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL

from .config_entry import SolArkConfigEntry
from .const import (
    DEFAULT_DEVICE_ID,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_PORT_RTU,
    DEFAULT_SCAN_INTERVAL,
    MAX_DEVICE_ID,
)


class ConnectionType(str, Enum):
    TCP = "tcp"
    RTU = "rtu"

CONF_CONNECTION_TYPE = "connection_type"
CONNECTION_TCP = ConnectionType.TCP.value
CONNECTION_RTU = ConnectionType.RTU.value


# ------------------------------------------------------------
# Flow State
# ------------------------------------------------------------

@dataclass
class ConfigFlowState:
    name: str = DEFAULT_NAME
    scan_interval: int = DEFAULT_SCAN_INTERVAL
    connection_type: ConnectionType = ConnectionType.TCP
    tcp_host: str = DEFAULT_HOST
    tcp_port: int = DEFAULT_PORT
    rtu_port: str = DEFAULT_PORT_RTU
    device_id: int = DEFAULT_DEVICE_ID

    def _set_info_v1(self, entry: ConfigEntry):
        """
        Initialize the ConfigFlowState object from a ConfigEntry with a single url stored in entry.data[CONF_HOST].

        The hostname (entry.data[CONF_HOST]) can be a valid URL (e.g. 192.168.2.2) or a serial port name (e.g. /dev/ttyUSB0 or COM1).
        If the hostname is not a valid URL, it will be interpreted as a serial port name.

        The device ID is an optional parameter that can be specified as a query parameter in the hostname (e.g. 192.168.2.2/;3).
        If the device ID is not specified, it will default to 1.

        The connection type is determined based on the hostname. If the hostname is a valid URL, it will be interpreted as a TCP connection.
        If the hostname is a serial port name, it will be interpreted as a serial connection."""
        self.name = str(entry.data.get(CONF_NAME))

        parsed = urlparse(f"//{entry.data[CONF_HOST]}")

        # If it not a proper URL it might be a serial port.
        # This logic is tested to work with linux and windows serial port names,
        # port numbers and device_ids
        #
        # Tested URLs:
        #  192.168.2.2
        #  192.268.2.2:502
        #  192.168.2.2:502/;3
        #  192.168.2.2/;3
        #  /dev/ttyUSB0
        #  /dev/ttyUDB0/;3
        #  COM1
        #  COM1/;3
        #

        if (parsed.port is None) and ((parsed.hostname is None) or parsed.hostname.lower().startswith("com")):
            self.connection_type = ConnectionType.RTU
            self.rtu_port = parsed.path.rstrip("/") + parsed.netloc
        else:
            self.connection_type = ConnectionType.TCP
            self.tcp_host = str(parsed.hostname)
            self.tcp_port = parsed.port or DEFAULT_PORT

        if parsed.params.isdigit() and int(parsed.params) < MAX_DEVICE_ID:
            self.device_id = int(parsed.params)

    @classmethod
    def from_config_entry(cls, entry: ConfigEntry) -> ConfigFlowState:
        state: ConfigFlowState = ConfigFlowState()

        if entry.version == 1:
            state._set_info_v1(entry)
        else:
            raise ValueError(entry.version)

        state.scan_interval = entry.data[CONF_SCAN_INTERVAL]

        return state

    def get_config_entry_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            CONF_NAME: self.name,
            CONF_SCAN_INTERVAL: self.scan_interval,
        }

        data.update(self.get_config_entry_data_v1())

        return data

    @classmethod
    def get_config_sensor_data(cls, entry: SolArkConfigEntry) -> dict[str, Any]:
        state: ConfigFlowState = ConfigFlowState.from_config_entry(entry)

        data: dict[str, Any] = {
            CONF_NAME: state.name,
            CONF_SCAN_INTERVAL: state.scan_interval,
            CONF_CONNECTION_TYPE: state.connection_type,
        }

        if state.connection_type == ConnectionType.TCP:
            data.update(
                {
                    CONF_HOST: state.tcp_host,
                    CONF_PORT: state.tcp_port
                }
            )
        else:
            data.update(
                {
                    CONF_PORT: state.rtu_port
                }
            )
        return data

    def get_config_entry_data_v1(self) -> dict[str, str]:
        """Return the VERSION 1 canonical host string for the entry."""
        host_string: str
        if self.connection_type == CONNECTION_TCP:
            host_string = f"{self.tcp_host}:{self.tcp_port}/;{self.device_id}"
        else:
            host_string = f"{self.rtu_port}/;{self.device_id}"

        data: dict[str, str] = {
            CONF_HOST: host_string
        }
        return data
