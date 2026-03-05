"""
bridge.py - Synchronous RTU→TCP Modbus Bridge with connect/disconnect logging.

This module defines a ForwardingBlock and start_bridge() to run a Modbus RTU server
that forwards read requests to a TCP Modbus device on-demand. Logs include
client connect/disconnect approximations and all read requests.
"""

import logging
import os
import pty
import subprocess
import time
from typing import List

from pymodbus.client import ModbusTcpClient
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext, ModbusSparseDataBlock
from pymodbus.server import StartSerialServer

_LOGGER = logging.getLogger(__name__)


class ForwardingBlock(ModbusSparseDataBlock):
    """Custom Modbus data block that forwards RTU reads to a TCP device with logging."""

    def __init__(self, tcp_host: str, tcp_port: int, device_id: int, reg_count: int = 100):
        """Initialize the forwarding block with TCP device parameters."""
        super().__init__({i: 0 for i in range(reg_count)})
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.device_id = device_id
        self._client_connected = False

    def _log_connect(self):
        if not self._client_connected:
            self._client_connected = True
            _LOGGER.info("RTU client connected (first read received)")

    def _log_disconnect(self):
        if self._client_connected:
            self._client_connected = False
            _LOGGER.info("RTU client disconnected (no activity detected)")

    def getValues(self, address: int, count: int = 1) -> List[int]:
        """Read registers from TCP device on-demand; log connection, reads, and failures."""
        # Convert from 1-based (server) to 0-based (Solark TCP)
        corrected_address = address - 1

        self._log_connect()
        _LOGGER.info("RTU read request: address=%d count=%d", corrected_address, count)

        try:
            with ModbusTcpClient(self.tcp_host, port=self.tcp_port) as client:
                rr = client.read_holding_registers(address=corrected_address, count=count, device_id=self.device_id)
                if rr.isError():
                    _LOGGER.warning("TCP read error at address %d count %d", corrected_address, count)
                    return [0] * count
                _LOGGER.debug("TCP read successful: %s", rr.registers)
                return rr.registers
        except Exception as exc:
            _LOGGER.exception("TCP connection failed: %s", exc)
            return [0] * count

    @staticmethod
    def test_tcp_read(tcp_host: str, tcp_port: int, device_id: int, address: int, count: int = 1) -> List[int]:
        """Static method to quickly read registers from a TCP Modbus device."""
        _LOGGER.info("Static test TCP read -> %s:%d device=%d address=%d count=%d",
                     tcp_host, tcp_port, device_id, address, count)
        try:
            with ModbusTcpClient(tcp_host, port=tcp_port) as client:
                rr = client.read_holding_registers(address=address, count=count, device_id=device_id)
                if rr.isError():
                    _LOGGER.warning("TCP read error in static test at address %d count %d", address, count)
                    return [0] * count
                _LOGGER.info("Static test read successful: %s", rr.registers)
                return rr.registers
        except Exception as exc:
            _LOGGER.exception("TCP static test connection failed: %s", exc)
            return [0] * count

def run_static_test(tcp_host: str, tcp_port: int, device_id: int):
    """Perform a quick TCP read test (registers 3–7) and log results."""
    registers = ForwardingBlock.test_tcp_read(tcp_host, tcp_port, device_id, address=3, count=5)
    _LOGGER.info("Static test read registers 3–7: %s", registers)
    return registers


def start_bridge(
    serial_port: str | None,
    baudrate: int,
    tcp_host: str,
    tcp_port: int,
    device_id: int,
    reg_count: int = 100,
) -> str:
    """
    Start the synchronous RTU→TCP bridge.

    If `serial_port` is None, it will automatically create a virtual serial pair
    using socat. The bridge listens on the master port, and the client should
    connect to the slave port.
    """
    try:
        if not serial_port or serial_port.strip() == "":
            # Create socat PTY pair
            master_link = "/tmp/bridge_master"
            slave_link = "/tmp/bridge_slave"
            cmd = [
                "socat", "-d", "-d",
                f"PTY,link={master_link},raw,echo=0",
                f"PTY,link={slave_link},raw,echo=0"
            ]
            proc = subprocess.Popen(cmd)
            _LOGGER.info("Created virtual serial pair with socat: master=%s, slave=%s", master_link, slave_link)

            serial_port = master_link  # bridge listens here
            slave_port = slave_link     # Solark client connects here
        else:
            slave_port = serial_port
            _LOGGER.info("Using fixed serial port: %s", serial_port)

        _LOGGER.info(
            "Bridge configuration -> Serial Port: %s, TCP: %s:%d, device_id: %d, registers: %d",
            serial_port, tcp_host, tcp_port, device_id, reg_count
        )
        _LOGGER.info("Solark/RTU client must connect to: %s", slave_port)

        # Forwarding block
        block = ForwardingBlock(tcp_host=tcp_host, tcp_port=tcp_port, device_id=device_id, reg_count=reg_count)
        device = ModbusDeviceContext(hr=block)
        context = ModbusServerContext(devices=device, single=True)

        _LOGGER.info("Starting RTU→TCP bridge on %s (device %d) forwarding to TCP %s:%d",
                     serial_port, device_id, tcp_host, tcp_port)

        # Start blocking RTU server
        StartSerialServer(
            context=context,
            port=serial_port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
        )

        # After server exits
        block._log_disconnect()
        _LOGGER.info("RTU→TCP bridge stopped")

        return slave_port

    except Exception as exc:
        _LOGGER.error(
            "Failed to start RTU→TCP bridge!\nSerial port: %s\nTCP host: %s:%d\nDevice ID: %d\nException: %s",
            serial_port or "<empty>", tcp_host, tcp_port, device_id, exc, exc_info=True
        )
        raise
