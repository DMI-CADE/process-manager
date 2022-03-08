import logging
import sys
import os
import datetime


class DmicLogging():

    FILE_NAME_FORMAT = "DMIC-PM-%s.log"
    FORMAT = '%(asctime)s - (%(threadName)-12.12s) %(levelname)-7.7s: %(filename)-25s: %(message)s'

    def __init__(self, user_args):
        self.log_folder = './logs'
        if 'logs' in user_args:
            self.log_folder = user_args['logs']


        self.logFormatter = logging.Formatter(self.FORMAT)

    def setup(self):

        # Set default loglevel.
        numeric_log_level = getattr(logging, 'INFO', None)

        # Handle command line arguments.
        for arg in sys.argv:

            # Set log level.
            if arg.find('--log=') == 0:
                loglevel = arg[6:]
                numeric_log_level = getattr(logging, loglevel.upper(), None)
                if not isinstance(numeric_log_level, int):
                    raise ValueError('Invalid log level: %s' % loglevel)

        rootLogger = logging.getLogger()
        rootLogger.setLevel(numeric_log_level)

        current_datetime_suffix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file_path = os.path.join(self.log_folder, self.FILE_NAME_FORMAT % current_datetime_suffix)
        print(log_file_path)

        fileHandler = logging.FileHandler(log_file_path)
        fileHandler.setFormatter(self.logFormatter)
        fileHandler.setLevel(logging.INFO)
        rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(self.logFormatter)
        rootLogger.addHandler(consoleHandler)