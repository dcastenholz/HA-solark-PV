from enum import Enum


class ConnectionType(str, Enum):
    TCP = "tcp"
    RTU = "rtu"

CONF_CONNECTION_TYPE = "connection_type"
CONNECTION_TCP = ConnectionType.TCP.value
CONNECTION_RTU = ConnectionType.RTU.value
