"""Connection type constants for SolArk."""

from enum import Enum


# TODO - Unused strings??? convert to auto()
class ConnectionType(str, Enum):
    """Supported SolArk connection types."""

    TCP = "tcp"
    RTU = "rtu"

CONF_CONNECTION_TYPE = "connection_type"

# TODO - Do we really want these???
CONNECTION_TCP = ConnectionType.TCP.value
CONNECTION_RTU = ConnectionType.RTU.value
