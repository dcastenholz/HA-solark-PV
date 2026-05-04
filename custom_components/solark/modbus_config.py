"""Modbus configuration helpers for SolArk."""

import ipaddress
import re
import socket
from dataclasses import dataclass
from typing import TYPE_CHECKING

import voluptuous as vol

from .config_connection_type import ConnectionType
from .const import MAX_DEVICE_ID, MAX_PORT_NUMBER

if TYPE_CHECKING:
    from .config_data import ConfigData


@dataclass
class ModbusConfig:
    """Resolved Modbus connection settings."""

    # Common connection parameters
    connection_type: ConnectionType
    device_id: int

    # TCP
    host: str | None
    port: int

    # Serial
    serial_port: str | None

    def __init__(self, config_data: "ConfigData"):
        """Initialize Modbus settings from config data."""
        self.name = config_data.name
        self.device_id = config_data.device_id
        self.connection_type = config_data.connection_type

        if self.connection_type == ConnectionType.RTU:
            self.serial_port = config_data.rtu_port
        else:
            self.host = config_data.tcp_host
            self.port = config_data.tcp_port

# TODO - Remove if unused
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
    """Return True if value is a valid TCP port."""
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
    """Return True if value is a valid Modbus device ID."""
    return device_id >= 1 and device_id <= MAX_DEVICE_ID
