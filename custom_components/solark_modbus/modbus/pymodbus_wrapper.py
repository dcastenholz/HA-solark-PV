"""Read-only, thread-safe, and async wrapper for PyModbus >=3.1.1 with full backwards compatibility.

Provides:
- Automatic client import handling for TCP and Serial
- Automatic keyword argument mapping for slave/device_id
- Thread-safe read/write operations
- Automatic connection failure handling
- Normalized response object with `.registers` and `.isError()`

Home Assistant Version  Pymodbus Version   Python Version
2023.2                  3.1.1              3.10
2024.3                  3.6.5 - 3.6.6      3.12
2024.4                  3.6.6 - 3.6.7      3.12
2025.1                  3.7.4              3.12
2025.2                  3.8.3              3.13
2025.7                  3.9.2              3.13
2025.9                  3.11.0 - 3.11.1    3.13
2025.10                 3.11.2             3.13

"""

# TODO - Keep this in sync with the manifest and README regarding supported PyModbus versions.
from __future__ import annotations

import logging

import pymodbus
from packaging import version

# ---- Client imports ----
from pymodbus.client import ModbusSerialClient, ModbusTcpClient

from ..const import DEFAULT_PORT, MODBUS_EXCEPTIONS

_LOGGER = logging.getLogger(__name__)

# ---- Version parsing ----
PYMODBUS_VERSION = version.parse(pymodbus.__version__)

# ---- Version flags ----
IS_PRIOR_TO_V3_5_0 = PYMODBUS_VERSION < version.parse("3.5.0")  # noqa: SIM300
IS_PRIOR_TO_V3_10_0 = PYMODBUS_VERSION < version.parse("3.10.0")  # noqa: SIM300


# ---- Response abstraction ----
class ModbusResponse:
    """Wrapper for Modbus read responses for PyModbus 3.1.1 → current."""

    __slots__ = ("_response",)

    def __init__(self, response: object | None) -> None:
        """Initialize ModbusResponse with a PyModbus response object."""
        self._response = response

    @property
    def registers(self) -> list[int] | None:
        """Return the list of registers or None if unavailable."""
        return getattr(self._response, "registers", None)

    @property
    def is_error(self) -> bool:
        """Return True if the response indicates an error."""
        return self.isError()

    def isError(self) -> bool:  # pylint: disable=invalid-name
        """Return True if the response indicates an error."""
        if self._response is None:
            return True

        if hasattr(self._response, "isError"):
            return self._response.isError()  # type: ignore[call-arg] optional if needed

        # If no 'isError' method, consider it an error if it has no 'registers'
        return not hasattr(self._response, "registers")

    def get_exception_code(self) -> int | None:
        """Return the exception if the response contains one."""
        return getattr(self._response, "exception_code", None)

    def get_exception_string(self) -> str | None:
        """Return the exception if the response contains one."""
        code = self.get_exception_code()

        if code:
            err = MODBUS_EXCEPTIONS.get(code, f"Unknown Modbus exception: {code}")
        else:
            err = None

        return err

    @property
    def error(self) -> str | None:
        """Return the error string if the response indicates an error."""
        if hasattr(self._response, "error_message"):
            return getattr(self._response, "error_message")
        if self.is_error:
            return str(self._response)
        return None

    def __repr__(self) -> str:
        """Return a string representation of the ModbusResponse."""
        # TODO - Add function_code and filter the attributes based on is_error
        return f"<ModbusResponse error={self.is_error} registers={self.registers} exception_code={self.get_exception_code()}>"


class ModbusResponseError(ModbusResponse):
    """Represents an error condition."""

    __slots__ = ("_exception",)

    def __init__(self, exception: Exception) -> None:
        """Initialize a ModbusResponseError with an exception."""
        self._exception = exception
        super().__init__(None)

    def isError(self) -> bool:  # pylint: disable=invalid-name
        """Return True if the response indicates an error."""
        return True

    def get_exception(self) -> Exception:
        """Return the exception."""
        return self._exception


class ModbusClientWrapper:
    """Wrapper for Modbus TCP/Serial."""

    __slots__ = "_client"

    def __init__(
        self,
        host: str | None = None,
        port: int = DEFAULT_PORT,
        serial_port: str | None = None,
        baudrate: int = 9600,
    ) -> None:
        """Create a Modbus client wrapper (TCP or Serial)."""
        self._client: ModbusTcpClient | ModbusSerialClient

        if serial_port is not None:
            if IS_PRIOR_TO_V3_5_0:
                self._client = ModbusSerialClient(  # pylint: disable=E1123
                    method="rtu",  # type: ignore[call-arg]
                    port=serial_port,
                    baudrate=baudrate,
                    timeout=5,
                )
            else:
                self._client = ModbusSerialClient(port=serial_port, baudrate=baudrate, timeout=5)
        elif host is not None:
            self._client = ModbusTcpClient(host=host, port=port, timeout=5)
        else:
            raise ValueError("Either host or serial_port must be provided")

    # ---- Close client ----
    def close(self) -> None:
        """Close the underlying Modbus client."""
        if self._client:
            self._client.close()

    def connect(self) -> bool:
        """Connect the underlying Modbus client."""
        if self._client:
            return self._client.connect()
        return False

    # ---- Sync read ----
    def read_holding_registers(self, address: int, count: int, device_id: int) -> ModbusResponse:
        """Read holding registers from the configured Modbus device."""
        device_kw = self._get_device_id_param_name(device_id)
        pdu = self._client.read_holding_registers(address=address, count=count, **device_kw)  # type: ignore[arg-type]
        return ModbusResponse(pdu)

    # ---- Sync write ----
    def write_registers(self, address: int, values: list[int], device_id: int) -> ModbusResponse:
        """Write registers to the configured Modbus device."""
        device_kw = self._get_device_id_param_name(device_id)
        pdu = self._client.write_registers(address=address, values=values, **device_kw)  # type: ignore[arg-type]
        return ModbusResponse(pdu)

    # ---- Helper for slave/device_id ------
    def _get_device_id_param_name(self, device_id: int) -> dict[str, int]:
        """Return the correct keyword argument for PyModbus >=3.1.1."""
        if IS_PRIOR_TO_V3_10_0:
            return {"slave": device_id}  # 3.1.1 → 3.9.x
        return {"device_id": device_id}  # 3.10+
