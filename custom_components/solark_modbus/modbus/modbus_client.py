""" Update the register map with the latest values read from the inverter and return a combined dictionary of all data.

Class is responsible for reading the data from the inverter and returning it as a dictionary.
The class maintains the last successful reading and timestamp, and if a read fails,
it will return the last known values if they are not too old, otherwise it will return an error message.

Philosopy here is  to perform a series of modbus reads, setting a single error flag for the whole dataset
on the failure of any read.
read, check for a successful read of all data, and return the last complete data.
If the read was not successful, then return the last known values if they are not too old, otherwise return an error message.
"""
import logging
import threading
from typing import Iterator

from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException

from ..config.config_connection_type import ConnectionType
from ..const import MODBUS_EXCEPTIONS
from ..entry_map.base_entry import BaseRegisterEntry
from ..entry_map.binary_sensor_entry import RegisterBoolEntry
from ..entry_map.register_entry import DataType, RegisterNumericEntry, StringEntry
from ..maps.solark_register_map import SolArkRegisterMap
from .binary_payload_decoder import BinaryPayloadDecoder
from .modbus_config import ModbusConfig
from .pymodbus_wrapper import ModbusClientWrapper, ModbusResponse, ModbusResponseError

_LOGGER = logging.getLogger(__name__)

# Per SolArk modbus documentation, register read count is 0x0001~ 0x007D, or 1 to 125
MAX_READ_REGISTER_COUNT = 125

class ModbusDecodeError(RuntimeError):
    """Raised when Modbus register decoding fails."""


class SolArkModbusClient():
    """Thread-safe wrapper for reading inverter data from Modbus using register dictionary."""

    def __init__(self, config: ModbusConfig, register_map: SolArkRegisterMap) -> None:
        """Initialize the Modbus hub."""
        if config.connection_type == ConnectionType.TCP:
            self._client = ModbusClientWrapper(host=config.host, port=config.port)
        elif config.connection_type == ConnectionType.RTU:
            self._client = ModbusClientWrapper(serial_port=config.serial_port, baudrate=9600)

        self.device_id = config.device_id
        self._lock = threading.Lock()
        self._register_map = register_map
        self._connected = False
        self._stopped = False

    def close(self) -> None:
        """Close the Modbus client connection safely."""
        with self._lock:
            if self._client:
                try:
                    self._client.close()
                except Exception as e:
                    _LOGGER.exception("Error closing modbus client connection: %s", e)
                finally:
                    self._connected = False
                    self._client = None

    # ---- Connection handling ----
    def _ensure_connected(self) -> None:
        """Ensure the Modbus client is connected.

        PyModbus attempts to handle reconnect in many situations, but not all.
        It is an undocumented feature. A failure in the pymodbus client creation
        used to leave the hub in an unrecoverable state. By explicitly handling it,
        we handle a failure at any point, as well as any reconnection attempt that
        pymodbus does not handle properly."""

        if self._client is None:
            raise ConnectionException("Modbus client is not initialized")

        if self._stopped:
            raise ConnectionException("Modbus client is stopped")

        if self._connected:
            return

        if not self._client.connect():
            raise ConnectionException("Modbus connection failed")

        self._connected = True

    def read_modbus_inverter_data(self) -> bool:
        """Read the static inverter data from the inverter and store the results in the register map."""

        # TODO - Move this to a static data list and read once and save values.
        self._process_register_range(self._register_map.SN, self._register_map.INFO_RATED_POWER)   # R5 - R16

        if self._register_map.is_error():
            _LOGGER.error("Reading inverter data failed!")

        return not self._register_map.is_error()

    def read_modbus_realtime_data(self) -> bool:
        """Read the real-time data from the inverter and store the results in the register map."""
        self._process_register_range(self._register_map.INFO_MPPT_PHASE_COUNTS_RAW, self._register_map.SYSTEM_TIME_MS_RAW)  # R18 - R24

        # self._process_register_range(self.register_map.DAILYINV_E, self.register_map.GRIDFREQ)  # R60 - R79
        # self._process_register_range(self.register_map.DAILYLOAD_E, self.register_map.ACHSTempC)  # R84 - R91

        self._process_register_range(self._register_map.DAILYINV_E, self._register_map.ACHSTempC)  # R60 - R91

        # self._process_register_range(self._register_map.TOTALINV_E, self._register_map.DAILYPV_E)  # R96 - R108
        # self._process_register_range(self._register_map.PV1_V, self._register_map.PV3_C)  # R109 - R114

        self._process_register_range(self._register_map.TOTALINV_E, self._register_map.PV3_C)  # R96 - R114

        # self._process_register_range(self._register_map.GRIDL1N_V, self._register_map.GRIDLMTL1_P)  # R150 - R170
        # self._process_register_range(self._register_map.GRIDLMTL2_P, self._register_map.PV3_P)  # R171 - R188
        # self._process_register_range(self._register_map.BATT_P, self._register_map.GEN_FREQ)  # R190 - R196

        # self._process_register_range(self._register_map.GRIDL1N_V, self._register_map.GRID_RLY)  # R150 - R194
        # self._process_register_range(self._register_map.GEN_RLY_RAW)  # R195
        # self._process_register_range(self._register_map.GEN_FREQ)  # R196

        self._process_register_range(self._register_map.GRIDL1N_V, self._register_map.GEN_FREQ)  # R150 - R196

        self._process_register_range(self._register_map.TIMEOFUSE_ENABLED, self._register_map.TIMEOFUSE_ENABLED_6)  # R248 - R279

        self._process_register_range(self._register_map.BMS_CHARGING_VOLTAGE, self._register_map.BMS_TEMP)  # R312 - R319

        return not self._register_map.is_error()

    def _process_register_range(self, start_register: BaseRegisterEntry, end_register: BaseRegisterEntry | None = None):
        """Read the holding registers and decode the vlues for a range of BaseRegisterEntry objects."""

        if end_register is None:
            end_register = start_register

        register_count = end_register.address + end_register.register_length - start_register.address

        # Per SolArk modbus documentation, register count read is 0x0001~ 0x007D, or 1 to 125
        if register_count > MAX_READ_REGISTER_COUNT:
            raise RuntimeError(f"Holding register read count exceeds maximum of {MAX_READ_REGISTER_COUNT}. Register range requested contains {register_count} registers.")

        # Init the register map entries prior to read attempt
        # self._register_map.init_register_range(start_register, end_register)

        # Read the registers from the inverter
        modbus_response = self._read_holding_registers(address=start_register.address, count=register_count)

        # Process the Modbus response and update the register map entries with the decoded values if successful,
        # otherwise set error state on the register map
        if modbus_response.isError():
            _LOGGER.error(
                "Processing registers %d-%d failed!", start_register.address, end_register.address + end_register.register_length - 1
            )
            self._register_map.set_error()
            return

        decoder = BinaryPayloadDecoder(modbus_response.registers)

        entries = self._register_map.entries_register_read_in_range(start_register, end_register)
        self._decode_register_map_entries(decoder, entries)

    def _decode_register_map_entries(self, decoder: BinaryPayloadDecoder, entries: Iterator[BaseRegisterEntry]) -> None:
        """Decode the Modbus response registers and update the register map entries with the decoded values."""
        next_address: int | None = None

        for entry in entries:
            # Skip if there is a gap in the registers we want to process.
            if next_address is not None and entry.address != next_address:
                gap = entry.address - next_address
                decoder.skip_registers(gap)

            if isinstance(entry, StringEntry):
                self._decode_register_map_string_entry(decoder, entry)

                if entry.sensor_value is None:
                    _LOGGER.error("Failed to decode register %s with data type string: value is None", entry.address)
                    self._register_map.set_error()
            elif isinstance(entry, RegisterBoolEntry):
                self._decode_register_map_bool_entry(decoder, entry)

                if entry.sensor_value is None:
                    _LOGGER.error("Failed to decode register %s with data type bool: value is None", entry.address)
                    self._register_map.set_error()
            elif isinstance(entry, RegisterNumericEntry):
                self._decode_register_map_numeric_entry(decoder, entry)

                if entry.sensor_value is None:
                    _LOGGER.error("Failed to decode register %s with data type %s: value is None", entry.address, entry.data_type)
                    self._register_map.set_error()
            else:
                raise RuntimeError(f"Unhandled entry type: {type(entry).__name__} (entry={entry})")

            next_address = entry.address + entry.register_length

    def _decode_register_map_string_entry(self, decoder: BinaryPayloadDecoder, entry: StringEntry) -> None:
        """Decode a single register map entry using the specified decoder, and store the value into the register entry."""

        entry.sensor_value = decoder.decode_string(entry.register_length * 2).decode("ascii")

    def _decode_register_map_bool_entry(self, decoder: BinaryPayloadDecoder, entry: RegisterBoolEntry) -> None:
        """Decode a single register map entry using the specified decoder, and store the value into the register entry."""

        entry.sensor_value = bool(decoder.decode_16bit_uint())

    def _decode_register_map_numeric_entry(self, decoder: BinaryPayloadDecoder, entry: RegisterNumericEntry) -> None:
        """Decode a single register map entry using the specified decoder, and store the value into the register entry."""

        int_value: int
        if entry.data_type == DataType.INT16:
            int_value = decoder.decode_16bit_int()
        elif entry.data_type == DataType.UINT16:
            int_value = decoder.decode_16bit_uint()
        elif entry.data_type == DataType.INT32:
            int_value = decoder.decode_32bit_int()
        elif entry.data_type == DataType.UINT32:
            int_value = decoder.decode_32bit_uint()
        elif entry.data_type == DataType.INT64:
            int_value = decoder.decode_64bit_int()
        elif entry.data_type == DataType.UINT64:
            int_value = decoder.decode_64bit_uint()
        else:
            raise ModbusDecodeError(f"Failed to decode register {entry.address} having data type {entry.data_type})")

        entry.sensor_value = int_value

    def _read_holding_registers(self, address: int, count: int) -> ModbusResponse:
        """Reads a block of holding registers from the inverter via Modbus

        Catch and handle common exceptions by returning error.
        Should not return NONE, and bubbles up ONLY unexpected exceptions.
        """
        with self._lock:
            try:
                self._ensure_connected()
            except (ConnectionException) as exc:
                _LOGGER.error("Ensure connected failed: %s", exc)
                return ModbusResponseError(exc)

            assert self._client is not None

            try:
                result: ModbusResponse = self._client.read_holding_registers(address, count=count, device_id=self.device_id)
            except (ModbusIOException, ConnectionException, ModbusException) as exc:
                return ModbusResponseError(exc)

            if result.isError():
                code = getattr(result, "exception_code", None)
                if code:
                    err = MODBUS_EXCEPTIONS.get(code, f"Unknown Modbus exception: {code}")
                else:
                    err = str(result)

                _LOGGER.warning("Reading holding registers Modbus error: %s", err)

            return result
