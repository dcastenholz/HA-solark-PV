import calendar
import datetime
from typing import Iterator

from homeassistant.util import dt

from .const import GEN_RELAY_STATUS, GRID_RELAY_STATUS
from .fault_info import translate_fault_code_to_messages
from .sensor_entity_description import SensorClass
from .sensor_map import SensorMap
from .sensor_map_entry import (
    ConfigEntry,
    EnergyEntry,
    PowerEntry,
    SensorMapEntry,
)
from .solark_register_map import SolArkRegisterMap


class SolArkSensorMap(SensorMap["SolArkSensorMap"]):
    register_map: SolArkRegisterMap

    def __init__(self, register_map: SolArkRegisterMap):
        self.register_map = register_map

    # ----------------------------------
    # Post process methods
    # ----------------------------------
    def post_process(self):
        """Post-process the register map entries after reading the raw values from the inverter."""
        # TODO - Handle case where the dependency registers were not read. Value is None
        for entry in self.entries_post_process:
            entry.post_process(self.register_map)

    @property
    def entries_post_process(self) -> Iterator[SensorMapEntry]:
        """Return all register map entries that have a post_process_method."""
        for entry in self:
            if entry.post_process_method is not None:
                yield entry

    @staticmethod
    def split_uint16(value: int) -> tuple[int, int]:
        """Split a UINT16 into two 8-bit integers (high byte, low byte)."""
        if not 0 <= value <= 0xFFFF:
            raise ValueError("Value must be in range 0..65535 (UINT16)")

        high = (value >> 8) & 0xFF
        low = value & 0xFF
        return high, low

    @staticmethod
    def int_to_month(month_int: int) -> str:
        if 1 <= month_int <= 12:
            return calendar.month_name[month_int]
        raise ValueError("Month must be between 1 and 12")

    @staticmethod
    def inverter_date_time(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        year_month: tuple[int, int] = SolArkSensorMap.split_uint16(int(register_map.SYSTEM_TIME_YM_RAW))
        day_hour: tuple[int, int] = SolArkSensorMap.split_uint16(int(register_map.SYSTEM_TIME_DH_RAW))
        minute_second: tuple[int, int] = SolArkSensorMap.split_uint16(int(register_map.SYSTEM_TIME_MS_RAW))
        local_dt = dt.as_local(datetime.datetime(2000 + year_month[0], year_month[1], day_hour[0], day_hour[1], minute_second[0], minute_second[1]))

        # Convert to UTC
        # utc_dt = dt.as_utc(local_dt)

        entry.register_value = local_dt  # ready for SensorDeviceClass.TIMESTAMP

    @staticmethod
    def inverter_date_time_string(register_map: "SolArkRegisterMap", entry: SensorMapEntry): # pylint: disable=W0613
        return

    @staticmethod
    def value_is_injected(register_map: "SolArkRegisterMap", entry: SensorMapEntry): # pylint: disable=W0613
        # Value is injected into the data dictionary outside of the normal register handling
        return

    @staticmethod
    def fault_code_to_message(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        fault_message_list = translate_fault_code_to_messages(int(register_map.FAULT_INFO_RAW))
        entry.register_value = ", ".join(fault_message_list)

    @staticmethod
    def pv_input_power(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        entry.register_value = register_map.PV1_P + register_map.PV2_P + register_map.PV3_P

    @staticmethod
    def grid_relay_status(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        raw: int = int(register_map.GRID_RLY_RAW)
        entry.register_value = GRID_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"

    @staticmethod
    def gen_relay_status(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        raw: int = int(register_map.GEN_RLY_RAW) & 0x0F  # mask low 4 bits
        entry.register_value = GEN_RELAY_STATUS.get(raw, "Unknown") if raw is not None else "Unknown"

    @staticmethod
    def total_grid_buy(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        high: int = int(register_map.TOTALGRIDBUY_E_HIGH_RAW)
        low: int = int(register_map.TOTALGRIDBUY_E_LOW_RAW)
        value = (high << 16) | low
        # We need to handle scale here because of the discontiguous component registers
        value *= entry.scale
        entry.register_value = value

    @staticmethod
    def firmware_versions(register_map: "SolArkRegisterMap", entry: SensorMapEntry):
        # firmware: str = f"M {get_firmware(int(register_map.FIRMWARE_M.register_value))} / "
        # firmware += f"S {get_firmware(int(register_map.FIRMWARE_S.register_value))} / "
        # firmware += f"C {get_firmware(int(register_map.FIRMWARE_C.register_value))}"
        return

    # ----------------------------------
    # Post processed sensor definitions
    # ----------------------------------
    FIRMWARE = SensorMapEntry(
        key="firmware",
        name="Firmware Versions",
        post_process_method=firmware_versions
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

@staticmethod
def get_mppt_info_string(decimal_number: int) -> str:
    info: tuple[int, int] = get_mppt_info(decimal_number)
    info_string: str = f"{info[0]} MPPTs, {info[1]} phase"
    return info_string

@staticmethod
def get_mppt_info(decimal_number: int) -> tuple[int, int]:
    hex_tuple: tuple[str, ...] = decimal_to_hex_tuple(decimal_number)
    info: tuple[int, int] = combine_decimal_digits(hex_tuple[0], hex_tuple[1]), combine_decimal_digits(hex_tuple[2], hex_tuple[3])
    return info

@staticmethod
def get_firmware(decimal_number: int) -> str:
    hex_tuple: tuple[str, ...] = decimal_to_hex_tuple(decimal_number)
    firmware: str = f"{hex_tuple[0]}.{hex_tuple[1]}.{hex_tuple[2]}.{hex_tuple[3]}"
    return firmware

@staticmethod
def decimal_to_hex_tuple(decimal_number: int) -> tuple[str, ...]:
    # Convert to hex without the '0x' prefix and make uppercase
    hex_str = hex(decimal_number)[2:].upper()
    # Create a tuple with each hex digit as a string
    return tuple(hex_str)

@staticmethod
def combine_decimal_digits(a: int, b: int) -> int:
    return a * 10 + b
