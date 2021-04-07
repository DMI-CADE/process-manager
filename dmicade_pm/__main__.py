from .statemachine import DmicStateMachine, DmicTaskType
from .uds_server import UdsServer
import threading


def main():
    client = Client()
    client.start()


class Client:
    SOCKET_PATH = '/tmp/dmicade_socket.s'

    def __init__(self):
        self._command_pool = None
        self._state_machine = DmicStateMachine(None)
        self._uds_server = UdsServer(self.SOCKET_PATH)

    def start(self):
        print('[PM CLIENT] Start')

        t = threading.Thread(target=self._debug_input)
        t.start()

        self._state_machine.queue_task_for_state({'type': DmicTaskType.TEST, 'data': ':)'})
        self._state_machine.run_event_loop_sync()

    def _debug_input(self):
        user_input = ''
        states = ['start', 'test']
        state = 0

        check_input = lambda x: user_input[:len(x)] == x

        while not check_input('exit'):
            user_input = input()
            if check_input('test'):
                self._state_machine.queue_task_for_state({'type': DmicTaskType.TEST, 'data': user_input})
            elif check_input('swst'):
                state = (state + 1) % len(states)
                self._state_machine.queue_task_for_state({'type': DmicTaskType.CHANGE_STATE, 'data': states[state]})

        self._state_machine.stop_event_loop()

main()
