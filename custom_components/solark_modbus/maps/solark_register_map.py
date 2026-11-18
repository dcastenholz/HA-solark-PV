"""Register map for SolArk."""

from typing import TypeVar

from homeassistant.components.sensor import (
    EntityCategory,
)

from .._sensor.sensor_entity_description import NativeUnit
from ..entry_map.register_entry import (
    BatteryCurrentEntry,
    BatteryVoltageEntry,
    CurrentEntry,
    DataType,
    EnergyEntry,
    EnergyTotalIncreasingEntry,
    FrequencyEntry,
    GridRelayEntry,
    GridVoltageEntry,
    PowerEntry,
    PVVoltageEntry,
    RawInfoEntry,
    RawValueEntry,
    RawValueSystemTimeEntry,
    RegisterIntEntry,
    SerialNumberEntry,
    SOCEntry,
    TemperatureEntry,
    TimeOfUse_ChargeSellEntry,
    TimeOfUse_TimeEntry,
)
from ..entry_map.register_map import RegisterMap

T = TypeVar("T", bound="RegisterMap")  # T is the real subclass


class SolArkRegisterMap(RegisterMap):
    """Declare the Modbus register map."""

    SN = SerialNumberEntry(address=3, length=5, key="sn", name="Serial Number", icon="mdi:information-outline")
    INFO_FIRMWARE_S = RawInfoEntry(address=11, key="info_firmware_s", name="Firmware S", icon="mdi:information-outline")
    INFO_FIRMWARE_M = RawInfoEntry(address=13, key="info_firmware_m", name="Firmware Control Board", icon="mdi:information-outline")
    INFO_FIRMWARE_C = RawInfoEntry(address=14, key="info_firmware_c", name="Firmware Communication Board", icon="mdi:information-outline")
    INFO_RATED_POWER = PowerEntry(
        address=16,
        key="info_rated_power",
        scale=0.1,
        name="Rated Power",
        icon="mdi:solar-power",
        data_type=DataType.UINT32,
        entity_category=EntityCategory.DIAGNOSTIC,
    )
    INFO_MPPT_PHASE_COUNTS_RAW = RawInfoEntry(address=18, key="info_mppt_phase_raw", name="MPPT & Phase")

    SYSTEM_TIME_YM_RAW = RawValueSystemTimeEntry(address=22, key="system_time_ym_raw", name="System Time Year Month")
    SYSTEM_TIME_DH_RAW = RawValueSystemTimeEntry(address=23, key="system_time_DH_raw", name="System Time Day Hour")
    SYSTEM_TIME_MS_RAW = RawValueSystemTimeEntry(address=24, key="system_time_ms_raw", name="System Time Minute Second")

    DAILYINV_E = EnergyEntry(address=60, key="dailyinv_e", name="Daily Inverter Energy", data_type=DataType.INT16)
    #    DAILYREA_E = EnergyEntry(address=61, key="dailyrea_e", name="Daily Reactive Energy", data_type=DataType.INT16)
    # TODO - The keys for some registers are very misleading. Review and rename, handling history.
    TOTALGRID_E = EnergyEntry(address=63, key="totalgrid_e", name="Total Inverter Energy", data_type=DataType.INT32)
    DAILYBATT_C_E = EnergyTotalIncreasingEntry(address=70, key="daybattc_e", name="Daily Battery Charge Energy", data_type=DataType.UINT16)
    DAILYBATT_D_E = EnergyTotalIncreasingEntry(
        address=71, key="daybattd_e", name="Daily Battery Discharge Energy", data_type=DataType.UINT16
    )
    TOTALBATT_C_E = EnergyTotalIncreasingEntry(
        address=72, key="totalbattc_e", name="Total Battery Charge Energy", data_type=DataType.UINT32
    )
    TOTALBATT_D_E = EnergyTotalIncreasingEntry(
        address=74, key="totalbattd_e", name="Total Battery Discharge Energy", data_type=DataType.UINT32
    )
    DAILYGRIDBUY_E = EnergyTotalIncreasingEntry(address=76, key="dailygridbuy_e", name="Daily Grid Buy Energy", data_type=DataType.UINT16)
    DAILYGRIDSELL_E = EnergyTotalIncreasingEntry(
        address=77, key="dailygridsell_e", name="Daily Grid Sell Energy", data_type=DataType.UINT16
    )
    TOTALGRIDBUY_E_LOW_RAW = RawValueEntry(
        address=78, key="totalgridbuy_e_low", name="Total Grid Buy Energy - low word", data_type=DataType.UINT16
    )
    GRIDFREQ = FrequencyEntry(address=79, key="gridfreq", name="Grid Frequency")
    TOTALGRIDBUY_E_HIGH_RAW = RawValueEntry(
        address=80, key="totalgridbuy_e_high", name="Total Grid Buy Energy - high word", data_type=DataType.UINT16
    )
    TOTALGRIDSELL_E = EnergyTotalIncreasingEntry(address=81, key="totalsell_e", name="Total Grid Sell Energy", data_type=DataType.UINT32)
    DAILYLOAD_E = EnergyTotalIncreasingEntry(address=84, key="dailyload_e", name="Daily Load Energy", data_type=DataType.UINT16)
    TOTALLOAD_E = EnergyTotalIncreasingEntry(address=85, key="totalload_e", name="Total Load Energy", data_type=DataType.UINT32)
    DCHSTempC = TemperatureEntry(address=90, key="dchstempc", name="DC Heatsink Temperature")
    ACHSTempC = TemperatureEntry(address=91, key="achstempc", name="AC Heatsink Temperature")
    # TODO - The keys for some registers are very misleading. Review and rename, handling history.
    TOTALINV_E = EnergyEntry(address=96, key="totalinv_e", name="Total PV Energy", data_type=DataType.INT32)
    FAULT_INFO_RAW = RawInfoEntry(
        address=103, key="fault_info_raw", name="Inverter Fault Information", data_type=DataType.UINT64, icon="mdi:message-alert-outline"
    )
    CORR_BATT_CAP = RegisterIntEntry(
        address=107,
        key="corr_batt_cap",
        name="Corrected Battery Capacity",
        data_type=DataType.UINT16,
        icon="mdi:battery",
        native_unit=NativeUnit.AH,
        state_class=None,
    )
    DAILYPV_E = EnergyTotalIncreasingEntry(address=108, key="dailypv_e", name="Daily PV Energy", data_type=DataType.UINT16)

    PV1_V = PVVoltageEntry(address=109, key="pv1_v", name="PV1 Voltage")
    PV1_C = CurrentEntry(address=110, key="pv1_c", name="PV1 Current")
    PV2_V = PVVoltageEntry(address=111, key="pv2_v", name="PV2 Voltage")
    PV2_C = CurrentEntry(address=112, key="pv2_c", name="PV2 Current")
    PV3_V = PVVoltageEntry(address=113, key="pv3_v", name="PV3 Voltage")
    PV3_C = CurrentEntry(address=114, key="pv3_c", name="PV3 Current")

    GRIDL1N_V = GridVoltageEntry(address=150, key="gridl1n_v", name="Grid L1-N Voltage")
    GRIDL2N_V = GridVoltageEntry(address=151, key="gridl2n_v", name="Grid L2-N Voltage")
    GRIDL1L2_V = GridVoltageEntry(address=152, key="gridl1l2_v", name="Grid L1-L2 Voltage")
    GRIDRELAY_V = GridVoltageEntry(address=153, key="gridrelay_v", name="Grid Relay Voltage")
    INVL1N_V = GridVoltageEntry(address=154, key="invl1n_v", name="Inverter L1-N Voltage")
    INVL2N_V = GridVoltageEntry(address=155, key="invl2n_v", name="Inverter L2-N Voltage")
    INVL1L2_V = GridVoltageEntry(address=156, key="invl1l2_v", name="Inverter L1-L2 Voltage")
    LOADL1_V = GridVoltageEntry(address=157, key="loadl1n_v", name="Load L1-N Voltage")
    LOADL2_V = GridVoltageEntry(address=158, key="loadl2n_v", name="Load L2-N Voltage")

    GRIDL1_C = CurrentEntry(address=160, key="gridl1_c", name="Grid L1 Current", icon="mdi:current-ac")
    GRIDL2_C = CurrentEntry(address=161, key="gridl2_c", name="Grid L2 Current", icon="mdi:current-ac")
    EXTLMTL1_C = CurrentEntry(address=162, key="extlmtl1_c", name="External Lmt L1 Current", icon="mdi:current-ac")
    EXTLMTL2_C = CurrentEntry(address=163, key="extlmtl2_c", name="External Lmt L2 Current", icon="mdi:current-ac")
    INVL1_C = CurrentEntry(address=164, key="invl1_c", name="Inverter L1 Current", icon="mdi:current-ac")
    INVL2_C = CurrentEntry(address=165, key="invl2_c", name="Inverter L2 Current", icon="mdi:current-ac")

    GEN_P = PowerEntry(address=166, key="gen_p", name="Gen Power", icon="mdi:solar-power")
    GRIDL1_P = PowerEntry(address=167, key="gridl1_p", name="Grid L1 Power", icon="mdi:solar-power")
    GRIDL2_P = PowerEntry(address=168, key="gridl2_p", name="Grid L2 Power", icon="mdi:solar-power")
    GRID_P = PowerEntry(address=169, key="grid_p", name="Grid Power", icon="mdi:solar-power")
    GRIDLMTL1_P = PowerEntry(address=170, key="gridlmtl1_p", name="Grid Limiter L1 Power", icon="mdi:solar-power")
    GRIDLMTL2_P = PowerEntry(address=171, key="gridlmtl2_p", name="Grid Limiter L2 Power", icon="mdi:solar-power")
    GRIDEXT_P = PowerEntry(address=172, key="gridext_p", name="Grid External Total Power", icon="mdi:solar-power")
    INVL1_P = PowerEntry(address=173, key="invl1_p", name="Inverter L1 Power", icon="mdi:solar-power")
    INVL2_P = PowerEntry(address=174, key="invl2_p", name="Inverter L2 Power", icon="mdi:solar-power")
    INV_P = PowerEntry(address=175, key="inv_p", name="Inverter Power", icon="mdi:solar-power")
    LOADL1_P = PowerEntry(address=176, key="loadl1_p", name="Load L1 Power", icon="mdi:solar-power")
    LOADL2_P = PowerEntry(address=177, key="loadl2_p", name="Load L2 Power", icon="mdi:solar-power")
    LOAD_P = PowerEntry(address=178, key="load_p", name="Load Power", icon="mdi:solar-power")

    LOADL1_C = CurrentEntry(address=179, key="loadl1_c", name="Load L1 Current", icon="mdi:current-ac")
    LOADL2_C = CurrentEntry(address=180, key="loadl2_c", name="Load L2 Current", icon="mdi:current-ac")

    GENL1L2_V = GridVoltageEntry(address=181, key="genl1l2_v", name="Generator L1-L2 Voltage")
    BATTTEMP_C = TemperatureEntry(address=182, key="batttempc", name="Battery Temperature")
    BATT_V = BatteryVoltageEntry(address=183, key="batt_v", name="Battery Voltage")
    BATT_SOC = SOCEntry(address=184, key="batt_soc", name="Battery State of Charge")

    PV1_P = PowerEntry(address=186, key="pv1_p", name="PV1 Input Power", icon="mdi:solar-power", data_type=DataType.UINT16)
    PV2_P = PowerEntry(address=187, key="pv2_p", name="PV2 Input Power", icon="mdi:solar-power", data_type=DataType.UINT16)
    PV3_P = PowerEntry(address=188, key="pv3_p", name="PV3 Input Power", icon="mdi:solar-power", data_type=DataType.UINT16)

    BATT_P = PowerEntry(address=190, key="batt_p", name="Battery Power", icon="mdi:solar-power", data_type=DataType.INT16)
    BATT_C = CurrentEntry(address=191, key="batt_c", name="Battery Current", icon="mdi:current-dc", data_type=DataType.INT16)

    LOAD_FREQ = FrequencyEntry(address=192, key="loadfreq", name="Load Frequency")
    INVERTER_FREQ = FrequencyEntry(address=193, key="inverterfreq", name="Inverter Output Frequency")

    GRID_RLY = GridRelayEntry(address=194, key="grid_rly", name="Grid Relay")
    GEN_RLY_RAW = RawValueEntry(address=195, key="gen_relay_status_raw", name="Generator Relay Status")

    GEN_FREQ = FrequencyEntry(address=196, key="genfreq", name="Generator Relay Frequency")

    BATT_MEASURE_MODE_RAW = RawValueEntry(
        address=213, key="batt_measure_mode_raw", name="Battery Measurement Mode Raw Value", data_type=DataType.UINT16
    )
    BATT_CHARGE_CURRENT_LIMIT = BatteryCurrentEntry(
        address=230, key="battery_charge_current_limit", name="Battery Charge Current Limit", data_type=DataType.UINT16
    )

    # ----------------------------
    # Time of use
    # ----------------------------
    TIMEOFUSE_ENABLED_RAW = RawValueEntry(
        address=248, key="timeofuse_enabled_raw", name="Time of Use Enabled Raw Value", data_type=DataType.UINT16
    )

    TIMEOFUSE_1_TIME = TimeOfUse_TimeEntry(address=250, key="timeofuse_1_time", name="Time of Use 1 Time")
    TIMEOFUSE_2_TIME = TimeOfUse_TimeEntry(address=251, key="timeofuse_2_time", name="Time of Use 2 Time")
    TIMEOFUSE_3_TIME = TimeOfUse_TimeEntry(address=252, key="timeofuse_3_time", name="Time of Use 3 Time")
    TIMEOFUSE_4_TIME = TimeOfUse_TimeEntry(address=253, key="timeofuse_4_time", name="Time of Use 4 Time")
    TIMEOFUSE_5_TIME = TimeOfUse_TimeEntry(address=254, key="timeofuse_5_time", name="Time of Use 5 Time")
    TIMEOFUSE_6_TIME = TimeOfUse_TimeEntry(address=255, key="timeofuse_6_time", name="Time of Use 6 Time")

    TIMEOFUSE_1_POWER = PowerEntry(address=256, key="timeofuse_1_power", name="Time of Use 1 Power", data_type=DataType.UINT16)
    TIMEOFUSE_2_POWER = PowerEntry(address=257, key="timeofuse_2_power", name="Time of Use 2 Power", data_type=DataType.UINT16)
    TIMEOFUSE_3_POWER = PowerEntry(address=258, key="timeofuse_3_power", name="Time of Use 3 Power", data_type=DataType.UINT16)
    TIMEOFUSE_4_POWER = PowerEntry(address=259, key="timeofuse_4_power", name="Time of Use 4 Power", data_type=DataType.UINT16)
    TIMEOFUSE_5_POWER = PowerEntry(address=260, key="timeofuse_5_power", name="Time of Use 5 Power", data_type=DataType.UINT16)
    TIMEOFUSE_6_POWER = PowerEntry(address=261, key="timeofuse_6_power", name="Time of Use 6 Power", data_type=DataType.UINT16)

    TIMEOFUSE_1_VOLTAGE = BatteryVoltageEntry(address=262, key="timeofuse_1_voltage", name="Time of Use 1 Voltage")
    TIMEOFUSE_2_VOLTAGE = BatteryVoltageEntry(address=263, key="timeofuse_2_voltage", name="Time of Use 2 Voltage")
    TIMEOFUSE_3_VOLTAGE = BatteryVoltageEntry(address=264, key="timeofuse_3_voltage", name="Time of Use 3 Voltage")
    TIMEOFUSE_4_VOLTAGE = BatteryVoltageEntry(address=265, key="timeofuse_4_voltage", name="Time of Use 4 Voltage")
    TIMEOFUSE_5_VOLTAGE = BatteryVoltageEntry(address=266, key="timeofuse_5_voltage", name="Time of Use 5 Voltage")
    TIMEOFUSE_6_VOLTAGE = BatteryVoltageEntry(address=267, key="timeofuse_6_voltage", name="Time of Use 6 Voltage")

    TIMEOFUSE_1_SOC = SOCEntry(address=268, key="timeofuse_1_soc", name="Time of Use 1 SOC")
    TIMEOFUSE_2_SOC = SOCEntry(address=269, key="timeofuse_2_soc", name="Time of Use 2 SOC")
    TIMEOFUSE_3_SOC = SOCEntry(address=270, key="timeofuse_3_soc", name="Time of Use 3 SOC")
    TIMEOFUSE_4_SOC = SOCEntry(address=271, key="timeofuse_4_soc", name="Time of Use 4 SOC")
    TIMEOFUSE_5_SOC = SOCEntry(address=272, key="timeofuse_5_soc", name="Time of Use 5 SOC")
    TIMEOFUSE_6_SOC = SOCEntry(address=273, key="timeofuse_6_soc", name="Time of Use 6 SOC")

    TIMEOFUSE_1_CHARGE_SELL = TimeOfUse_ChargeSellEntry(address=274, key="timeofuse_1_charge_sell", name="Time of Use 1 Charge/Sell")
    TIMEOFUSE_2_CHARGE_SELL = TimeOfUse_ChargeSellEntry(address=275, key="timeofuse_2_charge_sell", name="Time of Use 2 Charge/Sell")
    TIMEOFUSE_3_CHARGE_SELL = TimeOfUse_ChargeSellEntry(address=276, key="timeofuse_3_charge_sell", name="Time of Use 3 Charge/Sell")
    TIMEOFUSE_4_CHARGE_SELL = TimeOfUse_ChargeSellEntry(address=277, key="timeofuse_4_charge_sell", name="Time of Use 4 Charge/Sell")
    TIMEOFUSE_5_CHARGE_SELL = TimeOfUse_ChargeSellEntry(address=278, key="timeofuse_5_charge_sell", name="Time of Use 5 Charge/Sell")
    TIMEOFUSE_6_CHARGE_SELL = TimeOfUse_ChargeSellEntry(address=279, key="timeofuse_6_charge_sell", name="Time of Use 6 Charge/Sell")

    # ----------------------------
    # BMS
    # ----------------------------
    BMS_CHARGING_VOLTAGE = BatteryVoltageEntry(address=312, key="bms_charging_voltage", name="BMS Charging Voltage")
    BMS_DISCHARGE_VOLTAGE = BatteryVoltageEntry(address=313, key="bms_discharge_voltage", name="BMS Discharge Voltage")
    BMS_CHARGE_CURRENT_LIMIT = BatteryCurrentEntry(address=314, key="bms_charge_current_limit", name="BMS Charge Current Limit")
    BMS_DISCHARGE_CURRENT_LIMIT = BatteryCurrentEntry(address=315, key="bms_discharge_current_limit", name="BMS Discharge Current Limit")
    BMS_SOC = SOCEntry(address=316, key="bms_soc", name="BMS SOC")
    BMS_VOLTAGE = BatteryVoltageEntry(address=317, key="bms_voltage", name="BMS Voltage")
    BMS_CURRENT = BatteryCurrentEntry(address=318, key="bms_current", data_type=DataType.INT16, name="BMS Current")
    BMS_TEMP = TemperatureEntry(address=319, key="bms_temp", name="BMS Temperature")
    # TODO - Add 320-325
