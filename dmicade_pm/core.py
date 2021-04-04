from helper import DmicEvent
import uds_server, window_handler

class Client:

    SOCKET_PATH = '/tmp/dmicade_socket.s'

    def __init__(self):
        pass

    def start(self):
        print('[Client] Connecting to unix domain socket')
        server = uds_server.UdsServer(self.SOCKET_PATH)

        server.connected_event += lambda x: print('[Client] udsServer: Connected!')
        server.received_event += lambda msg: print('[Client] udsServer: Received: ', msg)
        server.disconnected_event += lambda x: print('[Client] udsServer: Disconnected...')

        server.start()

        while not server.is_connected():
            pass

        # Test
        msg = ''
        while msg != 'exit' and server.is_connected():
            print('Send: ')
            msg = input()
            server.send(msg)

        server.close()

        #win_handler = window_handler.WindowHandler()
        #win_handler.start()


if __name__ == '__main__':
    client = Client()
    client.start()