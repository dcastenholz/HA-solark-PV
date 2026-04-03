import calendar
import datetime
from typing import TYPE_CHECKING

from homeassistant.util import dt

from .const import GEN_RELAY_STATUS, GRID_RELAY_STATUS
from .fault_info import translate_fault_code_to_messages
from .sensor_entity_description import SensorClass
from .sensor_map import SensorMap
from .sensor_map_entry import (
    ConfigEntry,
    DiagnosticEntry,
    EnergyEntry,
    PowerEntry,
    SensorMapEntry,
)
from .solark_register_map import SolArkRegisterMap

if TYPE_CHECKING:
    from .data import SolArkData


# @staticmethod
# def split_uint16(value: int) -> tuple[int, int]:
#     """Split a UINT16 into two 8-bit integers (high byte, low byte)."""
#     if not 0 <= value <= 0xFFFF:
#         raise ValueError("Value must be in range 0..65535 (UINT16)")

#     high = (value >> 8) & 0xFF
#     low = value & 0xFF
#     return high, low

@staticmethod
def inverter_date_time(runtime_data: SolArkData, entry: SensorMapEntry):
    register_map: SolArkRegisterMap = runtime_data.register_map
    year_month: tuple[int, int] = register_map.SYSTEM_TIME_YM_RAW.split_bytes_uint16()
    day_hour: tuple[int, int] = register_map.SYSTEM_TIME_DH_RAW.split_bytes_uint16()
    minute_second: tuple[int, int] = register_map.SYSTEM_TIME_MS_RAW.split_bytes_uint16()
    local_dt = dt.as_local(datetime.datetime(2000 + year_month[0], year_month[1], day_hour[0], day_hour[1], minute_second[0], minute_second[1]))

    # Convert to UTC
    # utc_dt = dt.as_utc(local_dt)

    entry.register_value = local_dt  # ready for SensorDeviceClass.TIMESTAMP

@staticmethod
def value_is_injected(runtime_data: SolArkData, entry: SensorMapEntry): # pylint: disable=W0613
    # Value is injected into the data dictionary outside of the normal register handling
    return

@staticmethod
def fault_code_to_message(runtime_data: SolArkData, entry: SensorMapEntry):
    fault_message_list = translate_fault_code_to_messages(int(runtime_data.register_map.FAULT_INFO_RAW))
    entry.register_value = ", ".join(fault_message_list)

@staticmethod
def pv_input_power(runtime_data: SolArkData, entry: SensorMapEntry):
    entry.register_value = runtime_data.register_map.PV1_P + runtime_data.register_map.PV2_P + runtime_data.register_map.PV3_P

@staticmethod
def grid_relay_status(runtime_data: SolArkData, entry: SensorMapEntry):
    raw: int = int(runtime_data.register_map.GRID_RLY_RAW)
    entry.register_value = GRID_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"

@staticmethod
def gen_relay_status(runtime_data: SolArkData, entry: SensorMapEntry):
    raw: int = int(runtime_data.register_map.GEN_RLY_RAW) & 0x0F  # mask low 4 bits
    entry.register_value = GEN_RELAY_STATUS.get(raw, "Unknown") if raw is not None else "Unknown"

@staticmethod
def total_grid_buy(runtime_data: SolArkData, entry: SensorMapEntry):
    high: int = int(runtime_data.register_map.TOTALGRIDBUY_E_HIGH_RAW)
    low: int = int(runtime_data.register_map.TOTALGRIDBUY_E_LOW_RAW)
    value = (high << 16) | low
    # We need to handle scale here because of the discontiguous component registers
    value *= entry.scale
    entry.register_value = value

@staticmethod
def firmware_versions(runtime_data: SolArkData, entry: SensorMapEntry):
    firmware: str = f"M {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_M))} / "
    firmware += f"S {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_S))} / "
    firmware += f"C {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_C))}"
    entry.register_value = firmware
    return

@staticmethod
def mppt_count(runtime_data: SolArkData, entry: SensorMapEntry):
    info: tuple[int, int] = get_mppt_phase_info(int(runtime_data.register_map.INFO_MPPT_PHASE_COUNTS_RAW))
    entry.register_value = f"{plural(info[0], 'MPPT')}"
    return

@staticmethod
def phase_count(runtime_data: SolArkData, entry: SensorMapEntry):
    info: tuple[int, int] = get_mppt_phase_info(int(runtime_data.register_map.INFO_MPPT_PHASE_COUNTS_RAW))
    entry.register_value = f"{plural(info[1], 'phase')}"
    return

# ----------------------------
# Helpers
# ----------------------------
@staticmethod
def int_to_month(month_int: int) -> str:
    if 1 <= month_int <= 12:
        return calendar.month_name[month_int]
    raise ValueError("Month must be between 1 and 12")

@staticmethod
def get_mppt_phase_info(decimal_number: int) -> tuple[int, int]:
    hex_tuple: tuple[str, str, str, str] = decimal_to_hex_tuple(decimal_number)
    info: tuple[int, int] = combine_decimal_digits(hex_tuple[0], hex_tuple[1]), combine_decimal_digits(hex_tuple[2], hex_tuple[3])
    return info

@staticmethod
def get_firmware(decimal_number: int) -> str:
    hex_tuple: tuple[str, ...] = decimal_to_hex_tuple(decimal_number)
    firmware: str = f"{hex_tuple[0]}.{hex_tuple[1]}.{hex_tuple[2]}.{hex_tuple[3]}"
    return firmware

@staticmethod
def decimal_to_hex_tuple(decimal_number: int) -> tuple[str, str, str, str]:
    # Convert to hex without the '0x' prefix and make uppercase
    hex_str = f"{decimal_number:04X}"
    # Create a tuple with each hex digit as a string
    return hex_str[0], hex_str[1], hex_str[2], hex_str[3]

@staticmethod
def combine_decimal_digits(a: int, b: int) -> int:
    return int(a) * 10 + int(b)

@staticmethod
def plural(value: int, word: str) -> str:
    return f"{value} {word}{'' if value == 1 else 's'}"


class SolArkSensorMap(SensorMap):

    # ----------------------------------
    # Post processed sensor definitions
    # ----------------------------------
    FIRMWARE = DiagnosticEntry(
        key="firmware",
        name="Firmware Versions",
        post_process_method=firmware_versions
    )

    MPPT_INFO = DiagnosticEntry(
        key="info_mppt_count",
        name="MPPT Count",
        post_process_method=mppt_count
    )

    PHASE_INFO = DiagnosticEntry(
        key="info_phase_count",
        name="Phase Count",
        post_process_method=phase_count
    )

    SYSTEM_DATE_TIME = SensorMapEntry(
        key="system_date_time",
        name="System Date Time",
        icon="mdi:clock",
        sensor_class=SensorClass.DATETIME,
        exclude_from_recorder=True,
        post_process_method=inverter_date_time,
    )

    FAULTMSG = SensorMapEntry(
        key="faultmsg",
        #data_type=DataType.STRING,
        name="Inverter error Message",
        # name="Inverter Fault Message", # TODO - get concensus on changing entiity name(s) to match the SolArk documentation.
        # Caution: this is used by the hub to indicate a communication error with the device.
        # TODO - Another option is to create another entity, with the old one set to be not enabled by default.
        icon="mdi:message-alert-outline",
        post_process_method=fault_code_to_message,
        entity_registry_enabled_default=True,
    )
    PV_P = PowerEntry(
        key="pv_p",
        name="PV Input Power",
        icon="mdi:solar-power",
        post_process_method=pv_input_power,
        entity_registry_enabled_default=True,
    )
    GRID_RLY = SensorMapEntry(
        key="grid_rly",
        name="Grid Relay",
        icon="mdi:electric-switch",
        post_process_method=grid_relay_status,
    )
    GEN_RLY = SensorMapEntry(
        key="gen_rly",
        name="Generator Relay",
        icon="mdi:electric-switch",
        post_process_method=gen_relay_status,
    )
    TOTALGRIDBUY_E = EnergyEntry(
        key="totalgridbuy_e",
        name="Total Grid Buy Energy",
        post_process_method=total_grid_buy,
    )

    UPDATE_COUNTER = SensorMapEntry(
        key="update_cnt",
        name="Update Counter",
        icon="mdi:information-outline",
        post_process_method=value_is_injected,
    )

    CONFIG_INFO = ConfigEntry(
        key="config_info",
        name="Configuration Information",
        post_process_method=value_is_injected
    )
