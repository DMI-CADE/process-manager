import socket
import os, os.path

class UdsServer:
    """Unix Domain Socket Server for dmicade process manager."""

    _server_socket = None
    _socket_path = ""
    _client_conn = None

    def __init__(self, socket_path):
        self._socket_path = socket_path

    def start(self):
        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        if os.path.exists(self._socket_path):
            os.remove(self._socket_path)

        self._server_socket.bind(self._socket_path)

        self._server_socket.listen(1)
        self._client_conn, addr = self._server_socket.accept()

    def send(self, message):
        bytes_sent = self._client_conn.send(message.encode('ascii'))
        print('bytesSent:', bytes_sent)

    def disconnect(self):
        pass

    def _connect(self):
        pass

    def _receive_msg(self):
        print('Receiving Msg...')
        rec_msg = self._client_conn.recv(1024)
        print('[Received Message]', rec_msg.decode('ascii'))

    def _is_connected(self):
        return _client_conn != None


#serversocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#
#socketPath = '/tmp/dmicade_socket.s'
#
#if os.path.exists(socketPath):
#    os.remove(socketPath)
#
#print('Bind:', socketPath)
#serversocket.bind(socketPath)
#
#print('Listening for connection...')
#serversocket.listen(1)
#
#while True:
#    clientsocket, addr = serversocket.accept()
#
#    print('Connected: ', str(addr), str(clientsocket))
#
#    print('Receiving Msg...')
#    recMsg = clientsocket.recv(1024)
#    print('[Received Message]', recMsg.decode('ascii'))
#
#    msg = ''
#    while msg != 'exit':
#        print(msg != 'exit')
#        msg = input("Send: ")
#        bytesSent = clientsocket.send(msg.encode('ascii'))
#        print("bytesSent:", bytesSent)
#
#    clientsocket.close()
#    break
