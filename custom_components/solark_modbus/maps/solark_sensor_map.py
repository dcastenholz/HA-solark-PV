"""Sensor map for sensors that are not DIRECTLY backed by scaled and offset register reads."""

import calendar
import datetime
import random
from typing import TYPE_CHECKING

from homeassistant.util import dt

from .._binary_sensor.binary_sensor_entry import BinaryProblemEntry
from .._sensor.sensor_class import SensorClass
from ..entry_map.sensor_entry import (
    ConfigEntry,
    DiagnosticEntry,
    EnergyTotalIncreasingCalculatedEntry,
    GeneratorRelayEntry,
    PowerEntry,
    SensorEntry_NoSet,
)
from ..entry_map.sensor_map import SensorMap
from ..helpers.fault_info import translate_fault_code_to_messages
from ..maps.solark_register_map import SolArkRegisterMap

if TYPE_CHECKING:
    from ..data import SolArkData

# ----------------------------
# Helpers
# ----------------------------
@staticmethod
def int_to_month(month_int: int) -> str:
    """Return the month name for a month number."""
    if 1 <= month_int <= 12:
        return calendar.month_name[month_int]
    raise ValueError("Month must be between 1 and 12")

@staticmethod
def get_mppt_phase_info(decimal_number: int) -> tuple[int, int]:
    """Return MPPT and phase counts from an encoded register value."""
    hex_tuple: tuple[str, str, str, str] = decimal_to_hex_tuple(decimal_number)
    info: tuple[int, int] = combine_decimal_digits(hex_tuple[0], hex_tuple[1]), combine_decimal_digits(hex_tuple[2], hex_tuple[3])
    return info

@staticmethod
def get_firmware(decimal_number: int) -> str:
    """Return a firmware version string from an encoded register value."""
    hex_tuple: tuple[str, ...] = decimal_to_hex_tuple(decimal_number)
    firmware: str = f"{hex_tuple[0]}.{hex_tuple[1]}.{hex_tuple[2]}.{hex_tuple[3]}"
    return firmware

@staticmethod
def decimal_to_hex_tuple(decimal_number: int) -> tuple[str, str, str, str]:
    """Return a four-character uppercase hex tuple for a decimal value."""
    # Convert to hex without the '0x' prefix and make uppercase
    hex_str = f"{decimal_number:04X}"
    # Create a tuple with each hex digit as a string
    return hex_str[0], hex_str[1], hex_str[2], hex_str[3]

@staticmethod
def combine_decimal_digits(a: int, b: int) -> int:
    """Combine two decimal digits into a two-digit integer."""
    return int(a) * 10 + int(b)

@staticmethod
def plural(value: int, word: str) -> str:
    """Return a value and pluralized word."""
    return f"{value} {word}{'' if value == 1 else 's'}"


# ----------------------------------
# Post processed sensor method definitions
# ----------------------------------
@staticmethod
def firmware_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update the firmware sensor value from firmware registers."""
    firmware: str = f"M {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_M))} / "
    firmware += f"S {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_S))} / "
    firmware += f"C {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_C))}"
    entry.sensor_value = firmware
    return

@staticmethod
def info_mppt_count_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update the MPPT count sensor value."""
    info: tuple[int, int] = get_mppt_phase_info(int(runtime_data.register_map.INFO_MPPT_PHASE_COUNTS_RAW))
    entry.sensor_value = f"{plural(info[0], 'MPPT')}"
    return

@staticmethod
def info_phase_count_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update the phase count sensor value."""
    info: tuple[int, int] = get_mppt_phase_info(int(runtime_data.register_map.INFO_MPPT_PHASE_COUNTS_RAW))
    entry.sensor_value = f"{plural(info[1], 'phase')}"
    return

@staticmethod
def system_date_time_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update the system date time sensor value from raw time registers."""
    register_map: SolArkRegisterMap = runtime_data.register_map
    year_month: tuple[int, int] = register_map.SYSTEM_TIME_YM_RAW.split_bytes_uint16()
    day_hour: tuple[int, int] = register_map.SYSTEM_TIME_DH_RAW.split_bytes_uint16()
    minute_second: tuple[int, int] = register_map.SYSTEM_TIME_MS_RAW.split_bytes_uint16()
    local_dt = dt.as_local(datetime.datetime(2000 + year_month[0], year_month[1], day_hour[0], day_hour[1], minute_second[0], minute_second[1]))
    entry.sensor_value = local_dt  # ready for SensorDeviceClass.TIMESTAMP
    return

@staticmethod
def faultmsg_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update the fault message sensor value."""
    fault_message_list = translate_fault_code_to_messages(int(runtime_data.register_map.FAULT_INFO_RAW))
    entry.sensor_value = ", ".join(fault_message_list)
    return

@staticmethod
def pv_p_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update the total PV power sensor value."""
    entry.sensor_value = runtime_data.register_map.PV1_P + runtime_data.register_map.PV2_P + runtime_data.register_map.PV3_P
    return

@staticmethod
def totalgridbuy_e_data_updated(entry: "SensorEntry_NoSet", runtime_data: "SolArkData") -> None:
    """Update total grid buy energy from discontiguous raw registers."""
    high: int = int(runtime_data.register_map.TOTALGRIDBUY_E_HIGH_RAW)
    low: int = int(runtime_data.register_map.TOTALGRIDBUY_E_LOW_RAW)
    value_int: int = (high << 16) | low
    # We need to handle scale here because of the discontiguous component registers
    scale = 0.1
    value_float: float = value_int * scale
    entry.sensor_value = value_float
    return

@staticmethod
def has_fault_data_updated(entry: "SensorEntry_NoSet[bool]", runtime_data: "SolArkData") -> None:
    """Update the fault-state test sensor value."""
    entry.sensor_value = random.choice([True, False])
    return

class SolArkSensorMap(SensorMap):
    '''Class that declares sensors that need custom code to process other data'''
    # ----------------------------------
    # Post processed sensor definitions
    # ----------------------------------
    FIRMWARE = DiagnosticEntry(key="firmware", name="Firmware Versions", set_sensor_value=firmware_data_updated)
    MPPT_INFO = DiagnosticEntry(key="info_mppt_count", name="MPPT Count", set_sensor_value=info_mppt_count_data_updated)
    PHASE_INFO = DiagnosticEntry(key="info_phase_count", name="Phase Count", set_sensor_value=info_phase_count_data_updated)
    SYSTEM_DATE_TIME = SensorEntry_NoSet(
        key="system_date_time", name="System Date Time", icon="mdi:clock", sensor_class=SensorClass.DATETIME, exclude_from_recorder=True,
        set_sensor_value=system_date_time_data_updated
        )

    # TODO - Add 2 separate sensors or get concensus on changing entiity name(s) to match the SolArk documentation.
    # Caution: this is used by the hub to indicate a communication error with the device.
    # TODO - Another option is to create another entity, with the old one set to be not enabled by default.
    FAULTMSG = SensorEntry_NoSet(
        key="faultmsg", name="Inverter error Message", icon="mdi:message-alert-outline", set_sensor_value=faultmsg_data_updated)

    PV_P = PowerEntry(key="pv_p", name="PV Input Power", icon="mdi:solar-power", set_sensor_value=pv_p_data_updated)
    GEN_RLY = GeneratorRelayEntry(key="gen_rly", name="Generator Relay")
    TOTALGRIDBUY_E = EnergyTotalIncreasingCalculatedEntry(key="totalgridbuy_e", name="Total Grid Buy Energy", set_sensor_value=totalgridbuy_e_data_updated)

    CONFIG_INFO = ConfigEntry(key="config_info", name="Configuration Information")



# TODO - BELOW are all metrics. Move to metrics map and finish
    HAS_FAULT = BinaryProblemEntry(key="has_fault", name="ZZ Has Inverter Fault", set_sensor_value=has_fault_data_updated)
