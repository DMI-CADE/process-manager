import logging
import sys
import os
import datetime
import re

from .helper import ccolors


class DmicLogging():

    FILE_NAME_FORMAT = "DMIC-PM-%s.log"
    FORMAT = '%(asctime)s - (%(threadName)-12.12s) %(levelname)-7.7s: %(filename)-25s: %(message)s'

    def __init__(self, user_args):
        self._no_file_log = 'nofilelog' in user_args

        self.log_folder = './logs'
        if 'logs' in user_args:
            self.log_folder = user_args['logs']


    def setup(self):
        """Sets up logging to console and file."""

        try:
            os.mkdir(self.log_folder)
            print('Created log folder: ', os.path.abspath(self.log_folder))
        except FileExistsError:
            print('Logging to: ', os.path.abspath(self.log_folder))

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

        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_log_level)

        log_formatter = logging.Formatter(self.FORMAT)
        console_log_formatter = DmicConsoleFormatter(self.FORMAT)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_log_formatter)
        root_logger.addHandler(console_handler)

        if self._no_file_log:
            return

        current_datetime_suffix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file_path = os.path.join(self.log_folder, self.FILE_NAME_FORMAT % current_datetime_suffix)
        logging.info(f'[LOGGING MANAGER]: log to: {log_file_path}')

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)


class DmicConsoleFormatter(logging.Formatter):

    def __init__(self, fmt="%(levelname)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

        lvl_name_sub = re.search(r'%\(levelname\)[^s]*s', self._fmt)[0]
        self.info_fmt = fmt.replace(lvl_name_sub, ccolors.OKCYAN + lvl_name_sub + ccolors.ENDC)
        self.debug_fmt = fmt.replace(lvl_name_sub, ccolors.OKBLUE + lvl_name_sub + ccolors.ENDC)
        self.warning_fmt = fmt.replace(lvl_name_sub, ccolors.FAIL + lvl_name_sub + ccolors.ENDC)


    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        original_format = self._fmt

        if record.levelno == logging.DEBUG:
            self._fmt = self.debug_fmt

        elif record.levelno == logging.INFO:
            self._fmt = self.info_fmt

        elif record.levelno == logging.ERROR or record.levelno == logging.WARNING:
            self._fmt = self.warning_fmt

        logging.Formatter.__init__(self, self._fmt)
        result = logging.Formatter.format(self, record)

        scoped_match = re.match('^\[(?P<scope>[^\]]+)\]', record.getMessage())
        if scoped_match:
            scope = scoped_match.groupdict()['scope']
            result = result.replace(scope, ccolors.OKGREEN + scope + ccolors.ENDC)

        # Restore the original format configured by the user
        self._fmt = original_format

        return result
