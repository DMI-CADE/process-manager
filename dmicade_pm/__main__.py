import sys
import threading
import logging

from .helper import parse_command_line_arguments
from .processmanager import DmicProcessManager
from .statemachine import DmicStateMachine
from .tasks import DmicTaskType, DmicTask
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
    client.start()


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

    def start(self):
        print('[PM CLIENT] Start')

        #self._uds_server.connected_event += lambda x: print('[Client] udsServer: Connected!')
        #self._uds_server.received_event += lambda msg: print('[Client] udsServer: Received: ', msg)
        #self._uds_server.disconnected_event += lambda x: print('[Client] udsServer: Disconnected...')

        self._uds_server.start()

        #while not self._uds_server.is_connected():
            #pass

        # self._process_manager._timer.alert_event += lambda x: print('--------- jeff')
        # self._process_manager._timer.set_timer(3)
        # input('...\n')
        # self._process_manager._timer.reset()
        #input('...\n')
        #self._uds_server.close()
        #return

        t = threading.Thread(target=self._debug, daemon=True)
        t.name = 'debug_thread'
        # t.start()

        # self._state_machine.queue_task_for_state(DmicTask(DmicTaskType.TEST, ':)'))
        self._state_machine.run_event_loop_sync()

        self._uds_server.close()

    def queue_state_task(self, task: DmicTask):
        self._state_machine.queue_task_for_state(task)

    def _debug(self):

        app_name = 'alien-soldier'
        input('...\n')
        self._state_machine.queue_task_for_state(DmicTask(DmicTaskType.START_APP, app_name))
        input('...\n')
        self._state_machine.queue_task_for_state(DmicTask(DmicTaskType.CLOSE_APP, app_name))
        input('...\n')
        self._state_machine.stop_event_loop()

        return

        user_input = ''
        states = ['start', 'test']
        state = 0

        def check_input(x):
            return user_input[:len(x)] == x

        while not check_input('exit'):
            user_input = input()
            if check_input('test'):
                self.queue_state_task(DmicTask(DmicTaskType.TEST, user_input))
            elif check_input('t3'):
                self.queue_state_task(DmicTask(DmicTaskType.TEST, '1'))
                self.queue_state_task(DmicTask(DmicTaskType.TEST, '2'))
                self.queue_state_task(DmicTask(DmicTaskType.TEST, '3'))
                self.queue_state_task(DmicTask(DmicTaskType.CHANGE_STATE, 'start'))
            elif check_input('swst'):
                state = (state + 1) % len(states)
                self.queue_state_task(DmicTask(DmicTaskType.CHANGE_STATE, states[state]))

        self._state_machine.stop_event_loop()


main()
