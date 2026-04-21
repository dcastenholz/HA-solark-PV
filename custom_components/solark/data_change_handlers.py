from .data import SolArkData
from .device_info import SolArkDeviceInfo


class DatChangeHandlers():
    _runtime_data: SolArkData
    _serial_number: str = ""

    def __init__(self, runtime_data: SolArkData):
        self._runtime_data = runtime_data

    # def SN_change_handler(self, new_serial_number, old_serial_number):
    #     if new_serial_number == self._serial_number:
    #         return

    def SN_change_handler(self, new_serial_number):
        '''Save the serial number to the device info serial number property'''
        if new_serial_number == self._serial_number:
            return

        SolArkDeviceInfo.set_serial_number(self._runtime_data, new_serial_number)
        self._serial_number = new_serial_number
