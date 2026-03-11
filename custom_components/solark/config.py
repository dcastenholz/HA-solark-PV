import ipaddress
import re
import socket
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant.config_entries import CONF_NAME, ConfigEntry
from homeassistant.const import CONF_HOST

MIN_DEVICE_ID: int = 1
MAX_DEVICE_ID: int = 247

MIN_PORT: int = 1
MAX_PORT_NUMBER: int = 65535

class ConnectionType(str, Enum):
    TCP = "tcp"
    RTU = "rtu"

# TODO - https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/
@dataclass
class SolArkConfig:
    # Common connection parameters
    connection_type: ConnectionType
    device_id: int

    # TCP
    host: str | None
    port: int

    # Serial
    serial_port: str | None

    def __init__(self, entry: ConfigEntry):
        """
        Initialize the SolArkConfig object from a single url.

        The hostname (entry.data[CONF_HOST]) can be a valid URL (e.g. 192.168.2.2) or a serial port name (e.g. /dev/ttyUSB0 or COM1).
        If the hostname is not a valid URL, it will be interpreted as a serial port name.

        The device ID is an optional parameter that can be specified as a query parameter in the hostname (e.g. 192.168.2.2/;3).
        If the device ID is not specified, it will default to 1.

        The connection type is determined based on the hostname. If the hostname is a valid URL, it will be interpreted as a TCP connection.
        If the hostname is a serial port name, it will be interpreted as a serial connection."""
        self.entry_id = entry.entry_id
        self.name = entry.data.get(CONF_NAME)

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

        # Default values
        self.device_id = 1
        self.host = None
        self.port = 502
        self.serial_port = None

        if (parsed.port is None) and ((parsed.hostname is None) or parsed.hostname.lower().startswith("com")):
            self.connection_type = ConnectionType.RTU
            self.serial_port = parsed.path.rstrip("/") + parsed.netloc
        else:
            self.connection_type = ConnectionType.TCP
            self.host = parsed.hostname
            self.port = parsed.port or 502

        self.device_id = 1
        if parsed.params.isdigit() and int(parsed.params) < 256:
            self.device_id = int(parsed.params)


def validate_tcp_host_1(value: str) -> str:
    """Validate a hostname usable by a TCP Modbus client."""
    if not isinstance(value, str) or not value.strip():
        raise vol.Invalid("invalid_host")

    host = value.strip()

    try:
        # Try resolving the hostname/IP using the system resolver
        socket.getaddrinfo(host, None)
    except socket.gaierror as err:
        raise vol.Invalid("invalid_host") from err

    return host



HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)*[a-zA-Z0-9-]{1,63}$"
)

def is_valid_tcp_host(value: str) -> bool:
    """Return True if value is a valid TCP hostname, IPv4, or IPv6 address."""
    # TODO - Test for all valid forms
    if not isinstance(value, str):
        return False

    host = value.strip()
    if not host:
        return False

    # Check IPv4/IPv6
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    # Allow localhost
    if host == "localhost":
        return True

    # Allow standard DNS hostnames (simple check: all labels match HOSTNAME_RE)
    if all(HOSTNAME_RE.match(label) for label in host.split(".")):
        return True

    return False

def is_valid_tcp_port(tcp_port: int):
    return tcp_port >= 1 and tcp_port <= MAX_PORT_NUMBER

def is_valid_rtu_port(rtu_port: str) -> bool:
    """Return True if value is a plausible RTU serial port."""
    # TODO - Test for all valid forms
    if not isinstance(rtu_port, str):
        return False

    port = rtu_port.strip()
    if not port or " " in port:
        return False

    return True

def rtu_port_exists(rtu_port: str) -> bool:
    """Return True if the serial port exists on this system."""
    # TODO - Should we add this in???
    try:
        from serial.tools import list_ports
    except ImportError:
        return False

    available = {p.device for p in list_ports.comports()}
    return rtu_port in available

def is_valid_device_id(device_id: int):
    return device_id >= 1 and device_id <= MAX_DEVICE_ID
