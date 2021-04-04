from helper import DmicEvent
import socket, threading
import os, os.path

class UdsServer:
    """Unix Domain Socket Server for dmicade process manager."""

    CLIENT_TIMEOUT = 0.5

    def __init__(self, socket_path):
        self.connected_event = DmicEvent()
        self.received_event = DmicEvent()
        self.disconnected_event = DmicEvent()

        self._connected = False

        self._socket_path = socket_path
        self._server_socket = None
        self._client_conn = None

        self._receive_thread = None
        self._connect_thread = None

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists(self._socket_path):
            os.remove(self._socket_path)
        self._server_socket.bind(self._socket_path)

        # Start receive when connected.
        self._receive_thread = threading.Thread(target=self._receive_continuous)
        self.connected_event += lambda arg: self._receive_thread.start()

    def start(self):
        self._connect_thread = threading.Thread(target=self._connect)
        self._connect_thread.start()

    def close(self):
        if self.is_connected():
            try:
                self._client_conn.shutdown(socket.SHUT_WR)
                self._client_conn.close()
            except:
                #print('[UDS SERVER] Shutdown failed.')
                pass

            self._connected = False

    def _connect(self):
        #print('[UDS SERVER] Waiting for connection...')
        self._server_socket.listen(1)
        self._client_conn, addr = self._server_socket.accept()
        self._client_conn.settimeout(self.CLIENT_TIMEOUT)

        self._connected = True
        self.connected_event.update()

    def send(self, message):
        if self.is_connected():
            bytes_sent = self._client_conn.send(message.encode('ascii'))
            #print('[UDS SERVER] bytesSent:', bytes_sent)

    def _receive_continuous(self):
        #print('[UDS SERVER] Start continuous receive...')
        while self.is_connected():
            #print('[UDS SERVER] Receive...')
            try:
                rec_msg = self._client_conn.recv(1024)
                msg = rec_msg.decode('ascii')
                if len(msg) == 0:
                    print('[UDS SERVER] Connection closed by remote host.')
                    self.close()
                    break

                print('[UDS SERVER] Received:', msg)
                self.received_event.update(msg)
            except socket.timeout:
                #print('[UDS SERVER] receive timeout...')
                continue
            except socket.error as e:
                print('[UDS SERVER] receive exception raised:')
                print(e)
                self.close()
                
        #print('[UDS SERVER] Continuous receive stopped.')

    def is_connected(self):
        return self._connected
