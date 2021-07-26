import os
import os.path
import socket
import threading
import warnings
import logging

from time import sleep
from .helper import DmicEvent


class UdsServer:
    """Unix Domain Socket Server for dmicade process manager.

    Will disable core functionalities on Windows.

    Attributes:
      connected_event : DmicEvent
        Event handler that is raised when the server successfully
        connects to a client.
      received_event : DmicEvent
        Event handler that is raised when the server receives a message
        from the client when connected.
      disconnected_event : DmicEvent
        Event handler that is raised when the server gets disconnected
        from the client.
    """

    """Client timeout time used as interval for checking for received
    messages."""
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

        if os.name == 'nt':
            warnings.warn('Uds socket functionalities are is disabled on Windows.')
            return

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists(self._socket_path):
            logging.debug('[UDS SERVER] Deleting old socket file...')
            os.remove(self._socket_path)
        self._server_socket.bind(self._socket_path)

        # Start receive when connected.
        self._receive_thread = threading.Thread(target=self._receive_continuous)
        self._receive_thread.name = 'receive_thread'
        self.connected_event += lambda arg: self._receive_thread.start()

    def start(self):
        """Starts the server in its separate thread.

        At first it starts listening for a connection on a separate
        thread.
        If a client connected the receive thread is started and raises
        the 'received_event' when a message from the client is received.
        Will do nothing on Windows.
        """

        if os.name == 'nt':
            warnings.warn('Uds socket functionalities are is disabled on Windows.')

        else:
            self._connect_thread = threading.Thread(target=self._connect, daemon=True)
            self._connect_thread.start()

    def close(self):
        """Disconnects the server socket and stops its threads.

        Only tries to close the connection if the server is currently
        connected.
        """

        if self.is_connected():
            try:
                self._client_conn.shutdown(socket.SHUT_WR)
                self._client_conn.close()
            except socket.error:
                logging.debug('[UDS SERVER] Shutdown failed.')
                pass

            self._connected = False

    def send(self, message, return_zero_on_windows=False):
        """Sends a message to the connected client.

        Args:
          message: str
            The message to send to the client.
          return_zero_on_windows: bool
            If true message always returns 0 when run on windows.

        Returns:
          The amount of bytes sent to the client.
        """

        bytes_sent = 0

        if os.name == 'nt':
            if not return_zero_on_windows:
                bytes_sent = len(message)
            warnings.warn(f'UDS Server will not send msg on windows. Returning: {bytes_sent}')

        elif self.is_connected():
            bytes_sent = self._client_conn.send(message.encode('ascii'))

        sleep(0.05) # Simple fix to avoid messages getting munched together when send in quick succession...

        return bytes_sent

    def _connect(self):
        """Synchronously listens for a client to connect."""

        self._server_socket.listen(1)
        self._client_conn, addr = self._server_socket.accept()
        self._client_conn.settimeout(self.CLIENT_TIMEOUT)

        self._connected = True
        self.connected_event.update()

    def _receive_continuous(self):
        """Synchronously checks for received messages from the client.

        Checks for a new message every time the recv times out.
        Updates the received event when message was received.
        Closes the connection when a socket error occurs or a message
        length of 0 is received.
        """

        while self.is_connected():
            try:
                rec_msg = self._client_conn.recv(1024)
                msg = rec_msg.decode('ascii')

                # Close server when msg length of 0 is received indication a closed connection.
                if len(msg) == 0:
                    logging.info('[UDS SERVER] Connection closed by remote host.')
                    self.close()
                    break

                logging.debug(f'[UDS SERVER] Received: {msg=}')
                self.received_event.update(msg)

            except socket.timeout:
                continue
            except socket.error as e:
                logging.exception(f'[UDS SERVER] receive exception raised: {e}')
                self.close()

    def is_connected(self):
        """Checks if server is connected to a client.

        Returns:
          True if server is currently connected to a client.
        """

        return self._connected
