from .uds_server import UdsServer
from .statemachine import DmicStateMachine

def main():
    client = Client()
    client.start()

class Client:

    SOCKET_PATH = '/tmp/dmicade_socket.s'

    def __init__(self):
        self._state_machine = DmicStateMachine()
        self._uds_server = UdsServer(self.SOCKET_PATH)

    def start(self):
        print('[PM CLIENT] Start')

        input()

main()
