from .helper import DmicEvent
import socket, threading
import os, os.path

class UdsServer:
    """Unix Domain Socket Server for dmicade process manager.

    Attributes
    ----------
    CLIENT_TIMEOUT : double
        Client timout time used as interval for checking for received
        messages.
    connected_event : DmicEvent
        Event handler that is raised when the server successfully
        connects to a client.
    received_event : DmicEvent
        Event handler that is raised when the server receives a message
        from the client when connected.
    disconnected_event : DmicEvent
        Event handler that is raised when the server gets disconnected
        from the client.

    Methods
    -------
    start()
        Starts the server in its seperate thread.
    close()
        Disconnects the server socket and stops its threads.
    send(message)
        Sends a message to the connected client.
    is_connected()
        Checks if server is connected to a client.
    """

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
        """Starts the server in its seperate thread.

        At first it starts listening for a connection on a seperate
        thread.
        If a client connected the receive thread is started and raises
        the 'received_event' when a message from the client is received.
        """

        self._connect_thread = threading.Thread(target=self._connect)
        self._connect_thread.start()

    def close(self):
        """Disconnects the server socket and stops its threads.

        Only tries to close the connection if the server is curently
        connected.
        """

        if self.is_connected():
            try:
                self._client_conn.shutdown(socket.SHUT_WR)
                self._client_conn.close()
            except:
                #print('[UDS SERVER] Shutdown failed.')
                pass

            self._connected = False

    def _connect(self):
        """Sends a message to the connected client.

        Parameters
        ----------
        message : str
            The message to send to the client.

        Retruns
        -------
        int
            The amount of bytes sent to the client.
        """

        self._server_socket.listen(1)
        self._client_conn, addr = self._server_socket.accept()
        self._client_conn.settimeout(self.CLIENT_TIMEOUT)

        self._connected = True
        self.connected_event.update()

    def send(self, message):
        bytes_sent = 0

        if self.is_connected():
            bytes_sent = self._client_conn.send(message.encode('ascii'))

        return bytes_sent

    def _receive_continuous(self):
        while self.is_connected():
            try:
                rec_msg = self._client_conn.recv(1024)
                msg = rec_msg.decode('ascii')
                # Close server when msg length of 0 is received indication a closed connection.
                if len(msg) == 0:
                    #print('[UDS SERVER] Connection closed by remote host.')
                    self.close()
                    break

                self.received_event.update(msg)
            except socket.timeout:
                continue
            except socket.error as e:
                #print('[UDS SERVER] receive exception raised:')
                #print(e)
                self.close()

    def is_connected(self):
        """Checks if server is connected to a client.

        Returns
        -------
        bool
            True if server is currently connected to a client.
        """

        return self._connected
