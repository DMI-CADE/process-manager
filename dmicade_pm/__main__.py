import sys
import threading
import logging

from .helper import parse_command_line_arguments
from .processmanager import DmicProcessManager
from .statemachine import DmicStateMachine
from .tasks import DmicTask
from .commands import DmicCommandPool
from .uds_server import UdsServer
from .message_parser import DmicMessageParser
from .config_loader import DmicConfigLoader


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

logging.basicConfig(level=numeric_log_level,
                    format='%(asctime)s - (%(threadName)-9s) %(levelname)s:%(name)s:%(filename)s: %(message)s',)


def main():
    print(__import__('os').getcwd())
    parsed_args = parse_command_line_arguments(sys.argv)
    client = Client(parsed_args)

    debug_mode = 'debug' in parsed_args
    client.start(debug_mode)


class Client:
    SOCKET_PATH = '/tmp/dmicade_socket.s'

    def __init__(self, user_args):
        self._config_loader = DmicConfigLoader(user_args)
        self._uds_server = UdsServer(self.SOCKET_PATH)
        self._message_parser = DmicMessageParser(self._uds_server)
        self._process_manager = DmicProcessManager(self, self._uds_server, self._config_loader)
        self._command_pool = DmicCommandPool(self._process_manager)
        self._state_machine = DmicStateMachine(self._command_pool)

        self._message_parser.received_task_event += self.queue_state_task

    def start(self, debug_mode=False):
        logging.debug('[PM CLIENT] Start')

        self._uds_server.connected_event += lambda x: logging.info('[PM CLIENT] UDS server connected!')
        self._uds_server.disconnected_event += lambda x: logging.warning('[PM CLIENT] UDS server disconnected!')

        self._uds_server.start()

        if debug_mode:
            logging.info('[PM CLIENT] Running in Debug mode...')
            t = threading.Thread(target=self._debug, daemon=True)
            t.name = 'DebugThread'
            t.start()

        self._state_machine.run_event_loop_sync()

        logging.debug('[PM CLIENT] Close uds server...')
        self._uds_server.close()
        logging.debug('[PM CLIENT] Done...')

    def queue_state_task(self, task: DmicTask):
        self._state_machine.queue_task_for_state(task)

    def _debug(self):

        input_str = ''

        while input_str != 'exit':
            input_str = input()
            self._message_parser.parse_uds_message(input_str)

        self._state_machine.stop_event_loop()


main()
