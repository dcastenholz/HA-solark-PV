import calendar
import datetime
from typing import TYPE_CHECKING

from homeassistant.components.sensor import EntityCategory, SensorStateClass
from homeassistant.util import dt

from .config_sensor import ConfigSensor
from .const import GEN_RELAY_STATUS, GRID_RELAY_STATUS
from .fault_info import translate_fault_code_to_messages
from .sensor_class import SensorClass
from .sensor_dynamic_icon import SensorDynamicIcon
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
    from .sensor import SolArkBaseSensor

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


# ----------------------------------
# Post processed sensor method definitions
# ----------------------------------
@staticmethod
def firmware_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    firmware: str = f"M {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_M))} / "
    firmware += f"S {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_S))} / "
    firmware += f"C {get_firmware(int(runtime_data.register_map.INFO_FIRMWARE_C))}"
    self.register_value = firmware
    return

@staticmethod
def info_mppt_count_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    info: tuple[int, int] = get_mppt_phase_info(int(runtime_data.register_map.INFO_MPPT_PHASE_COUNTS_RAW))
    self.register_value = f"{plural(info[0], 'MPPT')}"
    return

@staticmethod
def info_phase_count_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    info: tuple[int, int] = get_mppt_phase_info(int(runtime_data.register_map.INFO_MPPT_PHASE_COUNTS_RAW))
    self.register_value = f"{plural(info[1], 'phase')}"
    return

@staticmethod
def system_date_time_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    register_map: SolArkRegisterMap = runtime_data.register_map
    year_month: tuple[int, int] = register_map.SYSTEM_TIME_YM_RAW.split_bytes_uint16()
    day_hour: tuple[int, int] = register_map.SYSTEM_TIME_DH_RAW.split_bytes_uint16()
    minute_second: tuple[int, int] = register_map.SYSTEM_TIME_MS_RAW.split_bytes_uint16()
    local_dt = dt.as_local(datetime.datetime(2000 + year_month[0], year_month[1], day_hour[0], day_hour[1], minute_second[0], minute_second[1]))
    self.register_value = local_dt  # ready for SensorDeviceClass.TIMESTAMP
    return

@staticmethod
def faultmsg_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    fault_message_list = translate_fault_code_to_messages(int(runtime_data.register_map.FAULT_INFO_RAW))
    self.register_value = ", ".join(fault_message_list)
    return

@staticmethod
def pv_p_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    self.register_value = runtime_data.register_map.PV1_P + runtime_data.register_map.PV2_P + runtime_data.register_map.PV3_P
    return

@staticmethod
def grid_rly_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    raw: int = int(runtime_data.register_map.GRID_RLY_RAW)
    self.register_value = GRID_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"
    return

@staticmethod
def gen_rly_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    raw: int = int(runtime_data.register_map.GEN_RLY_RAW) & 0x0F  # mask low 4 bits
    self.register_value = GEN_RELAY_STATUS.get(raw, "Unknown") if raw is not None else "Unknown"
    return

@staticmethod
def totalgridbuy_e_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    high: int = int(runtime_data.register_map.TOTALGRIDBUY_E_HIGH_RAW)
    low: int = int(runtime_data.register_map.TOTALGRIDBUY_E_LOW_RAW)
    value = (high << 16) | low
    # We need to handle scale here because of the discontiguous component registers
    value *= self.scale
    self.register_value = value
    return

@staticmethod
def update_count_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    import warnings
    warnings.warn(
        "update_cnt is deprecated, use update_count",
        DeprecationWarning,
        stacklevel=2,
    )
    self.register_value = runtime_data.coordinator_metrics.update_count & 0xFFFF
    return

@staticmethod
def update_cnt_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    self.register_value = runtime_data.coordinator_metrics.update_count
    return

@staticmethod
def config_info_post_process(self: "SensorMapEntry", runtime_data: "SolArkData") -> None:
    self.register_value = runtime_data.name
    return

@staticmethod
def config_info_post_process_sensor(sensor: "SolArkBaseSensor", runtime_data: "SolArkData") -> None:
    sensor.extra_state_attributes = ConfigSensor.get_data(runtime_data.config_entry)
    return

class SolArkSensorMap(SensorMap):

    # ----------------------------------
    # Post processed sensor definitions
    # ----------------------------------
    FIRMWARE = DiagnosticEntry(key="firmware", name="Firmware Versions", post_process=firmware_post_process)
    MPPT_INFO = DiagnosticEntry(key="info_mppt_count", name="MPPT Count", post_process=info_mppt_count_post_process)
    PHASE_INFO = DiagnosticEntry(key="info_phase_count", name="Phase Count", post_process=info_phase_count_post_process)
    SYSTEM_DATE_TIME = SensorMapEntry(
        key="system_date_time", name="System Date Time", icon="mdi:clock", sensor_class=SensorClass.DATETIME, exclude_from_recorder=True,
        post_process=system_date_time_post_process
        )

    # TODO - get concensus on changing entiity name(s) to match the SolArk documentation.
    # Caution: this is used by the hub to indicate a communication error with the device.
    # TODO - Another option is to create another entity, with the old one set to be not enabled by default.
    FAULTMSG = SensorMapEntry(
        key="faultmsg", name="Inverter error Message", icon="mdi:message-alert-outline", entity_registry_enabled_default=True,
        post_process=faultmsg_post_process
        )

    PV_P = PowerEntry(
        key="pv_p", name="PV Input Power", icon="mdi:solar-power", entity_registry_enabled_default=True, post_process=pv_p_post_process
        )
    GRID_RLY = SensorMapEntry(key="grid_rly", name="Grid Relay", icon="mdi:electric-switch", post_process=grid_rly_post_process, dynamic_icon=SensorDynamicIcon.RELAY)
    GEN_RLY = SensorMapEntry(key="gen_rly", name="Generator Relay", icon="mdi:electric-switch", post_process=gen_rly_post_process, dynamic_icon=SensorDynamicIcon.GENERATOR_RELAY)
    TOTALGRIDBUY_E = EnergyEntry(key="totalgridbuy_e", name="Total Grid Buy Energy", post_process=totalgridbuy_e_post_process)

    UPDATE_COUNTER = SensorMapEntry(
        key="update_count", name="Update Count", icon="mdi:information-outline", state_class=SensorStateClass.TOTAL,
        post_process=update_count_post_process
        )

    '''For backwards compatibility.
    New underlying count property will not roll over under normal conditions.
    This will prevent the appearance of a restart, when in fact, the counter has just rolled over.'''
    UPDATE_CNT = SensorMapEntry(
        key="update_cnt", name="Update Count - 16 bit rollover", icon="mdi:information-outline", state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=False, entity_category = EntityCategory.DIAGNOSTIC, post_process=update_cnt_post_process
        )

    CONFIG_INFO = ConfigEntry(
        key="config_info", name="Configuration Information", exclude_from_recorder=True, post_process=config_info_post_process,
        post_process_sensor=config_info_post_process_sensor, should_poll=False
        )
