import logging
import serial
import time


class DmicSerialConnector():
    """Interface for communicating with connected serial device."""

    def __init__(self, port):
        self._connection = None

        try:
            self._connection = serial.Serial(port=port, baudrate=9600, timeout=.1)
            time.sleep(3)
        except serial.SerialException as se:
            logging.warning(se)

    def write_data(self, data_str):
        if self._connection:
            self._connection.write(bytes(data_str, 'utf-8'))

        time.sleep(0.05)
        
    def read_data(self):
        return self._connection.readline()
