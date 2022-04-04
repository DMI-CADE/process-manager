import logging
import threading
import time
import datetime

from .serial_connection import *

class DmicTemperatureLogging():

    def __init__(self, global_conf):
        self.is_running = True

        self._port = 'NO_TEMP_PORT_SET'
        if 'temp_port' in global_conf:
            self._port = global_conf['temp_port']

        self.serial_connector = None # Init in thread to not block main pm.

        # Setup Logging
        self.logger = logging.getLogger('temp_logger') # First call creates new logger.
        self.logger.propagate = False # Do not pass logs to handlers of higher level (only own file handler).

        # Setup Temp Log Thread
        self.t = threading.Thread(target=self.temp_log_loop, daemon=True)
        self.t.name = 'TemperatureLoggingThread'
        self.t.start()

    def _logging_setup(self):
        log_file = "./logs/temp-log-%s.log" % datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        file_handler = logging.FileHandler(log_file) # Create handler.
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(file_handler)

    def temp_log_loop(self):

        self.serial_connector = DmicSerialConnector(self._port)

        if not self.serial_connector._connection:
            logging.warning('[TEMPERATURE LOGGING] Could not connect..')
            return

        logging.info(f'[TEMPERATURE LOGGING] Connected! port={self._port}')
        self._logging_setup()
        self.logger.info('Start Temperature Logging...')
        
        initial_msg = self.serial_connector.read_data()
        logging.info(f'[TEMPERATURE LOGGING] {initial_msg=}')
        self.logger.info('Initial Msg: ' + str(initial_msg))
        
        while self.is_running:
            msg = self.serial_connector.read_data()
            if len(msg) > 0:
                self.logger.info(msg)

            time.sleep(5)

    def stop(self):
        self.is_running = False
        time.sleep(6)
        self.logger.handlers.clear()
