import uds_server, window_handler

class ProjectManager:

    def __init__(self):
        pass

    def start(self):
        socket_path = '/tmp/dmicade_socket.s'
        server = uds_server.UdsServer(socket_path)

        #win_handler = window_handler.WindowHandler()
        #win_handler.start()


if __name__ == '__main__':
    pm = ProjectManager()
    pm.start()