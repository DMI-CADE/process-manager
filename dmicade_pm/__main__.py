import sys
import threading
import logging

from .helper import parse_command_line_arguments
from .processmanager import DmicProcessManager
from .statemachine import DmicStateMachine
from .tasks import DmicTask
from .commands import commands_set_pm
from .uds_server import UdsServer
from .message_parser import DmicMessageParser
from .config_loader import DmicConfigLoader
from .logging_manager import DmicLogging

def main():
    print(__import__('os').getcwd())
    parsed_args = parse_command_line_arguments(sys.argv)
    logger = DmicLogging(parsed_args)
    logger.setup()
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
        commands_set_pm(self._process_manager)
        self._state_machine = DmicStateMachine()

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
        logging.debug('[PM CLIENT] Done...\n')

    def queue_state_task(self, task: DmicTask):
        self._state_machine.queue_task_for_state(task)

    def _debug(self):

        input_str = ''

        while input_str != 'exit':
            input_str = input()
            self._message_parser.parse_uds_message(input_str)

        self._state_machine.stop_event_loop()


main()


def test_udsserver():
    print('[Client] Connecting to unix domain socket')
    server = UdsServer(Client.SOCKET_PATH)

    server.connected_event += lambda x: print('[Client] udsServer: Connected!')
    server.received_event += lambda msg: print('[Client] udsServer: Received: ', msg)
    server.disconnected_event += lambda x: print('[Client] udsServer: Disconnected...')

    server.start()

    while not server.is_connected():
        pass
    print('Connected!')

    # Test
    msg = ''
    while msg != 'exit' and server.is_connected():
        print('Send: ')
        msg = input()
        server.send(msg)

    server.close()

# test_udsserver()
