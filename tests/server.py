import socket
import os, os.path

serversocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

socketPath = '/tmp/dmicade_socket.s'

if os.path.exists(socketPath):
    os.remove(socketPath)

print('Bind:', socketPath)
serversocket.bind(socketPath)

print('Listening for connection...')
serversocket.listen(1)

while True:
    clientsocket, addr = serversocket.accept()

    print('Connected: ', str(addr), str(clientsocket))

    print('Receiving Msg...')
    recMsg = clientsocket.recv(1024)
    print('[Received Message]', recMsg.decode('ascii'))

    msg = ''
    while msg != 'exit':
        print(msg != 'exit')
        msg = input("Send: ")
        bytesSent = clientsocket.send(msg.encode('ascii'))
        print("bytesSent:", bytesSent)

    clientsocket.close()
    break
