"""Since pymodbus BinaryPayloadDecoder is deprecated, create our own to replace it."""

import logging
from array import array
from struct import pack, unpack

from pymodbus.exceptions import ParameterException

_LOGGER = logging.getLogger(__name__)

class BinaryPayloadDecoder:
    """Custom Solark BinaryPayloadDecoder to replace the deprecated one from pymodbus.
    Word order and byte order are SolArk specific.

    Decode payload messages from a modbus response message.

    A simple wrapper around the struct module that saves time looking up
    format strings. Example::

        decoder = BinaryPayloadDecoder(payload)
        first   = decoder.decode_8bit_uint()
        second  = decoder.decode_16bit_uint()
    """

    def __init__(self, registers: list[int] | None):
        """Initialize a new BinaryPayloadDecoder.
        :param registers: The register results to initialize with

        :raises ParameterException:
        """

        if registers is None:
            raise ParameterException("registers parameter cannot be None")

        _LOGGER.debug("Registers: %s", registers)

        self._payload = pack(f"!{len(registers)}H", *registers)
        self._pointer = 0x00

        # SolArk specific values
        # byteorder: The endianness of the payload
        self._byteorder = ">"
        # wordorder: The endianness of the word (when wordcount is >= 2)
        self._wordorder = "<"

    def _unpack_words(self, handle) -> bytes:
        """Unpack words based on the word order and byte order.

        # ---------------------------------------------- #
        # Unpack in to network ordered unsigned integer  #
        # Change Word order if little endian word order  #
        # Pack values back based on correct byte order   #
        # ---------------------------------------------- #
        """
        if "<" in {self._byteorder, self._wordorder}:
            handle = array("H", handle)
            if self._byteorder == "<":
                handle.byteswap()
            if self._wordorder == "<":
                handle.reverse()
            handle = handle.tobytes()
        _LOGGER.debug("handle: %s", handle)
        return handle

    def _decode(self, fmt: str, size: int, use_word_unpack: bool = False):
        """Decode an integer from the payload.

        Args:
            fmt: The struct format string for unpacking (e.g., 'B', 'H', 'i').
            size: Number of bytes to consume from the payload.
            use_word_unpack: Whether to call _unpack_words before unpacking.

        Returns:
            The decoded integer value.
        """
        if self._pointer + size > len(self._payload):
            raise ValueError(
                f"Decoder buffer overrun: need {size} bytes at {self._pointer}, "
                f"payload length {len(self._payload)}"
            )

        start = self._pointer
        self._pointer += size
        handle: bytes = self._payload[start : self._pointer]

        if use_word_unpack:
            handle = self._unpack_words(handle)

        return unpack(fmt, handle)[0]

    def decode_16bit_int(self):
        """Decode 16-bit signed integer."""
        return self._decode(self._byteorder + "h", 2)

    def decode_16bit_uint(self):
        """Decode 16-bit unsigned integer."""
        return self._decode(self._byteorder + "H", 2)

    def decode_32bit_int(self):
        """Decode 32-bit signed integer."""
        return self._decode("!i", 4, use_word_unpack=True)

    def decode_32bit_uint(self):
        """Decode 32-bit unsigned integer."""
        return self._decode("!I", 4, use_word_unpack=True)

    def decode_64bit_int(self):
        """Decode 64-bit signed integer."""
        return self._decode("!q", 8, use_word_unpack=True)

    def decode_64bit_uint(self):
        """Decode 64-bit unsigned integer."""
        return self._decode("!Q", 8, use_word_unpack=True)

    # Strings and skipping
    def decode_string(self, size=1):
        """Decode bytes string of given size."""
        start = self._pointer
        self._pointer += size
        return self._payload[start : self._pointer]

    def skip_registers(self, nregisters):
        """Skip given number of registers."""
        self._pointer += nregisters * 2  # Each register is 2 bytes
