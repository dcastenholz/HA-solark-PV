"""SolArk Modbus Register Map."""

from typing import TypeVar

from homeassistant.const import EntityCategory

from .const import GEN_RELAY_STATUS, GRID_RELAY_STATUS
from .fault_info import translate_fault_code_to_messages
from .register_map import DIAGNOSTIC, DataType, DeviceClass, NativeUnit, RegisterMap, RegisterMapEntry, SensorClass, StateClass

T = TypeVar("T", bound="RegisterMap")  # T is the real subclass

"""SolArk Modbus Register Map class"""


class SolArkRegisterMap(RegisterMap["SolArkRegisterMap"]):
    SN = RegisterMapEntry(
        address=3,
        string_register_length=5,
        key="sn",
        data_type=DataType.STRING,
        name="Serial Number",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )

    FIRMWARE_S = RegisterMapEntry(
        address=11,
        key="firmware_s",
        data_type=DataType.INT16,
        name="Firmware S Raw",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )
    FIRMWARE_M = RegisterMapEntry(
        address=13,
        key="firmware_m",
        data_type=DataType.INT16,
        name="Firmware Control Board Raw",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )
    FIRMWARE_C = RegisterMapEntry(
        address=14,
        key="firmware_c",
        data_type=DataType.INT16,
        name="Firmware Communication Board Raw",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )

    RATED_POWER = RegisterMapEntry(
        address=16,
        key="rated_power",
        data_type=DataType.INT32,
        scale=0.1,
        name="Rated Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        entity_registry_enabled_default=False,
    )

    MPPT_INFO_RAW = RegisterMapEntry(
        address=18,
        key="mppt_info_raw",
        data_type=DataType.INT16,
        name="MPPT Info Raw Value",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )

    SYSTEM_TIME_YM_RAW = RegisterMapEntry(
        address=22,
        key="system_time_ym_raw",
        data_type=DataType.INT16,
        name="System Time Year Month Raw Value",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )
    SYSTEM_TIME_DH_RAW = RegisterMapEntry(
        address=23,
        key="system_time_DH_raw",
        data_type=DataType.INT16,
        name="System Time Day Hour Raw Value",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )
    SYSTEM_TIME_MS_RAW = RegisterMapEntry(
        address=24,
        key="system_time_ms_raw",
        data_type=DataType.INT16,
        name="System Time Minute Second Raw Value",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    )




    DAILYINV_E = RegisterMapEntry(
        address=60,
        key="dailyinv_e",
        data_type=DataType.INT16,
        scale=0.1,
        name="Daily Inverter Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    TOTALGRID_E = RegisterMapEntry(
        address=63,
        key="totalgrid_e",
        data_type=DataType.INT32,
        scale=0.1,
        name="Total Grid Breaker Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    DAILYBATT_C_E = RegisterMapEntry(
        address=70,
        key="daybattc_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Battery Charge Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    DAILYBATT_D_E = RegisterMapEntry(
        address=71,
        key="daybattd_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Battery Discharge Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )

    # NEW ------------------------------------------------
    TOTALBATT_C_E = RegisterMapEntry(
        address=72,
        key="totalbattc_e",
        data_type=DataType.UINT32,
        scale=0.1,
        name="Total Battery Charge Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    TOTALBATT_D_E = RegisterMapEntry(
        address=74,
        key="totalbattd_e",
        data_type=DataType.UINT32,
        scale=0.1,
        name="Total Battery Discharge Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    # END ------------------------------------------------

    DAILYGRIDBUY_E = RegisterMapEntry(
        address=76,
        key="dailygridbuy_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Grid Buy Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    DAILYGRIDSELL_E = RegisterMapEntry(
        address=77,
        key="dailygridsell_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Grid Sell Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )

    # NEW ------------------------------------------------
    TOTALGRIDBUY_E_LOW_RAW = RegisterMapEntry(
        address=78,
        key="totalgridbuy_e_low",
        data_type=DataType.UINT16,
        name="Total Grid Buy Energy - low word",
        entity_category=DIAGNOSTIC,
    )
    # END ------------------------------------------------

    GRIDFREQ = RegisterMapEntry(
        address=79,
        key="gridfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Grid Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
    )

    # NEW ------------------------------------------------
    TOTALGRIDBUY_E_HIGH_RAW = RegisterMapEntry(
        address=80,
        key="totalgridbuy_e_high",
        data_type=DataType.UINT16,
        name="Total Grid Buy Energy - high word",
        entity_category=DIAGNOSTIC,
    )

    TOTALGRIDSELL_E = RegisterMapEntry(
        address=81,
        key="totalsell_e",
        data_type=DataType.UINT32,
        scale=0.1,
        name="Total Grid Sell Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    # END ------------------------------------------------

    DAILYLOAD_E = RegisterMapEntry(
        address=84,
        key="dailyload_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily Load Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    TOTALLOAD_E = RegisterMapEntry(
        address=85,
        key="totalload_e",
        data_type=DataType.UINT32,
        scale=0.1,
        name="Total Load Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
    )
    DCHSTempC = RegisterMapEntry(
        address=90,
        key="dchstempc",
        data_type=DataType.UINT16,
        scale=0.1,
        offset=1000,
        name="DC Heatsink Temperature",
        native_unit_of_measurement=NativeUnit.CELSIUS,
        device_class=DeviceClass.TEMPERATURE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    ACHSTempC = RegisterMapEntry(
        address=91,
        key="achstempc",
        data_type=DataType.UINT16,
        scale=0.1,
        offset=1000,
        name="AC Heatsink Temperature",
        native_unit_of_measurement=NativeUnit.CELSIUS,
        device_class=DeviceClass.TEMPERATURE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TOTALINV_E = RegisterMapEntry(
        address=96,
        key="totalinv_e",
        data_type=DataType.INT64,
        scale=0.1,
        name="Total PV Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    FAULT_INFO_RAW = RegisterMapEntry(
        address=103,
        key="fault_info_raw",
        data_type=DataType.UINT64,
        name="Inverter Fault Information Raw Value",
        icon="mdi:message-alert-outline",
        entity_category=DIAGNOSTIC,
    )
    CORR_BATT_CAP = RegisterMapEntry(
        address=107,
        key="corr_batt_cap",
        data_type=DataType.UINT16,
        name="Corrected Battery Capacity",
        icon="mdi:battery",
        native_unit_of_measurement=NativeUnit.AH,
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
    )
    DAILYPV_E = RegisterMapEntry(
        address=108,
        key="dailypv_e",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Daily PV Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL_INCREASING,
    )
    PV1_V = RegisterMapEntry(
        address=109,
        key="pv1_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV1 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV1_C = RegisterMapEntry(
        address=110,
        key="pv1_c",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV1 Current",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV2_V = RegisterMapEntry(
        address=111,
        key="pv2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV2_C = RegisterMapEntry(
        address=112,
        key="pv2_c",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV2 Current",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV3_V = RegisterMapEntry(
        address=113,
        key="pv3_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV3 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV3_C = RegisterMapEntry(
        address=114,
        key="pv3_c",
        data_type=DataType.UINT16,
        scale=0.1,
        name="PV3 Current",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    # # NEW ---------------- NOT VERIFIED - Looks bad --------------------------------
    # GRID_CHARGE_CURRENT = RegisterMapEntry(
    #     address=128,
    #     key="grid_charge_current",
    #     data_type=DataType.UINT16,
    #     name="Grid Charge Current",
    #     icon="mdi:current-dc",
    #     native_unit_of_measurement=NativeUnit.A,
    #     device_class=DeviceClass.CURRENT,
    #     state_class=StateClass.MEASUREMENT,
    #     entity_registry_enabled_default=False,
    # )
    # GEN_CHARGE_ENABLE = RegisterMapEntry(
    #     address=129,
    #     key="gen_charge_enable",
    #     data_type=DataType.UINT16,
    #     name="Generator Charge Enable",
    #     icon="mdi:engine",
    #     state_class=StateClass.NONE,
    #     entity_registry_enabled_default=False,
    # )
    # GRID_CHARGE_ENABLE = RegisterMapEntry(
    #     address=130,
    #     key="grid_charge_enable",
    #     data_type=DataType.UINT16,
    #     name="Grid Charge Enable",
    #     icon="mdi:transmission-tower-export",
    #     state_class=StateClass.NONE,
    #     entity_registry_enabled_default=False,
    # )
    # # END ------------------------------------------------

    GRIDL1N_V = RegisterMapEntry(
        address=150,
        key="gridl1n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid L1-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL2N_V = RegisterMapEntry(
        address=151,
        key="gridl2n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid L2-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL1L2_V = RegisterMapEntry(
        address=152,
        key="gridl1l2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid L1-L2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDRELAY_V = RegisterMapEntry(
        address=153,
        key="gridrelay_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Grid Relay Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1N_V = RegisterMapEntry(
        address=154,
        key="invl1n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Inverter L1-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL2N_V = RegisterMapEntry(
        address=155,
        key="invl2n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Inverter L2-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1L2_V = RegisterMapEntry(
        address=156,
        key="invl1l2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Inverter L1-L2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
    )
    LOADL1N_V = RegisterMapEntry(
        address=157,
        key="loadl1n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Load L1-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOADL2N_V = RegisterMapEntry(
        address=158,
        key="loadl2n_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Load L2-N Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL1_C = RegisterMapEntry(
        address=160,
        key="gridl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Grid L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL2_C = RegisterMapEntry(
        address=161,
        key="gridl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Grid L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    EXTLMTL1_C = RegisterMapEntry(
        address=162,
        key="extlmtl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="External Lmt L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    EXTLMTL2_C = RegisterMapEntry(
        address=163,
        key="extlmtl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="External Lmt L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1_C = RegisterMapEntry(
        address=164,
        key="invl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Inverter L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL2_C = RegisterMapEntry(
        address=165,
        key="invl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Inverter L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GEN_P = RegisterMapEntry(
        address=166,
        key="gen_p",
        data_type=DataType.INT16,
        name="Gen Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    GRIDL1_P = RegisterMapEntry(
        address=167,
        key="gridl1_p",
        data_type=DataType.INT16,
        name="Grid L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDL2_P = RegisterMapEntry(
        address=168,
        key="gridl2_p",
        data_type=DataType.INT16,
        name="Grid L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRID_P = RegisterMapEntry(
        address=169,
        key="grid_p",
        data_type=DataType.INT16,
        name="Total Grid Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    GRIDLMTL1_P = RegisterMapEntry(
        address=170,
        key="gridlmtl1_p",
        data_type=DataType.INT16,
        name="Grid Limiter L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDLMTL2_P = RegisterMapEntry(
        address=171,
        key="gridlmtl2_p",
        data_type=DataType.INT16,
        name="Grid Limiter L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRIDEXT_P = RegisterMapEntry(
        address=172,
        key="gridext_p",
        data_type=DataType.INT16,
        name="Grid External Total Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVL1_P = RegisterMapEntry(
        address=173,
        key="invl1_p",
        data_type=DataType.INT16,
        name="Inverter L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    INVL2_P = RegisterMapEntry(
        address=174,
        key="invl2_p",
        data_type=DataType.INT16,
        name="Inverter L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    INV_P = RegisterMapEntry(
        address=175,
        key="inv_p",
        data_type=DataType.INT16,
        name="Inverter Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    LOADL1_P = RegisterMapEntry(
        address=176,
        key="loadl1_p",
        data_type=DataType.INT16,
        name="Load L1 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOADL2_P = RegisterMapEntry(
        address=177,
        key="loadl2_p",
        data_type=DataType.INT16,
        name="Load L2 Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOAD_P = RegisterMapEntry(
        address=178,
        key="load_p",
        data_type=DataType.INT16,
        name="Load Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    LOADL1_C = RegisterMapEntry(
        address=179,
        key="loadl1_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Load L1 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    LOADL2_C = RegisterMapEntry(
        address=180,
        key="loadl2_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Load L2 Current",
        icon="mdi:current-ac",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GENL1L2_V = RegisterMapEntry(
        address=181,
        key="genl1l2_v",
        data_type=DataType.UINT16,
        scale=0.1,
        name="Generator L1-L2 Voltage",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BATTTEMP_C = RegisterMapEntry(
        address=182,
        key="batttempc",
        data_type=DataType.UINT16,
        scale=0.1,
        offset=1000,
        name="Battery Temperature",
        native_unit_of_measurement=NativeUnit.CELSIUS,
        device_class=DeviceClass.TEMPERATURE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BATT_V = RegisterMapEntry(
        address=183,
        key="batt_v",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Battery Voltage",
        icon="mdi:battery",
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
    )
    BATT_SOC = RegisterMapEntry(
        address=184,
        key="batt_soc",
        data_type=DataType.UINT16,
        name="Battery State of Charge",
        icon="mdi:battery-50",
        native_unit_of_measurement=NativeUnit.PERCENT,
        device_class=DeviceClass.BATTERY,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    PV1_P = RegisterMapEntry(
        address=186,
        key="pv1_p",
        data_type=DataType.UINT16,
        name="PV1 Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    PV2_P = RegisterMapEntry(
        address=187,
        key="pv2_p",
        data_type=DataType.UINT16,
        name="PV2 Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    PV3_P = RegisterMapEntry(
        address=188,
        key="pv3_p",
        data_type=DataType.UINT16,
        name="PV3 Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    BATT_P = RegisterMapEntry(
        address=190,
        key="batt_p",
        data_type=DataType.INT16,
        name="Battery Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
    )
    BATT_C = RegisterMapEntry(
        address=191,
        key="batt_c",
        data_type=DataType.INT16,
        scale=0.01,
        name="Battery Current",
        icon="mdi:current-dc",
        native_unit_of_measurement=NativeUnit.A,
        device_class=DeviceClass.CURRENT,
        state_class=StateClass.MEASUREMENT,
    )
    LOAD_FREQ = RegisterMapEntry(
        address=192,
        key="loadfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Load Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    INVERTER_FREQ = RegisterMapEntry(
        address=193,
        key="inverterfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Inverter Output Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    GRID_RLY_RAW = RegisterMapEntry(
        address=194,
        key="grid_rly_raw",
        data_type=DataType.INT16,
        name="Grid Relay Raw Value",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        entity_category=DIAGNOSTIC,
    )
    GEN_RLY_RAW = RegisterMapEntry(
        address=195,
        key="gen_rly_raw",
        data_type=DataType.INT16,
        name="Generator Relay Raw Value",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        entity_category=DIAGNOSTIC,
    )
    GEN_FREQ = RegisterMapEntry(
        address=196,
        key="genfreq",
        data_type=DataType.UINT16,
        scale=0.01,
        name="Generator Relay Frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=NativeUnit.HZ,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    # Time of use

    TIMEOFUSE_ENABLED = RegisterMapEntry(
        address=248,
        key="timeofuse_enabled",
        data_type=DataType.UINT16,
        name="Time of Use Enabled",
        entity_registry_enabled_default=False,
    )

    TIMEOFUSE_TIME_1 = RegisterMapEntry(
        address=250,
        key="timeofuse_time_1",
        data_type=DataType.UINT16,
        name="Time of Use Time 1",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_TIME_2 = RegisterMapEntry(
        address=251,
        key="timeofuse_time_2",
        data_type=DataType.UINT16,
        name="Time of Use Time 2",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_TIME_3 = RegisterMapEntry(
        address=252,
        key="timeofuse_time_3",
        data_type=DataType.UINT16,
        name="Time of Use Time 3",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_TIME_4 = RegisterMapEntry(
        address=253,
        key="timeofuse_time_4",
        data_type=DataType.UINT16,
        name="Time of Use Time 4",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_TIME_5 = RegisterMapEntry(
        address=254,
        key="timeofuse_time_5",
        data_type=DataType.UINT16,
        name="Time of Use Time 5",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_TIME_6 = RegisterMapEntry(
        address=255,
        key="timeofuse_time_6",
        data_type=DataType.UINT16,
        name="Time of Use Time 6",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    TIMEOFUSE_POWER_1 = RegisterMapEntry(
        address=256,
        key="timeofuse_power_1",
        data_type=DataType.UINT16,
        name="Time of Use Power 1",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_POWER_2 = RegisterMapEntry(
        address=257,
        key="timeofuse_power_2",
        data_type=DataType.UINT16,
        name="Time of Use Power 2",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_POWER_3 = RegisterMapEntry(
        address=258,
        key="timeofuse_power_3",
        data_type=DataType.UINT16,
        name="Time of Use Power 3",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_POWER_4 = RegisterMapEntry(
        address=259,
        key="timeofuse_power_4",
        data_type=DataType.UINT16,
        name="Time of Use Power 4",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_POWER_5 = RegisterMapEntry(
        address=260,
        key="timeofuse_power_5",
        data_type=DataType.UINT16,
        name="Time of Use Power 5",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_POWER_6 = RegisterMapEntry(
        address=261,
        key="timeofuse_power_6",
        data_type=DataType.UINT16,
        name="Time of Use Power 6",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    TIMEOFUSE_VOLTAGE_1 = RegisterMapEntry(
        address=262,
        key="timeofuse_voltage_1",
        data_type=DataType.UINT16,
        name="Time of Use Voltage 1",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_VOLTAGE_2 = RegisterMapEntry(
        address=263,
        key="timeofuse_voltage_2",
        data_type=DataType.UINT16,
        name="Time of Use Voltage 2",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_VOLTAGE_3 = RegisterMapEntry(
        address=264,
        key="timeofuse_voltage_3",
        data_type=DataType.UINT16,
        name="Time of Use Voltage 3",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_VOLTAGE_4 = RegisterMapEntry(
        address=265,
        key="timeofuse_voltage_4",
        data_type=DataType.UINT16,
        name="Time of Use Voltage 4",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_VOLTAGE_5 = RegisterMapEntry(
        address=266,
        key="timeofuse_voltage_5",
        data_type=DataType.UINT16,
        name="Time of Use Voltage 5",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_VOLTAGE_6 = RegisterMapEntry(
        address=267,
        key="timeofuse_voltage_6",
        data_type=DataType.UINT16,
        name="Time of Use Voltage 6",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    TIMEOFUSE_SOC_1 = RegisterMapEntry(
        address=268,
        key="timeofuse_soc_1",
        data_type=DataType.UINT16,
        name="Time of Use SOC 1",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_SOC_2 = RegisterMapEntry(
        address=269,
        key="timeofuse_soc_2",
        data_type=DataType.UINT16,
        name="Time of Use SOC 2",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_SOC_3 = RegisterMapEntry(
        address=270,
        key="timeofuse_soc_3",
        data_type=DataType.UINT16,
        name="Time of Use SOC 3",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_SOC_4 = RegisterMapEntry(
        address=271,
        key="timeofuse_soc_4",
        data_type=DataType.UINT16,
        name="Time of Use SOC 4",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_SOC_5 = RegisterMapEntry(
        address=272,
        key="timeofuse_soc_5",
        data_type=DataType.UINT16,
        name="Time of Use SOC 5",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_SOC_6 = RegisterMapEntry(
        address=273,
        key="timeofuse_soc_6",
        data_type=DataType.UINT16,
        name="Time of Use SOC 6",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    TIMEOFUSE_ENABLED_1 = RegisterMapEntry(
        address=274,
        key="timeofuse_enabled_1",
        data_type=DataType.UINT16,
        name="Time of Use Enabled 1",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_ENABLED_2 = RegisterMapEntry(
        address=275,
        key="timeofuse_enabled_2",
        data_type=DataType.UINT16,
        name="Time of Use Enabled 2",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_ENABLED_3 = RegisterMapEntry(
        address=276,
        key="timeofuse_enabled_3",
        data_type=DataType.UINT16,
        name="Time of Use Enabled 3",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_ENABLED_4 = RegisterMapEntry(
        address=277,
        key="timeofuse_enabled_4",
        data_type=DataType.UINT16,
        name="Time of Use Enabled 4",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_ENABLED_5 = RegisterMapEntry(
        address=278,
        key="timeofuse_enabled_5",
        data_type=DataType.UINT16,
        name="Time of Use Enabled 5",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    TIMEOFUSE_ENABLED_6 = RegisterMapEntry(
        address=279,
        key="timeofuse_enabled_6",
        data_type=DataType.UINT16,
        name="Time of Use Enabled 6",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    BMS_CHARGING_VOLTAGE = RegisterMapEntry(
        address=312,
        key="bms_charging_voltage",
        data_type=DataType.UINT16,
        name="BMS Charging Voltage",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_DISCHARGE_VOLTAGE = RegisterMapEntry(
        address=313,
        key="bms_discharge_voltage",
        data_type=DataType.UINT16,
        name="BMS Discharge Voltage",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_CHARGE_CURRENT_LIMIT = RegisterMapEntry(
        address=314,
        key="bms_charge_current_limit",
        data_type=DataType.UINT16,
        name="BMS Charge Current Limit",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_DISCHARGE_CURRENT_LIMIT = RegisterMapEntry(
        address=315,
        key="bms_discharge_current_limit",
        data_type=DataType.UINT16,
        name="BMS Discharge Current Limit",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_SOC = RegisterMapEntry(
        address=316,
        key="bms_soc",
        data_type=DataType.UINT16,
        name="BMS SOC",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_VOLTAGE = RegisterMapEntry(
        address=317,
        key="bms_voltage",
        data_type=DataType.UINT16,
        name="BMS Voltage",
        scale=0.1,
        native_unit_of_measurement=NativeUnit.V,
        device_class=DeviceClass.VOLTAGE,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_CURRENT = RegisterMapEntry(
        address=318,
        key="bms_current",
        data_type=DataType.INT16,
        name="BMS Current",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )
    BMS_TEMP = RegisterMapEntry(
        address=319,
        key="bms_temp",
        data_type=DataType.INT16,
        name="BMS Temperature",
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    )

    # ----------------------------------
    # Post process methods
    # ----------------------------------
    @staticmethod
    def value_is_injected(register_map: "SolArkRegisterMap", entry: RegisterMapEntry): # pylint: disable=W0613
        # Value is injected into the data dictionary
        return

    @staticmethod
    def fault_code_to_message(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        fault_message_list = translate_fault_code_to_messages(int(register_map.FAULT_INFO_RAW))
        entry.register_value = ", ".join(fault_message_list)

    @staticmethod
    def pv_input_power(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        entry.register_value = register_map.PV1_P + register_map.PV2_P + register_map.PV3_P

    @staticmethod
    def grid_relay_status(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        raw: int = int(register_map.GRID_RLY_RAW)
        entry.register_value = GRID_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"

    @staticmethod
    def gen_relay_status(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        raw: int = int(register_map.GEN_RLY_RAW) & 0x0F  # mask low 4 bits
        entry.register_value = GEN_RELAY_STATUS.get(int(raw), "Unknown") if raw is not None else "Unknown"

    @staticmethod
    def total_grid_buy(register_map: "SolArkRegisterMap", entry: RegisterMapEntry):
        high: int = int(register_map.TOTALGRIDBUY_E_HIGH_RAW)
        low: int = int(register_map.TOTALGRIDBUY_E_LOW_RAW)
        entry.register_value = (high << 16) | low

    # ----------------------------------
    # Post processed sensor definitions
    # ----------------------------------
    FAULTMSG = RegisterMapEntry(
        source_is_register_read=False,
        key="faultmsg",
        data_type=DataType.STRING,
        name="Inverter error Message",
        # name="Inverter Fault Message", # TODO - get concensus on changing entiity name(s) to match the SolArk documentation.
        # Caution: this is used by the hub to indicate a communication error with the device.
        # TODO - Another option is to create another entity, with the old one set to be not enabled buy default.
        icon="mdi:message-alert-outline",
        state_class=StateClass.NONE,
        post_process_method=fault_code_to_message,
    )
    PV_P = RegisterMapEntry(
        source_is_register_read=False,
        key="pv_p",
        data_type=DataType.UINT16,
        name="PV Input Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=NativeUnit.WATT,
        device_class=DeviceClass.POWER,
        state_class=StateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        post_process_method=pv_input_power,
    )
    GRID_RLY = RegisterMapEntry(
        source_is_register_read=False,
        key="grid_rly",
        data_type=DataType.INT16,
        name="Grid Relay",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        post_process_method=grid_relay_status,
    )
    GEN_RLY = RegisterMapEntry(
        source_is_register_read=False,
        key="gen_rly",
        data_type=DataType.INT16,
        name="Generator Relay",
        icon="mdi:electric-switch",
        state_class=StateClass.NONE,
        entity_registry_enabled_default=False,
        post_process_method=gen_relay_status,
        description="Indicates the status of the generator relay based on raw register values.",
    )
    TOTALGRIDBUY_E = RegisterMapEntry(
        source_is_register_read=False,
        key="totalgridbuy_e",
        data_type=DataType.INT32,
        name="Total Grid Buy Energy",
        native_unit_of_measurement=NativeUnit.KWH,
        device_class=DeviceClass.ENERGY,
        state_class=StateClass.TOTAL,
        entity_registry_enabled_default=False,
        post_process_method=total_grid_buy,
    )

    UPDATE_COUNTER = RegisterMapEntry(
        source_is_register_read=False,
        key="update_cnt",
        data_type=DataType.INT16,
        name="Update Counter",
        icon="mdi:information-outline",
        state_class=StateClass.TOTAL,
        post_process_method=value_is_injected,
    )

    CONFIG_INFO = RegisterMapEntry(
        source_is_register_read=False,
        key="config_info",
        data_type=DataType.STRING,
        name="Configuration",
        icon="mdi:information-outline",
        entity_category = EntityCategory.DIAGNOSTIC,
        state_class=StateClass.NONE,
        post_process_method=value_is_injected,
        sensor_class = SensorClass.CONFIG,
    )
    # TODO - add performance metrics for the register reads.
    # TODO - add fault list sensor
