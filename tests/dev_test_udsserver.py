def test_udsserver():
    print('[Client] Connecting to unix domain socket')
    server = UdsServer(self.SOCKET_PATH)

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