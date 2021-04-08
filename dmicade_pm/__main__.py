from .processmanager import DmicProcessManager
from .statemachine import DmicStateMachine, DmicTaskType, DmicTask
from .commands import DmicCommandPool
from .uds_server import UdsServer
import threading


def main():
    client = Client()
    client.start()


class Client:
    SOCKET_PATH = '/tmp/dmicade_socket.s'

    def __init__(self):
        self._process_manager = DmicProcessManager(self)
        self._command_pool = DmicCommandPool(self._process_manager)
        self._state_machine = DmicStateMachine(self._command_pool)
        self._uds_server = UdsServer(self.SOCKET_PATH)

    def start(self):
        print('[PM CLIENT] Start')

        t = threading.Thread(target=self._debug_input, daemon=True)
        t.start()

        self._state_machine.queue_task_for_state(DmicTask(DmicTaskType.TEST, ':)'))
        self._state_machine.run_event_loop_sync()

    def queue_state_task(self, task: DmicTask):
        self._state_machine.queue_task_for_state(task)

    def _debug_input(self):
        user_input = ''
        states = ['start', 'test']
        state = 0

        check_input = lambda x: user_input[:len(x)] == x

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
