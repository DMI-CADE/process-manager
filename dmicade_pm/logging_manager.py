import logging
import sys

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

FORMAT = '%(asctime)s - (%(threadName)-12.12s) %(levelname)-7.7s: %(filename)-25s: %(message)s'

#logging.basicConfig(level=numeric_log_level)

logFormatter = logging.Formatter(FORMAT)
rootLogger = logging.getLogger()
rootLogger.setLevel(numeric_log_level)

fileHandler = logging.FileHandler("./logs/example.log")
#fileHandler.setLevel(numeric_log_level)
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.INFO)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
#consoleHandler.setLevel(numeric_log_level)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)